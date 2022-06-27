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
        self.channels = {}

        self._tmp_headers = {}
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

    async def _run_command_loop(self):
        while True:
            if self.is_stop:
                self._stop()
                break
            if self.client_status == "SUBSCRIBED":
                self._dispatch_cti_commands()
            await asyncio.sleep(1)
        return

    async def _parse_header(self, header):
        _logger.info(header)
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
            return True

        # freeswitch closed
        if self._is_break_headers(headers):
            self._tmp_headers = {}
            return False

        # keep receive more headers
        if self._is_meta_headers(headers):
            return True
        
        _logger.info("HEADERS %s", headers)
        await self._handle_headers(headers)
        self._log_event(headers)
        await self._push_event(headers)
        self._tmp_headers = {}
        return True

    async def _run_cti_loop(self):
        while True:
            if self.is_stop:
                self._stop()
                return
            try:
                self.reader, self.writer = await asyncio.open_connection(self.freeswitch_info["freeswitch_ip"], 8021)
            except:
                _logger.error("Disconnect: [%s], restart in 5 seconds." % self.freeswitch_info["freeswitch_ip"])
                await asyncio.sleep(5)
                continue

            _logger.info("FreeSWITCH: [%s] online" % self.freeswitch_info["freeswitch_ip"])
            
            self.client_status = "NULL"
            while True:
                if self.is_stop:
                    self._stop()
                    return
                try:
                    _timeout = 10
                    _header = await asyncio.wait_for(self.reader.readline(), timeout=_timeout)
                except asyncio.TimeoutError:
                    _logger.error("In [%d] seconds, no event, reconnect" % _timeout)
                    break
            
                if not _header:
                    break

                if not await self._parse_header(_header):
                    break
        return
    
    async def run_loop(self):
        self.db_connection = odoo.sql_db.db_connect(self.dbname)
        _freeswitch = self._get_freeswitch_info(self.db_connection)
        if not _freeswitch:
            _logger.error("No freeswitch, exit CTI.")
            return
        
        self.freeswitch_info = _freeswitch
        
        await asyncio.gather(self._run_command_loop(),
                             self._run_cti_loop())
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

        _logger.info("Event-Name: [%s], Unique-ID: [%s], Call-Direction: [%s], Channel-Call-UUID: [%s], Other-Leg-Unique-ID: [%s]" %
                     (_event_name,
                      headers.get("Unique-ID"),
                      headers.get("Call-Direction"),
                      headers.get("Channel-Call-UUID"),
                      headers.get("Other-Leg-Unique-ID")
                      ))

        _event_func_name = "_handle_event_func_%s" % _event_name.upper()
        if hasattr(self, _event_func_name):
            _event_func = getattr(self, _event_func_name)
            _event_func(headers)
        else:
            _logger.error("no _func defined for event [%s]" % _event_name)
            _logger.error("%s" % headers)

        return

    def _handle_event_func_CHANNEL_CREATE(self, headers):
        self._create_user_channel_map(headers)
        self._update_sip_phone_channel_create(headers)
        #"Call-Direction"
        #"Caller-Username"
        #"Caller-Caller-ID-Number"
        #"Unique-ID"
        # "Caller-Destination-Number
        #_logger.info(headers)
        return

    def _handle_event_func_CHANNEL_STATE(self, headers):
        #self._update_user_channel_map(headers)
        #"Call-Direction"
        #"Caller-Username"
        #"Caller-Caller-ID-Number"
        #"Unique-ID"
        # "Caller-Destination-Number
        #_logger.info(headers)
        return

    def _handle_event_func_CHANNEL_CALLSTATE(self, headers):
        #self._update_user_channel_map(headers)
        #"Call-Direction"
        #"Caller-Username"
        #"Caller-Caller-ID-Number"
        #"Unique-ID"
        # "Caller-Destination-Number
        #_logger.info(headers)
        return

    def _handle_event_func_CHANNEL_EXECUTE(self, headers):
        #self._update_user_channel_map(headers)
        #"Call-Direction"
        #"Caller-Username"
        #"Caller-Caller-ID-Number"
        #"Unique-ID"
        # "Caller-Destination-Number
        #_logger.info(headers)
        return

    def _handle_event_func_CHANNEL_EXECUTE_COMPLETE(self, headers):
        #self._update_user_channel_map(headers)
        #"Call-Direction"
        #"Caller-Username"
        #"Caller-Caller-ID-Number"
        #"Unique-ID"
        # "Caller-Destination-Number
        #_logger.info(headers)
        return

    def _handle_event_func_CHANNEL_DESTROY(self, headers):
        # _uuid = headers.get("Unique-ID")
        # _channel = self.channels.get(_uuid)
        # if _channel:
        #     _logger.info("MY CHANNEL: %s" % _channel)

        #     _other_uuid = _channel.get("other_uuid")
        #     if _other_uuid:
        #         _other_channel = self.channels.get(_other_uuid)
        #         _logger.info("OTHER CHANNEL: %s" % _other_channel)
        return

    def _handle_event_func_CHANNEL_HANGUP(self, headers):
        self._update_sip_phone_hangup(headers)
        self._remove_user_channel_map(headers)
        return
    
    def _handle_event_func_CHANNEL_HANGUP_COMPLETE(self, headers):
        return

    def _handle_event_func_CODEC(self, headers):
        return

    def _handle_event_func_CHANNEL_PROGRESS_MEDIA(self, headers):
        return

    def _handle_event_func_CHANNEL_PROGRESS(self, headers):
        return

    def _handle_event_func_CHANNEL_ORIGINATE(self, headers):
        return

    def _handle_event_func_CHANNEL_OUTGOING(self, headers):
        return
    
    def _handle_event_func_CHANNEL_ANSWER(self, headers):
        self._update_sip_phone_answer(headers)
        return

    def _handle_event_func_CHANNEL_BRIDGE(self, headers):
        return

    def _handle_event_func_CHANNEL_UNBRIDGE(self, headers):
        return

    def _handle_event_func_CALL_UPDATE(self, headers):
        return

    def _handle_event_func_HEARTBEAT(self, headers):
        self._update_freeswitch_info_last_seen()
        return

    def _handle_event_func_CUSTOM(self, headers):
        _subclass = headers.get("Event-Subclass")
        if not _subclass:
            return
        _subclass_handler_name = "_handle_subclass_func_%s" % ("_").join(_subclass.split("::"))
        if not hasattr(self, _subclass_handler_name):
            _logger.error("No subclass [%s] handler" % _subclass)
            return
        getattr(self, _subclass_handler_name)(headers)
        return

    def _handle_event_func_PRESENCE_IN(self, headers):
        #self._update_sip_phone_presence(headers)
        return
    
    def _handle_event_func_BACKGROUND_JOB(self, headers):
        _job_uuid = headers.get("Job-UUID")
        _command = self.jobs.get(_job_uuid)
        if not _command:
            _logger.error("No job for uuid: [%s]" % _job_uuid)
            _logger.info(headers)
            return    
        _content_content = headers.get("Content-Content") or ""
        self._update_cti_command_status(_command["cti_command_id"],
                                        "CONFIRM",
                                        result=_content_content)
        del self.jobs[_job_uuid]
        return

    def _handle_event_func_API(self, headers):
        return

    def _send_bgapi_command(self, command, parameter, record_id):
        self.bgapi_commands.append({"cti_command": command,
                                    "cti_parameter": parameter,
                                    "cti_command_id": record_id})
        _cmd = "bgapi %s %s" % (command, parameter)
        self._send_cmd(_cmd)
        return

    def _send_json_command(self, command, parameter, record_id):
        self.bgapi_commands.append({"cti_command": command,
                                    "cti_parameter": parameter,
                                    "cti_command_id": record_id})
        _cmd = "bgapi json %s" % {"command": command, "data": {"arguments": parameter}}
        self._send_cmd(_cmd)
        return
    
    # def _send_test_commands(self):
    #     self._send_bgapi_command("status", 1)
    #     return
    
    def _is_ignored_event(self, headers):
        _ignore_events = ["RE_SCHEDULE", "MODULE_UNLOAD"]
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
            _id = _command["id"]
            _name = _command["name"]
            _parameter = _command.get("parameter") or ""
            if _name.startswith("callcenter"):
                self._send_json_command(_name, _parameter, _id)
            else:
                self._send_bgapi_command(_name, _parameter, _id)
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

        _customs += [
            "callcenter::info"
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
            SELECT * FROM freeswitch_cti_freeswitch
            WHERE is_active = true
            ORDER BY create_date DESC
            LIMIT 1
            """)
            _freeswitch = cr.dictfetchone()
        return _freeswitch

    def _update_freeswitch_info_last_seen(self):
        with self.db_connection.cursor() as cr:
            cr.execute("""
            UPDATE freeswitch_cti_freeswitch
            set last_seen=now()
            WHERE id=%d
            """ % self.freeswitch_info["id"])
            cr.commit()
        return

    def _is_ignored_event_for_log(self, headers):
        _do_not_log = ["RE_SCHEDULE", "HEARTBEAT", "MODULE_UNLOAD"]
        if headers.get("Event-Name") in _do_not_log:
            return True
        return False

    def _log_event(self, headers):
        if self._is_ignored_event_for_log(headers):
            return        
        _command = headers.get("Job-Command") or headers.get("API-Command") or ""
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
                  _command))
            _r = cr.fetchone()
            headers.update({"cti_event_id": _r})
        return

    async def _push_event(self, headers):
        if self._is_ignored_event_for_log(headers):
            return

        async with aiohttp.ClientSession() as session:
            _event_url = "http://localhost:8069/web/cti_event/%d" % headers.get("cti_event_id")
            async with session.get(_event_url) as resp:
                _r = await resp.json()
                #_logger.info("push cti_event: %s" % _r)
        return

    def _handle_subclass_func_callcenter_info(self, headers):
        """
        agent-status-change
        When an agent's Status changes, this event is generated with the agent's new Status.
        
        Event-Subclass: callcenter::info
        Event-Name: CUSTOM
        CC-Agent: 1000@default
        CC-Action: agent-status-change
        CC-Agent-Status: Available

        agent-state-change
        Every time an agent's State changes, this event is generated.

        Event-Subclass: callcenter::info
        Event-Name: CUSTOM
        CC-Agent: 1000@default
        CC-Action: agent-state-change
        CC-Agent-State: Receiving

        agent-offering
        Every time a caller is presented to an agent (before he answers), this event is generated.
        
        Event-Subclass: callcenter::info 
        Event-Name: CUSTOM 
        CC-Queue: support@default
        CC-Agent: AgentNameHere
        CC-Action: agent-offering 
        CC-Agent-System: single_box 
        CC-Member-UUID: 453324f8-3424-4322-4242362fd23d 
        CC-Member-Session-UUID: 600165a4-f748-11df-afdd-b386769690cd 
        CC-Member-CID-Name: CHOUINARD MO 
        CC-Member-CID-Number: 4385551212

        bridge-agent-start
        When an agent is connected, this event is generated. NOTE: the channel variables, including, for example, Event-Date-Timestamp are present as well as the callcenter values.
        
        Event-Subclass: callcenter::info
        Event-Name: CUSTOM
        CC-Queue: support@default
        CC-Action: bridge-agent-start
        CC-Agent: AgentNameHere
        CC-Agent-System: single_box
        CC-Agent-UUID: 7acfecd3-ab50-470b-8875-d37aba0429ba
        CC-Agent-Called-Time: 10000
        CC-Agent-Answered-Time: 10009
        CC-Member-Joined-Time: 9000
        CC-Member-UUID: 453324f8-3424-4322-4242362fd23d 
        CC-Member-Session-UUID: c6360976-231c-43c6-bda7-7ac4c7d1c125
        CC-Member-CID-Name: Their Name
        CC-Member-CID-Number: 555-555-5555

        bridge-agent-end
        When an agent is disconnected, this event is generated. NOTE: the channel variables, including, for example, Event-Date-Timestamp are present as well as the callcenter values.
        
        Event-Subclass: callcenter::info
        Event-Name: CUSTOM
        CC-Queue: support@default
        CC-Action: bridge-agent-end
        CC-Agent: AgentNameHere
        CC-Agent-System: single_box
        CC-Agent-UUID: 7acfecd3-ab50-470b-8875-d37aba0429ba
        CC-Agent-Called-Time: 10000
        CC-Agent-Answered-Time: 10009
        CC-Bridge-Terminated-Time: 10500
        CC-Member-Joined-Time: 9000
        CC-Member-UUID: 453324f8-3424-4322-4242362fd23d 
        CC-Member-Session-UUID: c6360976-231c-43c6-bda7-7ac4c7d1c125
        CC-Member-CID-Name: Their Name
        CC-Member-CID-Number: 555-555-5555

        bridge-agent-fail
        When an agent originate fail, this event is generated. NOTE: the channel variables, including, for example, Event-Date-Timestamp are present as well as the callcenter values.
        
        Event-Subclass: callcenter::info
        Event-Name: CUSTOM
        CC-Queue: support@default
        CC-Action: bridge-agent-fail
        CC-Hangup-Cause: CHECK FS HANGUP CAUSE
        CC-Agent: AgentNameHere
        CC-Agent-System: single_box
        CC-Member-UUID: 453324f8-3424-4322-4242362fd23d 
        CC-Member-Session-UUID: c6360976-231c-43c6-bda7-7ac4c7d1c125
        CC-Member-CID-Name: Their Name
        CC-Member-CID-Number: 555-555-5555
        

        members-count
        This event is generated every time the queue count api is called and anytime a caller enters or leaves the queue.
        
        Event-Subclass: callcenter::info
        Event-Name: CUSTOM
        CC-Queue: support@default
        CC-Action: members-count
        CC-Count: 1
        CC-Selection: Single-Queue

        member-queue-start
        Joining the queue triggers this event, allowing you to track when callers enter the queue.
        
        Event-Subclass: callcenter::info
        Event-Name: CUSTOM
        CC-Queue: support@default
        CC-Action: member-queue-start
        CC-Member-UUID: 453324f8-3424-4322-4242362fd23d 
        CC-Member-Session-UUID: b77c49c2-a732-11df-9438-e7d9456f8886
        CC-Member-CID-Name: CHOUINARD MO
        CC-Member-CID-Number: 4385551212
        
        member-queue-end
        This is generated when a caller leaves the queue. Different lengths of queue-specific times are reported in seconds. There are two values for CC-Cause: 'Terminated' and 'Cancel'.
        
        'Terminated' means the call ended after talking to an agent. Here is an example:
        
        Event-Subclass: callcenter::info
        Event-Name: CUSTOM
        CC-Queue: support@default
        CC-Action: member-queue-end
        CC-Hangup-Cause: CHECK FS HANGUP CAUSE
        CC-Cause: Terminated
        CC-Agent-Called-Time: 10000
        CC-Agent-Answered-Time: 10009
        CC-Member-Joined-Time: 9000
        CC-Member-Leaving-Time: 10100
        CC-Member-UUID: 453324f8-3424-4322-4242362fd23d 
        CC-Member-Session-UUID: b77c49c2-a732-11df-9438-e7d9456f8886
        CC-Member-CID-Name: CHOUINARD MO
        CC-Member-CID-Number: 4385551212

        If we get a hangup from the caller before talking to an agent, the CC-Cause will be 'Cancel'. CC-Cause-Reason will contain the reason of the drop between NONE (no specific reason), TIMEOUT (caller has been waiting more than the timeout), NO_AGENT_TIMEOUT (caller has been waiting more than the no_agent_timeout), and BREAK_OUT (caller abandoned). Here's an example:

        Event-Subclass: callcenter::info
        Event-Name: CUSTOM
        CC-Queue: support@default
        CC-Action: member-queue-end
        CC-Member-Joined-Time: 9000
        CC-Member-Leaving-Time: 10050
        CC-Cause: Cancel
        CC-Cancel-Reason: TIMEOUT
        CC-Member-UUID: 453324f8-3424-4322-4242362fd23d 
        CC-Member-Session-UUID: e260ffd0-a731-11df-9341-e7d9456f8886
        CC-Member-CID-Name: Marc O Robinson
        CC-Member-CID-Number: 5145551212
        
        """
        return
    
    def _handle_subclass_func_sofia_register_attempt(self, headers):
        return

    def _handle_subclass_func_sofia_register(self, headers):
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

        _logger.info("PRESENCE IN: [%s: %s]" % (_from, _event_type))
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

    def _create_user_channel_map(self, headers):
        #"Call-Direction"
        #"Caller-Username"
        #"Caller-Caller-ID-Number"
        #"Unique-ID"
        #"Caller-Destination-Number
        # Channel-Call-UUID
        # Other-Leg-Unique-ID
        # Other-Leg-Destination-Number
        _call_direction = headers.get("Call-Direction")
        _uuid = headers.get("Unique-ID")
        if not _uuid or not _call_direction:
            _logger.error("CHANNEL CREATE WITHOUT direction or unique id [%s]" % headers)
            return
        _other_leg_unique_id = headers.get("Other-Leg-Unique-ID")
        if _other_leg_unique_id:
            _other_channel = self.channels.get(_other_leg_unique_id)
            if _other_channel:
                _other_channel.update({"other_uuid": _uuid})
        self.channels[_uuid] = {
            "uuid": _uuid,
            "call_direction": _call_direction,
            "caller_id": headers.get("Caller-Caller-ID-Number"),
            "called_id": headers.get("Caller-Destination-Number"),
            "other_uuid": _other_leg_unique_id
        }

        _logger.info("CHANNEL CREATE : %s: " % self.channels)
        return    

    def _update_sip_phone_answer(self, headers):
        _uuid = headers.get("Unique-ID")
        _sip_number = self._get_sip_number_from_channel_map(_uuid)
        self._update_sip_phone_status(_sip_number, "talking")
        return

    def _update_sip_phone_channel_create(self, headers):
        _uuid = headers.get("Unique-ID")
        _sip_number = self._get_sip_number_from_channel_map(_uuid)

        _call_direction = self.channels[_uuid]["call_direction"]

        _status = "calling"
        if _call_direction == "outbound":
            _status = "ringing"
        self._update_sip_phone_status(_sip_number, _status)
        return

    def _update_sip_phone_hangup(self, headers):
        _uuid = headers.get("Unique-ID")
        _sip_number = self._get_sip_number_from_channel_map(_uuid)
        self._update_sip_phone_status(_sip_number, "hangup")
        return

    def _remove_user_channel_map(self, headers):
        _uuid = headers.get("Unique-ID")
        del self.channels[_uuid]
        return

    def _get_sip_number_from_channel_map(self, _uuid):
        # inbound/outbound is from FreeSwitch' point of view.
        # not real world meaning.
        _channel = self.channels[_uuid]
        if _channel["call_direction"] == "inbound":
            return _channel["caller_id"]
        return _channel["called_id"]

    def _update_sip_phone_status(self, sip_number, status):
        with self.db_connection.cursor() as cr:
            cr.execute("""
            UPDATE res_users SET
            sip_phone_status='%s',
            sip_phone_last_seen=now()
            WHERE sip_number='%s'
            """ % (status, sip_number))
            cr.commit()
        return
