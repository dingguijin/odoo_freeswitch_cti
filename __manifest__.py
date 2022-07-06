# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'FreeSwitch CTI',
    'category': 'CallCenter',
    'summary': 'Odoo FreeSWITCH CTI',
    'version': '1.0',
    'description': """
        This module provides CTI connection with FreeSWITCH.
        """,
    'depends': ['mail', 'contacts'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/dialplan.xml',
        'data/freeswitch.xml'
    ],
    'assets': {
        'web.assets_qweb': [
            'odoo_freeswitch_cti/static/src/xml/*.xml'
        ],
        'web.assets_backend': [
            'odoo_freeswitch_cti/static/src/scss/dialplan_view.scss',
            
            'odoo_freeswitch_cti/static/lib/js/jquery.flowchart/jquery.flowchart.css',
            
            'odoo_freeswitch_cti/static/lib/js/jquery.panzoom/jquery.panzoom.js',
            'odoo_freeswitch_cti/static/lib/js/jquery.flowchart/jquery.flowchart.js',
            'odoo_freeswitch_cti/static/lib/js/html2canvas/html2canvas.js',

            'odoo_freeswitch_cti/static/src/js/node/*.js',
            'odoo_freeswitch_cti/static/src/js/widget/*.js',
            
            'odoo_freeswitch_cti/static/src/js/dialplan_model.js',
            'odoo_freeswitch_cti/static/src/js/dialplan_renderer.js',
            'odoo_freeswitch_cti/static/src/js/dialplan_controller.js',
            'odoo_freeswitch_cti/static/src/js/dialplan_view.js',
            'odoo_freeswitch_cti/static/src/js/dialplan_form.js',

            'odoo_freeswitch_cti/static/src/js/agent_list.js',
            'odoo_freeswitch_cti/static/src/js/queue_list.js',
            'odoo_freeswitch_cti/static/src/js/audio_url.js'
        ],
        'web.assets_frontend': [
        ],
        'web.tests_assets': [
        ],
        'web.qunit_mobile_suite_tests': [
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'post_load': 'post_load',
    'post_init_hook': 'post_init_hook'
}
