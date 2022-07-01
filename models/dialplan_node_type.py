# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

_NODE_TYPES = [
    {
        "type": "start",
        "name": "Start",
    },

    {
        "type": "exit",
        "name": "Exit",
    },

    {
        "type": "playback",
        "name": "Playback",
    },

    {
        "type": "bridge",
        "name": "Bridge",
    },

    {
        "type": "answer",
        "name": "Answer",
    },
    {
        "type": "hangup",
        "name": "Hangup",
    },

]

def get_node_types():
    return _NODE_TYPES
