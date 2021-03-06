odoo.define('freeswitch_cti.node_assignment', function (require) {
    "use strict";

    var NodeAbstract = require('freeswitch_cti.node_abstract');
    var NodeRegistry = require('freeswitch_cti.node_registry');

    var NodeAssignment = NodeAbstract.extend({
        node_path: function() {
            return ["SUCCESS"];
        },
        
        node_type: function() {
            return "assignment";
        },
        node_name: function() {
            return "Assign Agent";
        },

        node_icon: function() {
            return "user-circle";
        },

        node_seq: function() {
            return 6;
        },

        flow_types: function() {
            return ["incoming_call"];
        }
    });

    NodeRegistry.add("assignment", new NodeAssignment());
    
    return NodeAssignment;
});

