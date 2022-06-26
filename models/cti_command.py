# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class CtiCommand(models.Model):

    _name = "freeswitch_cti.cti_command"
    _description = "Cti Command"

    name = fields.Char('Name', required=True)
    parameter = fields.Char('Parameter', required=False)

    #NEW/EXECUTE/CONFIRM
    status = fields.Char('Status', required=False)
    result = fields.Char('Result', required=False)
    
    execute_time = fields.Datetime('Execute Time', required=False)
    confirm_time = fields.Datetime('Confirm Time', required=False)
    
    @api.model
    def send_cti_command(self, command, parameter=""):
        self.create({
            "name": command,
            "parameter": parameter or "",
            "status": "NEW"
        })
        return
