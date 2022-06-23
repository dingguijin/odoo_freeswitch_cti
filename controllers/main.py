# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import json

from odoo import http

_logger = logging.getLogger(__name__)

class Main(http.Controller):

    @http.route('/web/cti_command', type='json', auth="user", methods=['POST'])
    def cti_command(self):
        return http.request.make_response(json.dumps({"result": "OK"}), [('Content-Type', 'application/json')])

    @http.route('/web/cti_event/<int:event>', type='http', auth="none", methods=['GET'])
    def cti_event(self, event):
        #_logger.info(">?????????????< controller event: %d" % event)
        return http.request.make_response(json.dumps({"result": "OK"}), [('Content-Type', 'application/json')])
