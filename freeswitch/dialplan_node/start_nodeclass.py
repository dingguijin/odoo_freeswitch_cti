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

class start_NodeClass(AbstractNodeClass):

    async def execute_node(self, event):
        self.return_result_event("SUCCESS")
        
