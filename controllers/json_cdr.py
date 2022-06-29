# -*- coding: utf-8 -*-

import datetime
import json
import logging

from odoo import http

_logger = logging.getLogger(__name__)

def _from_timestamp(timestamp):
    if not timestamp:
        return None
    return datetime.datetime.fromtimestamp(timestamp/1000000)

class FreeSwitchJsonCdr(http.Controller):

    @http.route('/freeswitch_recording/<record_file>', type='http', methods=['GET'], auth='user')
    def record_file(self, record_file):
        _record_path = "/usr/local/freeswitch/recordings/" + record_file
        with open(_record_path, "r") as _file:
            _record_data = _file.read()
        httpheaders = [('Content-Type', 'audio/wav'), ('Content-Length', len(_record_data))]
        return request.make_response(_record_data, headers=httpheaders)

    @http.route('/freeswitch_json_cdr', type='json', methods=['POST'], auth='none', csrf=False)
    def xml_cdr(self, *args, **kw):
        # _logger.info(http.request.jsonrequest)
        _logger.info(json.dumps(http.request.jsonrequest, indent=2))

        _cdr = http.request.jsonrequest
        _variables = _cdr.get("variables")
        _record_file = None
        _app_log = _cdr.get("app_log") or {}
        _applications = _app_log.get("applications") or []
        for _application in _applications:
            if _application.get("app_name") == "bind_meta_app":
                if _application.get("app_data").find("record_session::") >=0:
                    _record_file = _application.get("app_data").split("/")[-1]

        _cdr_id = http.request.env["cti_cdr"].sudo().create({
            "name": _variables.get("uuid"),
            "direction": _variables.get("direction"),
            "channel_uuid": _variables.get("uuid"),
            "call_uuid": _variables.get("call_uuid"),
            "sip_from_user": _variables.get("sip_from_user"),
            "sip_to_user": _variables.get("sip_to_user"),
            "sip_from_host": _variables.get("sip_from_host"),
            "sip_to_host": _variables.get("sip_to_host"),
            "hangup_cause": _variables.get("hangup_cause"),
            "duration": _variables.get("duration"),
            "billsec": _variables.get("billsec"),
            "progresssec": _variables.get("progresssec"),
            "answersec": _variables.get("answersec"),
            "waitsec": _variables.get("waitsec"),
            "record_file": _record_file
        })
        _callflows = _cdr.get("callflow") or []
        for _callflow in _callflows:
            _caller_profile = _callflow.get("caller_profile") or {}
            _times = _callflow.get("times") or {}
            http.request.env["cti_callflow"].sudo().create({
                "cdr_id": _cdr_id,
                "profile_index": _callflow.get("profile_index"),
                "caller_profile_username": _caller_profile.get("username"),
                "caller_profile_caller_id_name": _caller_profile.get("caller_id_name"),
                "caller_profile_caller_id_number": _caller_profile.get("caller_id_number"),
                "caller_profile_network_addr": _caller_profile.get("network_addr"),
                "caller_profile_destination_number": _caller_profile.get("destination_number"),
                "caller_profile_uuid": _caller_profile.get("uuid"),
                "caller_profile_chan_name": _caller_profile.get("chan_name"),

                "times_created_time": _from_timestamp(_times.get("created_time")),
                "times_profile_created_time": _from_timestamp(_times.get("profile_created_time")),
                "times_progress_time": _from_timestamp(_times.get("progress_time")),
                "times_progress_media_time": _from_timestamp(_times.get("progress_media_time")),
                "times_answered_time": _from_timestamp(_times.get("answered_time")),
                "times_bridged_time": _from_timestamp(_times.get("bridged_time")),
                "times_last_hold_time": _from_timestamp(_times.get("last_hold_time")),
                "times_hold_accum_time": _from_timestamp(_times.get("hold_accum_time")),
                "times_hangup_time": _from_timestamp(_times.get("hangup_time")),
                "times_resurrect_time": _from_timestamp(_times.get("resurrect_time")),
                "times_transfer_time": _from_timestamp(_times.get("transfer_time"))
            })
        return ""
