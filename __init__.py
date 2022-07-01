# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import os
import signal

from . import controllers
from . import models
from . import worker

def post_load():
    worker.worker()
    return

def post_init_hook(cr, registry):
    os.kill(os.getpid(), signal.SIGINT)
    return
