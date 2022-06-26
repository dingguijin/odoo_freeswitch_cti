# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class FreeSwitch(models.Model):

    _name = "freeswitch_cti.freeswitch"
    _description = "FreeSwitch"

    name = fields.Char('FreeSwitch Name', required=True)
    
    freeswitch_hostname = fields.Char('FreeSwitch Host Name', required=True)
    freeswitch_ip = fields.Char('Freeswitch IP Address', translate=True, required=True)
    freeswitch_password = fields.Char('Freeswitch Password', translate=True, required=True)

    is_active = fields.Boolean("is active", required=False)
    is_online = fields.Boolean("Is online", required=False)
    uptime = fields.Integer("Uptime", required=False)
    last_seen = fields.Datetime("Last seen", required=False)
