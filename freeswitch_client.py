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

_logger = logging.getLogger(__name__)

class FreeSwitchClient():
    def __init__(self, dbname):
        self.dbname = dbname

        self.writer = None
        self.reader = None
        self.db_connection = None
        self.freeswitch_info = None
        
        self.is_stop = False
        self.client_status = "NULL" # AUTH
        self.bgapi_commands = collections.deque([])
        self.jobs = {}
        return

    def stop(self):
        self.is_stop = True
        return

    async def _stop(self):
        await self.writer.drain()
        self.writer.close()
        await self.writer.closed()
        odoo.sql_db.close_db(self.dbname)

        self.is_stop = False
        self.client_status = "NULL" # AUTH
        self.bgapi_commands = collections.deque([])
        self.jobs = {}

        return

    async def run_loop(self):

        self.db_connection = odoo.sql_db.db_connect(self.dbname)
        _freeswitch = self._get_freeswitch_info(self.db_connection)
        if not _freeswitch:
            _logger.error("No predefined freeswitch, exit CTI.")
            return
        
        self.freeswitch_info = _freeswitch
        try:
            self.reader, self.writer = await asyncio.open_connection(_freeswitch["freeswitch_ip"], 8021)
        except:
            _logger.error("Can not connect freeswitch: [%s], auto restarting." % _freeswitch["freeswitch_ip"])
            return
        
        _headers = {}
        while True:

            if self.is_stop:
                self._stop()
                break

            try:
                _header = await asyncio.wait_for(self.reader.readline(), timeout=3.0)
            except asyncio.TimeoutError:
                #_logger.info(">>>>>>>>> No event to read, continue")
                if self.client_status == "SUBSCRIBED":
                    self._dispatch_cti_commands()
                continue
            
            # _logger.info("CTIClient .............. %s", _header)            
            if not _header:
                self._stop()
                break

            parts = _header.split(b":")
            if len(parts) == 2:
                _key = urllib.parse.unquote(parts[0].strip())
                _value = urllib.parse.unquote(parts[1].strip())
                if _key == "Content-Length" and "Content-Length" in _headers:
                    _key = "Content-Content-Length"
                _headers[_key] = _value 

            if _header == b"\n":
                if self._is_break_headers(_headers):
                    self.client_status = "NULL"
                    break

                if self._is_meta_headers(_headers):
                    continue

                #_logger.info("HEADERS %s", _headers)
                await self._handle_headers(_headers)
                self._log_event(_headers)
                await self._push_event(_headers)
                _headers = {}

            if self.client_status == "SUBSCRIBED":
                self._dispatch_cti_commands()

        return
    
    def _is_meta_headers(self, headers):
        if self.client_status != "SUBSCRIBED":
            return False
        if len(headers) != 2:
            return False
        if headers.get("Content-Type") != "text/event-plain":
            return False
        if not headers.get("Content-Length"):
            return False        
        return True

    def _is_break_headers(self, headers):
        if headers.get("Content-Type") == "text/disconnect-notice":
            return True
        # if headers.get("Content-Type") == "text/rude-rejection":
        #     return True
        return False
    
    async def _handle_headers(self, headers):
        if self.client_status == "NULL" and headers.get("Content-Type") == "auth/request":
            self._send_cmd("auth %s" % self.freeswitch_info["freeswitch_password"])
            self.client_status = "AUTHING"
            return
            
        if self.client_status == "AUTHING" and headers.get("Content-Type") == "command/reply":
            if headers.get("Reply-Text") == "+OK accepted":
                self.client_status = "AUTHED"
                self._send_interest_events()
                return
            
        if self.client_status == "AUTHED" and headers.get("Content-Type") == "command/reply":
            if headers.get("Reply-Text") == "+OK event listener enabled plain":
                self.client_status = "SUBSCRIBED"
                return

        if self.client_status == "SUBSCRIBED" and headers.get("Content-Content-Length"):
            _length = headers.get("Content-Content-Length")
            _content = await self.reader.read(int(_length))
            _content = _content.decode("utf-8")
            headers["Content-Content"] = _content

        if headers.get("Content-Type") == "command/reply":
            self._handle_command_reply(headers)
            return
            
        if self._is_ignored_event(headers):
            return

        self._handle_event(headers)
        
        return

    def _handle_command_reply(self, headers):
        _job_uuid = headers.get("Job-UUID")
        if _job_uuid:
            _command = self.bgapi_commands.popleft()
            self.jobs[_job_uuid] = _command
        return

    def _handle_event(self, headers):
        # _content = headers.get("Content-Content")
        # if _content:
        #     _cl = _content.split("\n")
        #     _logger.info(_cl)

        _event_name = headers.get("Event-Name")
        if not _event_name:
            return
        
        _event_func_name = "_handle_event_func_%s" % _event_name.upper()
        if hasattr(self, _event_func_name):
            _event_func = getattr(self, _event_func_name)
            _event_func(headers)
        else:
            _logger.error("no _func defined for event [%s]" % _event_name)
            _logger.error("%s" % headers)

        return

    def _handle_event_func_CHANNEL_CREATE(self, headers):
        #self._update_user_channel_map(headers)
        #"Call-Direction"
        #"Caller-Username"
        #"Caller-Caller-ID-Number"
        #"Unique-ID"
        # "Caller-Destination-Number
        _logger.info(headers)
        return

    def _handle_event_func_CHANNEL_STATE(self, headers):
        #self._update_user_channel_map(headers)
        #"Call-Direction"
        #"Caller-Username"
        #"Caller-Caller-ID-Number"
        #"Unique-ID"
        # "Caller-Destination-Number
        _logger.info(headers)
        return

    def _handle_event_func_CHANNEL_CALLSTATE(self, headers):
        #self._update_user_channel_map(headers)
        #"Call-Direction"
        #"Caller-Username"
        #"Caller-Caller-ID-Number"
        #"Unique-ID"
        # "Caller-Destination-Number
        _logger.info(headers)
        return

    def _handle_event_func_CHANNEL_EXECUTE(self, headers):
        #self._update_user_channel_map(headers)
        #"Call-Direction"
        #"Caller-Username"
        #"Caller-Caller-ID-Number"
        #"Unique-ID"
        # "Caller-Destination-Number
        _logger.info(headers)
        return

    def _handle_event_func_CHANNEL_EXECUTE_COMPLETE(self, headers):
        #self._update_user_channel_map(headers)
        #"Call-Direction"
        #"Caller-Username"
        #"Caller-Caller-ID-Number"
        #"Unique-ID"
        # "Caller-Destination-Number
        _logger.info(headers)
        return

    def _handle_event_func_HEARTBEAT(self, headers):
        self._update_freeswitch_info_last_seen()
        return

    def _handle_event_func_CUSTOM(self, headers):
        _subclass = headers.get("Event-Subclass")
        if _subclass == "sofia::register_attempt":
            return
        if _subclass == "sofia::register":
            self._update_sip_register_status(headers)
            return
        return

    def _handle_event_func_PRESENCE_IN(self, headers):
        self._update_sip_phone_presence(headers)
        return
    
    def _handle_event_func_BACKGROUND_JOB(self, headers):
        _job_uuid = headers.get("Job-UUID")
        _command = self.jobs.get(_job_uuid)
        if not _command:
            _logger.error("No job for uuid: [%s]" % _job_uuid)
            #_logger.info(headers)
            return    
        _content_content = headers.get("Content-Content") or ""
        self._update_cti_command_status(_command["cti_command_id"],
                                        "CONFIRM",
                                        result=_content_content)
        del self.jobs[_job_uuid]
        return

    def _handle_event_func_API(self, headers):
        return

    def _send_bgapi_command(self, command, record_id):
        self.bgapi_commands.append({"cti_command": command,
                                    "cti_command_id": record_id})
        _cmd = "bgapi %s" % command
        self._send_cmd(_cmd)
        return
    
    # def _send_test_commands(self):
    #     self._send_bgapi_command("status", 1)
    #     return
    
    def _is_ignored_event(self, headers):
        _ignore_events = ["RE_SCHEDULE"]
        _event_name = headers.get("Event-Name")
        if _event_name in _ignore_events:
            return True
        return False

    def _dispatch_cti_commands(self):
        _commands = None
        with self.db_connection.cursor() as cr:
            cr.execute("""
            SELECT * 
            FROM freeswitch_cti_cti_command
            WHERE status = 'NEW'
            ORDER BY create_date ASC
            """)
            _commands = cr.dictfetchall()
        if not _commands:
            return
        self._send_cti_commands(_commands)
        for _command in _commands:
            self._update_cti_command_status(_command["id"], "EXECUTE")
        return
        
    def _send_cti_commands(self, commands):
        for _command in commands:
            _parameter = _command.get("parameter") or ""
            _cti_command = "%s %s" % (_command["name"], _parameter)
            self._send_bgapi_command(_cti_command, _command["id"])
        return
    
    def _send_interest_events(self):
        _customs = [
            "sofia::register",  
            "sofia::unregister",
            "sofia::expire",
            "sofia::register_attempt",
            "sofia::register_failure",
            "sofia::gateway_add",   
            "sofia::gateway_delete",
            "sofia::gateway_state"
        ]
        self._send_cmd("event plain ALL")
        self._send_cmd("event CUSTOM %s" % " ".join(_customs))
        return
    
    def _send_cmd(self, cmd):
        cmd = "%s\n\n\n\n" % cmd
        cmd = cmd.encode("utf-8")
        self.writer.write(cmd)
        _logger.info(">>>>>>>>>>>>>>>>>>>send command [%s]", cmd)
        return

    def _update_cti_command_status(self, id, status, result=""):
        if not id:
            return
        _time = "%s_time=now()" % status.lower()
        with self.db_connection.cursor() as cr:
            _sql = """
            UPDATE freeswitch_cti_cti_command
            SET status='%s', result='%s', %s
            WHERE id = %d
            """ % (status, result, _time, id)
            cr.execute(_sql)
            cr.commit()
        return

    def _get_freeswitch_info(self, db):
        _freeswith = None
        with db.cursor() as cr:
            cr.execute("""
            SELECT * FROM freeswitch_xml_curl_freeswitch
            WHERE is_active = true
            ORDER BY create_date DESC
            LIMIT 1
            """)
            _freeswitch = cr.dictfetchone()
        return _freeswitch

    def _update_freeswitch_info_last_seen(self):
        with self.db_connection.cursor() as cr:
            cr.execute("""
            UPDATE freeswitch_xml_curl_freeswitch
            set last_seen=now()
            WHERE id=%d
            """ % self.freeswitch_info["id"])
            cr.commit()
        return
        
    def _log_event(self, headers):
        _do_not_log = ["RE_SCHEDULE", "HEARTBEAT"]
        if headers.get("Event-Name") in _do_not_log:
            return

        with self.db_connection.cursor() as cr:
            _r = cr.execute("""
            INSERT into freeswitch_cti_cti_event
            (name, freeswitch, content_type, content_length, content_content, event_content, subclass, command_name, create_date) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, now()) RETURNING id;
            """, (headers.get("Event-Name") or "",
                  self.freeswitch_info["id"],
                  headers.get("Content-Type") or "",
                  headers.get("Content-Length") or 0,
                  headers.get("Content-Content") or "",
                  json.dumps(headers),
                  headers.get("Event-Subclass") or "",
                  headers.get("Job-Command") or ""))
            _r = cr.fetchone()
            headers.update({"cti_event_id": _r})
        return

    async def _push_event(self, headers):
        _do_not_push = ["RE_SCHEDULE", "HEARTBEAT"]
        if headers.get("Event-Name") in _do_not_push:
            return
        
        async with aiohttp.ClientSession() as session:
            _event_url = "http://localhost:8069/web/cti_event/%d" % headers.get("cti_event_id")
            async with session.get(_event_url) as resp:
                _r = await resp.json()
                #_logger.info("push cti_event: %s" % _r)
        return
        

    def _update_sip_register_status(self, headers):
        _status = headers.get("status") or ""# Registered(UDP)
        _user_agent = headers.get("user-agent") or ""
        _sip_auth_username = headers.get("sip_auth_username") or ""
        _sip_auth_realm = headers.get("sip_auth_realm") or ""
        _sip_phone_ip = headers.get("network-ip") or ""
        if not _sip_auth_username:
            return
        with self.db_connection.cursor() as cr:
            cr.execute("""
            UPDATE res_users
            set sip_register_status='%s',
            sip_phone_user_agent='%s',
            sip_phone_ip='%s',
            sip_auth_realm='%s',
            sip_phone_last_seen=now()
            WHERE sip_number='%s'
            """ % (_status, _user_agent, _sip_phone_ip,
                   _sip_auth_realm, _sip_auth_username))
            cr.commit()
        return

    def _update_sip_phone_presence(self, headers):
        _from = headers.get("from") or ""
        _event_type = headers.get("event_type") or ""
        _user_agent = headers.get("user-agent") or ""

        if not _from or not _event_type:
            return
        _sip_number = _from.split("@")[0]
        with self.db_connection.cursor() as cr:
            cr.execute("""
            UPDATE res_users SET
            sip_phone_status='%s',
            sip_phone_last_seen=now()
            WHERE sip_number='%s'
            """ % (_event_type, _sip_number))
            cr.commit()
        return

