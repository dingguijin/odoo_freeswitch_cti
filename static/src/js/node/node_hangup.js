odoo.define('freeswitch_cti.node_hangup', function (require) {
    "use strict";

    var NodeAbstract = require('freeswitch_cti.node_abstract');
    var NodeRegistry = require('freeswitch_cti.node_registry');

    var NodeHangup = NodeAbstract.extend({
        node_path: function() {
            return ["SUCCESS"];
        },
        
        node_type: function() {
            return "hangup";
        },
        node_name: function() {
            return "Hangup Telephone";
        },

        node_icon: function() {
            return "tty";
        },
        
        flow_types: function() {
            return ["incoming_call"];
        }
    });

    NodeRegistry.add("hangup", new NodeHangup());
    
    return NodeHangup;
});

