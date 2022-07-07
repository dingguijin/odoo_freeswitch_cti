# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 - ~.
# Guijin Ding, dingguijin@gmail.com.
# All rights reserved.
#
#

import logging

_logger = logging.getLogger(__name__)

from .abstract_nodeclass import AbstractNodeClass

class bridge_NodeClass(AbstractNodeClass):

    async def execute_node(self, event):
        _data = self.node_param.get("data")
        self.send_esl_execute("bridge", _data)
        return
        
