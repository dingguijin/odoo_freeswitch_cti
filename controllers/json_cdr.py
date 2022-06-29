# -*- coding: utf-8 -*-

import json
import logging

from odoo import http

_logger = logging.getLogger(__name__)

class FreeSwitchJsonCdr(http.Controller):

    @http.route('/freeswitch_json_cdr', type='json', methods=['POST'], auth='none', csrf=False)
    def xml_cdr(self, *args, **kw):
        # _logger.info(http.request.jsonrequest)
        _logger.info(json.dumps(http.request.jsonrequest, indent=2))
        return ""
