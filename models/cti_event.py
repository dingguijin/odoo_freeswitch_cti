# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class CtiEvent(models.Model):

    _name = "freeswitch_cti.cti_event"
    _description = "Cti Event"

    
    name = fields.Char('Event Name', required=True)
    freeswitch = fields.Many2one('freeswitch_cti.freeswitch', string='FreeSWITCH')

    content_type = fields.Char('Content Type', required=False)
    content_length = fields.Integer('Content Length', required=False)
    content_content = fields.Char("Content Content", required=False)
    event_content = fields.Char("Event Content", required=False)

    # if backgroup_job
    command_name = fields.Char("Command Name", required=False)
    command_id = fields.Integer("Command ID", required=False)
    command_record = fields.Many2one("freeswitch_cti.cti_command", "Command Record", required=False)

    # if register/unregister/dialing/hangup/offhook
    sip_number = fields.Char("Sip Number", required=False)

    subclass = fields.Char("Event Subclass", required=False)
