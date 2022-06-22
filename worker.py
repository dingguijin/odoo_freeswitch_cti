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

from . import freeswitch_client

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
        if not hasattr(self, "cti_command_workers"):
            self.cti_command_workers = {}
        if not hasattr(self, "cti_notification_workers"):
            self.cti_notification_workers = {}            
        if not self.cti_command_workers:
            self.worker_spawn(CTICommandWorker, self.cti_command_workers)
        # if not self.cti_notification_workers:
        #     self.worker_spawn(CTINotificationWorker, self.cti_notification_workers)
    PreforkServer.process_spawn = process_spawn

class CTIWorker(Worker):
    def __init__(self, multi):
        super(CTIWorker, self).__init__(multi)
        self.threads = {}  # {db_name: thread}
        self.interval = 1

    def signal_handler(self, sig, frame):
        super().signal_handler(sig, frame)
        #_logger.info(">>>>>>>>>>>>>>>>>>>CTIWORKER RECEIVE SIGNAL %s", self.alive)
        
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
                
        time.sleep(self.interval)

    def get_cti_thread(dbname):
        pass

class CTICommandWorker(CTIWorker):
    def get_cti_thread(self, dbname):
        return CTICommandThread(dbname)

class CTINotificationWorker(CTIWorker):
    def get_cti_thread(self, dbname):
        return CTINotificationThread(dbname)

class CTICommandThread(threading.Thread):
    """
    """

    def stop(self):
        _logger.info("stoping ..... CTICommandThread")
        self.is_stop = True
        return

    def __init__(self, dbname):
        threading.Thread.__init__(self, name='CTICommandThread')
        threading.current_thread().dbname = dbname
        
        self.daemon = True
        self.dbname = dbname
        self.is_stop = False

        self.cti_client = freeswitch_client.FreeSwitchClient(self.dbname)

    def run(self):
        _logger.info("CTICommandThread run.")

        while True:
            if self.is_stop:
                self.cti_client.stop()
                break

            asyncio.run(self.cti_client.run_loop())

            _logger.info("IN CTICOMMANDTHREAD")
            time.sleep(1)

    def dispatch_cti_commands(self, commands):
        return


class CTINotificationThread(threading.Thread):
    """
    """

    def __init__(self, dbname):
        threading.Thread.__init__(self, name='CTINotificationThread')
        threading.current_thread().dbname = dbname

        self.daemon = True
        self.dbname = dbname
        self.is_stop = False
        
    def run(self):
        _logger.info("CTINotificationThread started.")

        # self.db = odoo.sql_db.db_connect(self.dbname)
        # with db.cursor() as cr:
            
        while True:
            if self.is_stop:
                break
            
            _logger.info("IN CTINOTIFICATIONTHREAD")
            time.sleep(10)

    def stop(self):
        self.is_stop = True
        _logger.info("stoping ..... CTINotificationThread")
        return


