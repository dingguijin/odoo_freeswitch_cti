# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-~ PPMessage.
# Guijin Ding, dingguijin@gmail.com.
# All rights reserved.
#

import aiohttp
import asyncio
import collections
import json
import logging
import time
import threading
import urllib

import odoo

from . import freeswitch_info

from .freeswitch.dialplan_node.node_factory import NodeFactory

_logger = logging.getLogger(__name__)

class FreeSwitchOutbound():
    def __init__(self, dbname):
        self.dbname = dbname
        self.freeswitch_info = None        
        self.is_stop = False

        self.server = None
        self.streams = {}
        self.dialplans = {}

        self.event_queue = collections.deque([])
        return

    async def run_loop(self):
        self.db_connection = odoo.sql_db.db_connect(self.dbname)        
        self.freeswitch_info = freeswitch_info._FREESWITCH_INFO
        await asyncio.gather(self._run_node_loop(),
                             self._run_outbound_loop())
        odoo.sql_db.close_db(self.dbname)
        return

    async def _run_node_loop(self):
        while True:
            if self.is_stop:
                break

            _event = self._get_node_event()
            if not _event:
                await asyncio.sleep(1)
                continue
            
            await self._execute_node(_event)
            await asyncio.sleep(1)
        return

    async def _run_outbound_loop(self):
        self.server = await asyncio.start_server(self._client_connected_cb,
                                                 host="0.0.0.0", port=9999,
                                                 start_serving=False)
        async with self.server:
            try:
                await self.server.serve_forever()
            except asyncio.exceptions.CancelledError as e:
                # silent close
                pass
        return

    async def _stop(self):
        self.is_stop = True
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        return

    def stop(self):
        asyncio.run(self._stop())

    async def _client_connected_cb(reader, writer):
        _logger.info("NEW 111111111111111111111111111111")
        _uuid = str(uuid.uuid())
        self.streams[_uuid] = OutboundStream(self, _uuid, reader, writer)
        await self.streams[_uuid].start_stream()
        return

    def _get_node_event(self):
        if not len(self.event_queue):
            return None
        return self.event_queue.popleft()

    def _execute_node(self, event):
        if event.get("event") == None:
            node_object = NodeFactory.build(event.get("node"))
            node_object.execute_node(event)
        else:
            next_node = self._find_next_node(event)
            if next_node:
                event.get("stream").set_current_node(next_node)
                event.update(node=next_node)
                node_object = NodeFactory.build(next_node)
                node_object.execute_node(event)
        return

    def push_node_event(self, stream, node, event=None):
        self.event_queue.append({"event": event, "stream": stream, "node": node})
        return
    
class OutboundStream():

    def __init__(self, server, _uuid, reader, writer):
        self.status = "NULL"
        self.server = server
        self.uuid = _uuid
        self.reader = reader
        self.writer = writer
        self.db_connection = server.db_connection

        self.extension_ids = ()
        self.current_dialplan = None
        self.current_node = None

        self._tmp_headers = {}
        return

    async def start_stream(self):
        self._send_esl_command("connect")
        self._send_esl_command("myevents")
        self._send_esl_command("divert_events on")
        self._send_esl_command("linger 5")
        self._send_esl_command("event plain all")

        while True:
            try:
                _timeout = 1
                _header = await asyncio.wait_for(self.reader.readline(), timeout=_timeout)
            except asyncio.TimeoutError:
                _logger.error("In [%d] seconds, no event, yield" % _timeout)

            if not _header:
                await asyncio.sleep(1)

            await self._parse_header(_header)
        return

    async def _parse_header(self, header):
        headers = self._tmp_headers
        parts = header.split(b":")
        if len(parts) == 2:
            _key = urllib.parse.unquote(parts[0].strip())
            _value = urllib.parse.unquote(parts[1].strip())
            if _key == "Content-Length" and "Content-Length" in headers:
                _key = "Content-Content-Length"
            headers[_key] = _value 

        # keep receive more headers
        if header != b"\n":
            return

        # keep receive more headers
        if self._is_meta_headers(headers):
            return
        
        # _logger.info("%s", headers)
        await self._handle_headers(headers)
        self._tmp_headers = {}
        return

    async def _handle_headers(self, headers):
        if self.status == "NULL":
            _dialplan = self._hunt_dialplan(headers)
            if not _dialplan:
                self._send_esl_hangup()
                return
            self.current_dialplan = _dialplan
            self.status = "INIT"
            return
            
        if self.status == "INIT":
            self._execute_dialplan(self.current_dialplan)
            self.status = "DIALPLAN"
            return

        if self.status == "DIALPLAN":
            self._handle_event(headers)
            return
        return

    def _send_esl_command(self, cmd):
        cmd = cmd + "\n\n"
        cmd = cmd.encode("utf-8")
        self.writer.write(cmd)
        return

    def _send_esl_execute(self, app, arg=""):
        _esl = ["sendmsg",
                "call-command: execute",
                "execute-app-name: %s" % app,
                "execute-app-arg: %s" % arg]
        _esl = "\n".join(_esl) + "\n\n"
        _esl = _esl.encode("utf-8")
        self.writer.write(_esl)
        return

    def _send_esl_hangup(self, reason = 0):
        return self._send_esl_execute("hangup", reason)

    def _hunt_dialplan(self, headers):
        _profile = "internal"
        _context = headers.get("Caller-Context") or "default"
        _dialplans = self._search_dialplans(_profile, _context)
        if not _dialplans:
            return None
        for _dialplan in _dialplans:
            if dialplan.get("id") in self.extension_ids:
                continue
            if self._match_dialplan(_dialplan, headers):
                self.extension_ids.add(_dialplan.get("id"))
                return _dialplan
        return None

    def _search_dialplans(self, profile, context):
        _extensions = []
        with self.db_connection.cursor() as cr:
            cr.execute("""
            SELECT * 
            FROM freeswitch_cti_dialplan_extension
            WHERE profile='%s' AND context='%s' AND is_active=true
            ORDER BY priority ASC
            """ % (profile, context))
            _extensions = cr.dictfetchall()
        return _extensions
    
    def _match_dialplan(self, dialplan, headers):
        _condition = dialplan.get("condition")
        if not _condition:
            return True
        _condition = _condition.strip()

        # field="destination_number", expression="^*.$"
        _pattern = "field=[\'\"](\w+)[\'\"]\sexpression=[\'\"](.*)[\'\"]"
        _pattern = re.compile(_pattern)
        _match = _pattern.match(_condition)
        if not _match:
            return False
        if len(_match.groups()) != 2:
            return False
        _pattern = re.compile(_match.group(2))
        if _pattern.match(headers.get(_match.group(1)) or ""):
            return True
        return False

    def _execute_dialplan(self, dialplan):
        _start_node = self._search_dialplan_start_node(dialplan)
        if not _start_node:
            return
        self.server.push_node_event(self, _start_node)
        self.current_node = _start_node
        return

    def _search_dialplan_start_node(self, dialplan):
        _r = None
        with self.db_connection.cursor() as cr:
            cr.execute("""
            SELECT * 
            FROM freeswitch_cti_dialplan_node
            WHERE extension_id=%d AND node_type='start'
            LIMIT 1
            """ % dialplan.get("id"))
            _r = cr.dictfetchone()
        return _r
        
    def _handle_event(self, headers):
        # convert freeswitch event to result event and push to server
        return

    def on_start_node(self):
        return
    
    def on_stop_node(self):
        # hunt dialplan again
        if self.current_dialplan.get("is_continue"):
            self.state = "NULL"
        return

    def set_current_node(self, node):
        self.current_node = node
        return

