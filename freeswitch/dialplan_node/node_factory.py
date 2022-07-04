# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 - ~.
# Guijin Ding, dingguijin@gmail.com.
# All rights reserved.
#
# nodefactory.py 
# NodeFactory build node instance
#

import logging
import importlib

_logger = logging.getLogger(__name__)

class NodeFactory():
    @classmethod
    def build(cls, event):
        _node = event.get("node")
        _node_class_name = "%s_NodeClass" % _node.get("node_type")
        _node_module_name = _node_class_name.lower()
        _module = importlib.import_module(_node_module_name)
        if not _module:
            _logger.error("no node module for %s" % _node.get("node_type"))
            return None

        _node_class = getattr(_module, _node_class_name)
        if not _node_class:
            _logger.error("no node class for %s" % _node.get("node_type"))
            return None

        _logger.info("node class loaded: %s" % _node_class_name)
        return _node_class(event)
