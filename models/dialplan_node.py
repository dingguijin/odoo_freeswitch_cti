# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class DialplanNode(models.Model):

    _name = "freeswitch_cti.dialplan_node"
    _description = "Dialplan Node"

    name = fields.Char('Name', required=True)
    extension_id = fields.Many2one('freeswitch_cti.dialplan_extension', string='Dialplan Extension', ondelete='cascade')
    
    node_type = fields.Char('Node Type')
    
    node_param = fields.Char("Node Parameter")
    node_timeout = fields.Integer("Node Timeout")

    display_top = fields.Integer("Display Top")
    display_left = fields.Integer("Display Left")

