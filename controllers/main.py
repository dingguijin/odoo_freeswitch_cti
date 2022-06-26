# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import json

from odoo import http

_logger = logging.getLogger(__name__)

class Main(http.Controller):

    @http.route('/web/cti_command', type='json', auth="user", methods=['POST'])
    def cti_command(self):
        # write command to cti_command and make status new

        return http.request.make_response(json.dumps({"result": "OK"}), [('Content-Type', 'application/json')])

    @http.route('/web/cti_event/<int:event>', type='http', auth="none", methods=['GET'])
    def cti_event(self, event):
        _event = http.request.env['freeswitch_cti.cti_event'].sudo().browse(event)
        http.request.env['bus.bus']._sendone("agent_update", "agent_update",
                                             {
                                                 "event_id": event,
                                                 "event_name": _event.name,
                                                 "event_subclass": _event.subclass
                                             })
        return http.request.make_response(json.dumps({"result": "OK"}), [('Content-Type', 'application/json')])
