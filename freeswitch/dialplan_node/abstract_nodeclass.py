# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 - ~.
# Guijin Ding, dingguijin@gmail.com.
# All rights reserved.
#
#

import json
import logging

_logger = logging.getLogger(__name__)

class AbastractNodeClass():
    def __init__(self, event):
        self.stream = event.get("stream")
        self.event = event.get("event")
        self.node = event.get("node")

        self.node_param = node.get("node_param") or "{}"
        self.node_param = json.loads(self.node_param)
        return

    def execute_node(self, event):
        pass

    def return_result_event(self, result):
        self.stream.server.push_node_event(self.stream, self.node, result)
        return

    def send_esl_execute(self, app, arg=""):
        self.stream._send_esl_execute(app, arg)
        return
