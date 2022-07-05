# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 - ~.
# Guijin Ding, dingguijin@gmail.com.
# All rights reserved.
#
#

import logging

_logger = logging.getLogger(__name__)

from abastract_nodeclass import AbstractNodeClass

class answer_NodeClass(AbstractNodeClass):

    def execute_node(self, event):
        self.send_esl_execute("answer")
        self.return_result_event("SUCCESS")
        return
        
