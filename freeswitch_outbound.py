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
import re
import time
import threading
import urllib
import uuid

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
        self.stream_ids = 0
        
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
        return

    async def _run_outbound_loop(self):
        self.server = await asyncio.start_server(self._client_connected_cb,
                                                 host="localhost", port=9999,
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

    async def _client_connected_cb(self, reader, writer):
        self.streams[self.stream_ids] = OutboundStream(self, self.stream_ids, reader, writer)
        await self.streams[self.stream_ids].start_stream()
        self.stream_ids += 1
        return

    def _get_node_event(self):
        if not len(self.event_queue):
            return None
        return self.event_queue.popleft()

    async def _execute_node(self, event):
        _logger.info(">>>>>>>>>>>>>> execute_node <<<<<<<<<<<<< %s", event)

        if event.get("event") == None:
            node_object = NodeFactory.build(event)
            await node_object.execute_node(event)
        else:
            next_node = self._find_next_node(event)
            _logger.info("NEXT NODE >>>>>>>>>>>>>>>> %s" % next_node)
            if next_node:
                event.get("stream").set_current_node(next_node)
                event.update(node=next_node)
                node_object = NodeFactory.build(event)
                await node_object.execute_node(event)
        return

    def push_node_event(self, stream, node, event=None):
        self.event_queue.append({"event": event, "stream": stream, "node": node})
        return

    def _find_next_node(self, event):
        _event = event.get("event")
        _node = event.get("node")
        if not _event or not _node:
            return None
        _next_node = None
        with self.db_connection.cursor() as cr:
            cr.execute("""
            SELECT node.* 
            FROM freeswitch_cti_dialplan_node AS node LEFT JOIN 
            freeswitch_cti_dialplan_node_event as event ON
            event.next_node=node.id WHERE
            event.name='%s' AND event.node_id=%d AND event.extension_id=%d
            LIMIT 1
            """ % (_event, _node.get("id"), _node.get("extension_id")))
            _next_node = cr.dictfetchone()
        return _next_node

    def close_stream(self, _id):
        _stream = self.streams.get(_id)
        if _stream:
            del self.streams[_id]
        return

class OutboundStream():

    def __init__(self, server, _id, reader, writer):
        self.status = "NULL"
        self.server = server
        self.id = _id
        self.reader = reader
        self.writer = writer
        self.db_connection = server.db_connection

        self.extension_ids = set()
        self.current_dialplan = None
        self.current_node = None

        self._tmp_headers = {}

        self.is_closed = False

        self.is_variable_parsed = False
        self.variables = {}
        self.DP_MATCH = []
        return

    async def start_stream(self):
        self._send_esl_command("connect")
        self._send_esl_command("myevents")
        self._send_esl_command("divert_events on")
        self._send_esl_command("linger 5")
        self._send_esl_command("event plain all")

        while True:
            if self.reader.at_eof():
                await asyncio.sleep(1)

            if self.is_closed:
                break

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
        _logger.info("%s", headers)
        await self._handle_headers(headers)
        self._tmp_headers = {}
        return

    def _is_meta_headers(self, headers):
        if self.status != "DIALPLAN":
            return False
        
        if len(headers) != 2:
            return False
        if headers.get("Content-Type") != "text/event-plain":
            return False
        if not headers.get("Content-Length"):
            return False        
        return True

    async def _handle_headers(self, headers):
        self._update_stream_variable(headers)

        if self.status == "NULL":
            _dialplan = self._hunt_dialplan(headers)
            if not _dialplan:
                _logger.error("Can not hunt dialplan, close the stream")
                self._send_esl_hangup()
                await self._close_stream()
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

        _logger.info("APP -> %s" % _esl)
        self.writer.write(_esl)
        return

    def _send_esl_hangup(self, reason = 0):
        return self._send_esl_execute("hangup", reason)

    def _hunt_dialplan(self, headers):
        _id = headers.get("variable_dialplan_extension_id")
        if not _id:
            _logger.error("No dialplan id variable")
            return None
        _extension = None
        with self.db_connection.cursor() as cr:
            cr.execute("""
            SELECT * 
            FROM freeswitch_cti_dialplan_extension
            WHERE id=%s
            """ % _id)
            _extension = cr.dictfetchone()
        return _extension

    def _execute_dialplan(self, dialplan):
        _start_node = self._search_dialplan_start_node(dialplan)
        if not _start_node:
            return
        _logger.info(">>>>>>>>>>>>>> start node <<<<<<<<<< %s" % _start_node)
        self.server.push_node_event(self, _start_node)
        self.set_current_node(_start_node)
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
        return

    def set_current_node(self, node):
        self.current_node = node
        return

    async def _close_stream(self):
        self.server.close_stream(self.id)
        self.writer.close()
        await self.writer.wait_closed()
        self.is_closed = True
        return

    def _update_stream_variable(self, headers):
        # if self.is_variable_parsed:
        #     return
        
        self.is_variable_parsed = True
        DP_MATCH = headers.get("variable_DP_MATCH")
        if DP_MATCH:
            self.DP_MATCH = []
            groups = DP_MATCH.split("|:")
            if groups and len(groups) > 1:
                groups.pop(0)
                for group in groups:
                    self.DP_MATCH.append(group) 

        def _lower_underscore(item):
            x, y = str(item[0]).lower(), item[1]
            x = x.replace("-", "_")
            return x,y        
        _headers = dict(map(_lower_underscore, headers.items()))
        for _header in _headers.items():
            if _header[0].startswith("variable_"):
                self.variables[_header[0][len("variable_"):]] = _header[1]
        return

    def get_variable_value(self, variable):
        _logger.info("VARIABLE: %s -> " % variable)
        for _var in self.variables.items():
            variable = variable.replace("${%s}" % _var[0], _var[1])
        i = 1
        for DP_MATCH in self.DP_MATCH:
            variable = variable.replace("$%d" % i, DP_MATCH)

        _logger.info("VARIABLE: -> %s" % variable)
        return variable
