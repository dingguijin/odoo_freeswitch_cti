# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class CallcenterTier(models.Model):

    _name = "freeswitch_cti.callcenter_tier"
    _description = "Callcenter Tier"

    name = fields.Char('Name', related="tier_agent_id.name")
    
    tier_agent_id = fields.Many2one('res.users', 'Agent', required=True)
    tier_queue_id = fields.Many2one('freeswitch_cti.callcenter_queue', 'Queue', required=True)
    tier_level = fields.Integer('Tier Level', default=1)
    tier_position = fields.Integer('Tier Position', default=1)
    
    _sql_constraints = [
        ('tier_unique', 'UNIQUE(tier_agent_id, tier_queue_id)', 'One agent in queue one time')
    ]

    @api.model
    def create(self, vals):
        _r = super().create(vals)
        self.env["freeswitch_cti.cti_command"].send_cti_command("reload", "mod_callcenter")
        return _r

    def write(self, vals):
        _r = super().write(vals)
        self.env["freeswitch_cti.cti_command"].send_cti_command("reload", "mod_callcenter")
        return _r

    def unlink(self):
        _r = super().unlink()
        self.env["freeswitch_cti.cti_command"].send_cti_command("reload", "mod_callcenter")
        return _r
