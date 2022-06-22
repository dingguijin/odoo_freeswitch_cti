# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import http

_logger = logging.getLogger(__name__)

class Main(http.Controller):

    @http.route('/web/cti_command/<string:command>', type='json', auth="user")
    def cti_command(self, command):
        return
