odoo.define('web.node_hangup', function (require) {
    "use strict";

    var NodeAbstract = require('web.node_abstract');
    var NodeRegistry = require('web.node_registry');

    var NodeHangup = NodeAbstract.extend({
        node_path: function() {
            return ["SUCCESS"];
        },
        
        node_type: function() {
            return "node_hangup";
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

    NodeRegistry.add("node_hangup", new NodeHangup());
    
    return NodeHangup;
});

