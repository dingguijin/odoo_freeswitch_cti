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
    'depends': ['mail', 'odoo_freeswitch_xml_curl'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml'
    ],
    'assets': {
        'web.assets_qweb': [
        ],
        'web.assets_backend': [
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
