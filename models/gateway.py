# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class FreeSwitch(models.Model):

    _name = "freeswitch_cti.gateway"
    _description = "FreeSwitch Gateway"

    name = fields.Char('FreeSwitch Gateway for outbound call', required=True)
    
    gateway_ip = fields.Char('gateway ip', required=True)
    gateway_account = fields.Char('Gateway account', translate=True, required=True)
    gateway_password = fields.Char('Gateway Password', translate=True, required=True)

    is_active = fields.Boolean("is active", required=False)
    is_online = fields.Boolean("Is online", required=False)
    uptime = fields.Integer("Uptime", required=False)
    last_seen = fields.Datetime("Last seen", required=False)
