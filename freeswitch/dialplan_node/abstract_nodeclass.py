# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 - ~.
# Guijin Ding, dingguijin@gmail.com.
# All rights reserved.
#
#

import logging

_logger = logging.getLogger(__name__)

class AbastractNodeClass():
    def __init__(self, event):
        self.stream = event.get("stream")
        self.event = event.get("event")
        self.node = event.get("node")
        return

    def execute_node(self, event):
        return

    def return_result_event(self, result):
        self.stream.server.push_node_event(self.stream, self.node, result)
        return

