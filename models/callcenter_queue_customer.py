# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class CallcenterQueueCustomer(models.Model):

    _name = "freeswitch_cti.callcenter_queue_customer"
    _description = "Callcenter Queue Customer"

    name = fields.Char('Name', related='customer_id.name')
    
    customer_id = fields.Many2one('res.partner', 'Customer')
    queue_id = fields.Many2one('freeswitch_cti.callcenter_queue', 'Queue')

    is_active = fields.Boolean('Is Active', default=True)

    enter_time = fields.Datetime('Enter Time')
    leave_time = fields.Datetime('Leave Time')
