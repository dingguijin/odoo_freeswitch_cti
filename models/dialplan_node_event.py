# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class DialplanNodeEvent(models.Model):

    _name = "freeswitch_cti.dialplan_node_event"
    _description = "Dialplan Node Event"

    name = fields.Char('Name', required=True)
    extension_id = fields.Many2one('freeswitch_cti.dialplan_extension', string='Dialplan Extension', ondelete='cascade')
    node_id = fields.Many2one('freeswitch_cti.dialplan_node', string='Node', ondelete='cascade')
    next_node = fields.Many2one('freeswitch_cti.dialplan_node', string='Next Node')

