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
        'data/freeswitch.xml'
    ],
    'assets': {
        'web.assets_qweb': [
        ],
        'web.assets_backend': [
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
}
