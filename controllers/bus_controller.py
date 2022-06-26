# -*- coding: utf-8 -*-


import logging

from odoo import fields
from odoo import http
from odoo.addons.bus.controllers import main

_logger = logging.getLogger(__name__)

class BusController(main.BusController):

    @http.route('/longpolling/poll', type="json", auth="public")
    def poll(self, channels, last, options=None):
        if http.request.env.user.has_group('odoo_freeswitch_cti.group_sip_user'):
            ip_address = http.request.httprequest.remote_addr
            http.request.env.user.write({"user_agent_ip":ip_address, "user_agent_last_seen":fields.Datetime.now()})
        return super().poll(channels, last, options=options)

    def _poll(self, dbname, channels, last, options):
        channels = list(channels)  # do not alter original list
        if http.request.env.user.has_group('odoo_freeswitch_cti.group_sip_user'):
            channels.append('agent_update')
            channels.append('queue_update')
        return super()._poll(dbname, channels, last, options)

