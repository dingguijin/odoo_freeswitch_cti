# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

class CallcenterQueue(models.Model):

    _name = "freeswitch_cti.callcenter_queue"
    _description = "Callcenter Queue"

    queue_tiers = fields.One2many("freeswitch_cti.callcenter_tier", "tier_queue_id")
    queue_customers = fields.One2many("freeswitch_cti.callcenter_queue_customer", "queue_id")

    queue_agents = fields.Many2many("res.users", compute="_compute_queue_agents", readonly=True)
    active_customers = fields.Many2many("res.partner", compute="_compute_active_customers", readonly=True)
    
    name = fields.Char('Name', required=True)
    strategy = fields.Selection([('ring-all', 'Ring All'),
                                 ('longest-idle-agent', 'Longest Idle Agent'),
                                 ('round-robin', 'Round Robin'),
                                 ('top-down', 'Top Down'),
                                 ('agent-with-least-talk-time', 'Agent With Least Talk Time'),
                                 ('agent-with-lowest-calls', 'Rings the agent with fewest calls'),
                                 ('sequentially-by-agent-order', 'Rings agents sequentially by tier & order'),
                                 ('random', 'Rings agents in random orders'),
                                 ('ring-progressively', 'Rings agents in the same way as top-down, but keeping the previous members ringging(it basically leads to ring-all in the end)'),
                                 ], 'Strategy', default='round-robin')

    # the system will playback whatever you specify to incoming callers.
    moh_sound = fields.Char('Moh Sound', required=False)

    # record file $${base_dir}/recordings
    record_template = fields.Char('', required=False)

    # Add number of seconds to raising the caller's score.
    time_base_score = fields.Selection([('queue', 'Queue'), ('system', 'System')])

    # Can be True or False.
    # This defines if we should apply the following tier rules
    # when a caller advances through a queue's tiers.
    # If False, they will use all tiers with no wait.
    tier_rules_apply = fields.Boolean('Tier Rules Apply', default=False)

    # The time in seconds that a caller is required to wait before advancing to the next tier.
    # This will be multiplied by the tier level if tier-rule-wait-multiply-level is set to True.
    # If tier-rule-wait-multiply-level is set to false,
    # then after tier-rule-wait-second's have passed,
    # all tiers are open for calls in the tier-order
    # and no advancement (in terms of waiting) to another tier is made.
    tier_rule_wait_second = fields.Integer('Tier Rule Wait Second', default=10)

    # Can be True or False.
    # If False, then once tier-rule-wait-second is passed,
    # the caller is offered to all tiers in order (level/position).
    # If True, the tier-rule-wait-second will be multiplied by the tier level
    # and the caller will have to wait on every tier tier-rule-wait-second's before advancing
    # to the next tier.
    tier_rule_wait_multiple_level = fields.Boolean('Tier Rule Wait Multiple Level', default=False)

    # Can be True or False.
    # If True, callers will skip tiers that don't have agents available.
    # Otherwise, they are be required to wait before advancing.
    # Agents must be logged off to be considered not available.

    tier_rule_no_agent_no_wait = fields.Boolean('Tier Rule No Agent No Wait', default=True)
    
    # The number of seconds before we completely remove an abandoned member from the queue.
    # When used in conjunction with abandoned-resume-allowed,
    # callers can come back into a queue and resume their previous position.
    discard_abandoned_after = fields.Integer('Discard Abandoned After', default=600)

    # Can be True or False.
    # If True, a caller who has abandoned the queue
    # can re-enter and resume their previous position in that queue.
    # In order to maintain their position in the queue,
    # they must not abandoned it for longer than the number of seconds
    # defined in 'discard-abandoned-after'.
    abandoned_resume_allowed = fields.Boolean('Abandoned Resume Allowed', default=True)

    # Default to 0 to be disabled.
    # Any value are in seconds, and will define the delay before we quit the callcenter application IF the member haven't been answered by an agent.
    # Can be used for sending call in voicemail if wait time is too long.
    max_wait_time = fields.Integer('Max Wait Time', default=0)

    # Default to 0 to be disabled.
    # The value is in seconds, and it will define the amount of time
    # the queue has to be empty (without logged agents, on a call or not)
    # before we disconnect all members.
    # This principle protects kicking all members waiting
    # if all agents are logged off by accident.
    max_wait_time_with_no_agent = fields.Integer('Max Wait Time With No Agent', default=10)

    # Default to 5. Any value are in seconds,
    # and will define the length of time after the max-wait-time-with-no-agent is reached
    # to reject new caller.
    # This allow for kicking caller if no agent are logged in for over 5 seconds,
    # but new caller after that 5 seconds is reached can have a lower limit.
    max_wait_time_with_no_agent_time_reached = fields.Integer('Max wait time with no agent time reached', default=5)

    # Default to 10. The value is in seconds, and it will define the delay to wait before starting call to the next agent when using the 'ring-progressively' queue strategy.
    ring_progressively_delay = fields.Integer('Ring Progressively Delay', default=10)

    @api.depends("queue_tiers")
    def _compute_queue_agents(self):
        _logger.info(">>>>>>>_Compute queue agents")
        for record in self:
            if not record.queue_tiers:
                self.queue_agents = []
                return
            ids = map(lambda x: x.tier_agent_id.id, record.queue_tiers)
            if not _ids:
                self.queue_agents = []
                return
            self.queue_agents = [fields.Command.set(ids)]
        return

    @api.depends("queue_customers")
    def _compute_active_customers(self):
        for record in self:
            if not record.queue_customers:
                self.active_customers = []
                return
            customers = filter(lambda x: x.is_active, record.queue_customers)
            if not customers:
                self.active_customers = []
                return
            ids = map(lambda x: x.customer_id.id, customers)
            if not ids:
                self.active_customers = []
                return
            self.active_customers = [fields.Command.set(ids)]
        return
