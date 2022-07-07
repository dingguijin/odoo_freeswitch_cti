# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class DialplanExtension(models.Model):

    _name = "freeswitch_cti.dialplan_extension"
    _description = "Dialplan Extension"

    name = fields.Char('Name', required=True)

    type = fields.Selection([('telephone', 'Telephone'),
                             ('chat', 'Chat')], 'Type', default='telephone')
    
    profile = fields.Selection([('internal', 'Internal'),
                                  ('external', 'External')], 'Profile')

    context = fields.Selection([('default', 'Default'),
                                  ('public', 'Public')], 'Context')

    is_continue = fields.Boolean("Is Continue", default=False)

    condition_field = fields.Char("Condition Field")
    condition_expression = fields.Char("Condition Expression")

    # less is higher
    priority = fields.Integer("Priority", default=1)

    is_active = fields.Boolean("Is Active", default=True)
    
    node_ids = fields.One2many("freeswitch_cti.dialplan_node", "extension_id")
