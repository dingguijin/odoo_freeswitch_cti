odoo.define('freeswitch_cti.node_bridge', function (require) {
    "use strict";

    var NodeAbstract = require('freeswitch_cti.node_abstract');
    var NodeRegistry = require('freeswitch_cti.node_registry');

    var Node = NodeAbstract.extend({
        node_path: function() {
            return ["SUCCESS"];
        },
        
        node_type: function() {
            return "bridge";
        },
        node_name: function() {
            return "Bridge";
        },

        node_icon: function() {
            return "exchange";
        },

        node_seq: function() {
            return 5;
        },

        flow_types: function() {
            return ["incoming_call"];
        }
    });

    NodeRegistry.add("bridge", new Node());
    
    return Node;
});

