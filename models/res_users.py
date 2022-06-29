# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _
from . import cti_command

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):

    _inherit = "res.users"

    is_callcenter_agent = fields.Boolean('Is Callcenter Agent', compute='_compute_is_callcenter_agent', readonly=True, default=False, store=True)
    
    is_callcenter_supervisor = fields.Boolean('Is Callcenter Supervisor', compute='_compute_is_callcenter_supervisor', readonly=True, default=False, store=True) 
    
    sip_number = fields.Char('Sip Number', required=False)
    sip_password = fields.Char('Sip Password', required=False)
    
    # update by callcenter and PRESENSE IN
    sip_phone_status = fields.Char('Sip Phone Status', required=False, readonly=True)
    sip_agent_status = fields.Char('Sip Agent Status', required=False, readonly=True)

    # update by presence in
    sip_phone_last_seen = fields.Datetime('Sip Phone Last Seen', required=False, readonly=True)

    # update by register
    sip_register_status = fields.Char('Sip Register Status', required=False, readonly=True)
    sip_phone_user_agent = fields.Char('Sip Phone User Agent', required=False, readonly=True)
    sip_phone_ip = fields.Char('Sip Phone IP', required=False, readonly=True)
    sip_auth_realm = fields.Char('Sip Auth Realm', required=False, readonly=True)

    # update by poll
    user_agent_ip = fields.Char('User Agent IP', required=False, readonly=True)
    user_agent_last_seen = fields.Datetime('User Agent Last Seen', required=False, readonly=True)


    agent_name = fields.Char('Agent Contact', compute='_compute_agent_name', readonly=True)
    agent_contact = fields.Char('Agent Contact', compute='_compute_agent_contact', readonly=True)
    agent_type = fields.Selection([('callback', 'Callback'),
                                   ('uuid-standy', 'UUID Standby')],
                                  'Agent Type', default='callback')

    # changed by user interface
    agent_status = fields.Selection([('Available', 'Availabe To Receive Call'),
                                     ('Logged Out', 'Logged Out'),
                                     ('On Break', 'On Break'),
                                     ('Available(On Demand)', 'Available Special')],
                                    'Agent Default Status', default='Logged Out', readonly=True)

    # changed by callcenter system
    agent_state = fields.Selection([('Idle', 'Agent Idle'),
                                    ('Waiting', 'Ready to receive calls'),
                                    ('Receiving', 'A queue call is currently being offered to the agent'),
                                    ('In a queue call', 'Currently on a queue call')], readonly=True)
    
    # If the agent fails to answer calls this number of times, his status is changed to On Break automatically.
    agent_max_no_answer = fields.Integer("Max No Answer", default=1)

    # The amount of time to wait before putting the agent back in the available queue to receive another call, to allow her to complete notes or other tasks.
    agent_wrap_up_time = fields.Integer("Reject Delay Time", default=10)

    # If the agent presses the reject button on her phone, wait this defined time amount.
    agent_reject_delay_time = fields.Integer("Reject Delay Time", default=10)

    # If the agent is on Do Not Disturb, wait this defined time before trying him again.
    agent_busy_delay_time = fields.Integer("Busy Delay Time", default=10)

    # If the agent does not answer the call, wait this defined time before trying him again.
    agent_no_answer_delay_time = fields.Integer("No Answer Delay Time", default=10)
    

    # If defined to true, agent state is changed to Reserved if the old state is Receiving, the call will only be sent to him if the state get's changed.

    # This is useful if you're manipulating agent state external to mod_callcenter. false by default.
    agent_reserve_agents = fields.Boolean("Reserve Agents", default=False)

    # If defined to true, we'll delete all the agents when the module is loaded. false by default.
    agent_truncate_agents_on_load = fields.Boolean("Truncate Agents On Load", default=True)

    # If defined to true, we'll delete all the tiers when the module is loaded. false by default.
    agent_truncate_tiers_on_load = fields.Boolean("Truncate tires on load", default=True)

    @api.depends('sip_number')
    def _compute_agent_contact(self):
        for record in self:
            record.agent_contact = "user/%s" % record.sip_number
        return

    @api.depends('sip_number')
    def _compute_agent_name(self):
        for record in self:
            record.agent_name = "%s@default" % record.sip_number
        return

    def _compute_is_callcenter_agent(self):
        for record in self:
            if record.sip_number and record.has_group("odoo_freeswitch_cti.group_sip_user"):
                record.is_callcenter_agent = True
            else:
                record.is_callcenter_agent = False
        return

    def _compute_is_callcenter_supervisor(self):
        for record in self:
            if record.sip_number and record.has_group("odoo_freeswitch_cti.group_sip_supervisor"):
                record.is_callcenter_supervisor = True
            else:
                record.is_callcenter_supervisor = False
        return

    def search(self, args, offset=0, limit=None, order=None, count=False):
        _logger.info("search .... %s", args)
        self.env.add_to_compute(self._fields["is_callcenter_agent"], super().search([]))
        self.env.add_to_compute(self._fields["is_callcenter_supervisor"], super().search([]))
        return super().search(args, offset, limit, order, count)

    def write(self, vals):
        self._compute_is_callcenter_agent()
        if self.is_callcenter_agent:
            cti_command.send_cti_command("reload", "mod_callcenter")
        return
    
