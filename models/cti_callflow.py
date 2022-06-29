# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class CtiCallFlow(models.Model):

    _name = "freeswitch_cti.cti_callflow"
    _description = "Cti CallFlow"

    # same with profile_index
    name = fields.Char('Name', compute="_compute_name")
    profile_index = fields.Integer('Profile Index')
    
    caller_profile_username = fields.Char("Username")
    caller_profile_caller_id_name = fields.Char("Caller ID Name")
    caller_profile_caller_id_number = fields.Char("Caller ID Number")
    caller_profile_network_addr = fields.Char("Network Addr")
    caller_profile_destination_number = fields.Char("Destination Number")
    caller_profile_uuid = fields.Char("UUID")
    caller_profile_chan_name = fields.Char("Chan Name")
    
    times_created_time = fields.Datetime("Created Time")
    times_profile_created_time = fields.Datetime("Profile Created Time")
    times_progress_time = fields.Datetime("Progress Time")
    times_progress_media_time = fields.Datetime("Progress Media Time")
    times_answered_time = fields.Datetime("Answered Time")
    times_bridged_time = fields.Datetime("Bridged Time")
    times_last_hold_name = fields.Datetime("Last Hold Time")
    times_hold_accum_time = fields.Datetime("Hold Accum Time")
    times_hangup_time = fields.Datetime("Hangup Time")
    times_resurrect_time = fields.Datetime("Resurrect Time")
    times_transfer_time = fields.Datetime("Transfer Time")

    @depends("profile_index")
    def _compute_name(self):
        for record in self:
            record.name = "callflow_%d" % record.profile_index
        return

    

