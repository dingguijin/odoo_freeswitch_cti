# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import asyncio
import logging
import time
import threading
import urllib

import odoo
from odoo.service.server import Worker
from odoo.service.server import PreforkServer

from . import freeswitch_inbound
from . import freeswitch_outbound

_logger = logging.getLogger(__name__)

def db_list():
    if odoo.tools.config['db_name']:
        db_names = odoo.tools.config['db_name'].split(',')
    else:
        db_names = odoo.service.db.list_dbs(True)
    return db_names

def worker():    
    old_process_spawn = PreforkServer.process_spawn
    def process_spawn(self):
        old_process_spawn(self)
        if not hasattr(self, "cti_inbound_workers"):
            self.cti_inbound_workers = {}
        if not hasattr(self, "cti_outbound_workers"):
            self.cti_outbound_workers = {}            
        if not self.cti_inbound_workers:
            self.worker_spawn(CTIInboundWorker, self.cti_inbound_workers)
        if not self.cti_outbound_workers:
            self.worker_spawn(CTIOutboundWorker, self.cti_outbound_workers)
    PreforkServer.process_spawn = process_spawn

class CTIWorker(Worker):
    def __init__(self, multi):
        super(CTIWorker, self).__init__(multi)
        self.threads = {}  # {db_name: thread}
        self.interval = 1

    def signal_handler(self, sig, frame):
        super().signal_handler(sig, frame)
        
    def start(self):
        super(CTIWorker, self).start()
        if self.multi and self.multi.socket:
            self.multi.socket.close()
        return

    def sleep(self):
        return

    def stop(self):
        super(CTIWorker, self).stop()
        for _thread in self.threads.values():
            _thread.stop()
            _thread.join()

    def process_work(self):
        # this called by run() in while self.alive cycle
        db_names = db_list()
        for dbname in db_names:
            if self.threads.get(dbname, False):
                continue
            _thread = self.get_cti_thread(dbname)
            _thread.start()
            self.threads[dbname] = _thread

    def get_cti_thread(dbname):
        pass

class CTIInboundWorker(CTIWorker):
    def get_cti_thread(self, dbname):
        return CTIInboundThread(dbname)

class CTIOutboundWorker(CTIWorker):
    def get_cti_thread(self, dbname):
        return CTIOutboundThread(dbname)

class CTIInboundThread(threading.Thread):
    """
    """

    def stop(self):
        _logger.info("stoping ..... CTIInboundThread")
        self.cti.stop()
        return

    def __init__(self, dbname):
        threading.Thread.__init__(self, name='CTIInboundThread')
        threading.current_thread().dbname = dbname
        self.daemon = True
        self.cti = freeswitch_inbound.FreeSwitchInbound(dbname)

    def run(self):
        _logger.info("CTIInboundThread start.")
        asyncio.run(self.cti.run_loop())
        _logger.info("CTIInboundThread stopped.")
        
class CTIOutboundThread(threading.Thread):
    """
    """

    def __init__(self, dbname):
        threading.Thread.__init__(self, name='CTIOutboundThread')
        threading.current_thread().dbname = dbname
        self.daemon = True
        self.cti = freeswitch_outbound.FreeSwitchOutbound(dbname)
        
    def run(self):
        _logger.info("CTIOutboundThread started.")            
        asyncio.run(self.cti.run_loop())
        _logger.info("CTIOutboundThread stopped.")            

    def stop(self):
        self.cti.stop()
        _logger.info("stoping ..... CTIOutboundThread")
        return


