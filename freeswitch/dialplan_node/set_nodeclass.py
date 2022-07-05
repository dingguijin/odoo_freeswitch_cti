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

from abastract_nodeclass import AbstractNodeClass

class answer_NodeClass(AbstractNodeClass):

    def execute_node(self, event):
        _variable = self.node_param.get("variable")
        _value = self.node_param.get("value")
        self.send_esl_execute("set", "%s=%s" % (_variable, _value)))
        self.return_result_event("SUCCESS")
        return
        
