# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class CtiCdr(models.Model):

    _name = "freeswitch_cti.cti_cdr"
    _description = "Cti Cdr"

    name = fields.Char('Name', required=True)
    direction = fields.Selection([('inbound', 'Inbound'),
                                  ('outbound', 'Outbound')], 'Direction')

    # maybe same with call_uuid
    # variables/uuid
    channel_uuid = fields.Char('Channel UUID')

    # inbound/outbound share this one
    # caller_uuid/ it is caller uuid variables/uuid
    call_uuid = fields.Char('Call UUID', required=True)

    # variables/*
    sip_from_user = fields.Char('Sip from user', required=True)
    sip_to_user = fields.Char('Sip to user', required=True)
    sip_from_host = fields.Char("Sip from host")
    sip_to_host = fields.Char("Sip to host")

    callflow_ids = fields.One2many("freeswitch_cti.cti_callflow", "cdr_id")
    
    # variables/hangup_cause
    # FIXME Selection ORIGINATOR_CANCEL
    hangup_cause = fields.Char('Hangup Cause')

    # variables/*
    duration = fields.Integer("Duration")
    billsec = fields.Integer("Bill Seconds")
    progresssec = fields.Integer("Progress Seconds")
    answersec = fields.Integer("Answer Seconds")
    waitsec = fields.Integer("Wait Seconds")

    record_file = fields.Char("Record File")

