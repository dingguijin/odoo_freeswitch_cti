# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

from . import dialplan_node_type

_node_types = dialplan_node_type.get_node_types()
_node_types = list(map(lambda x: (x.get("type"), x.get("name")), _node_types))

class DialplanNode(models.Model):

    _name = "freeswitch_cti.dialplan_node"
    _description = "Dialplan Node"

    name = fields.Char('Name', required=True)
    extension_id = fields.Many2one('freeswitch_cti.dialplan_extension', string='Dialplan Extension', ondelete='cascade')
    
    node_type = fields.Selection(_node_types, 'Type')
    
    node_param = fields.Char("Node Parameter")
    node_timeout = fields.Integer("Node Timeout")

    display_top = fields.Integer("Display Top")
    display_left = fields.Integer("Display Left")

