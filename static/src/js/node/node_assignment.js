odoo.define('web.node_assignment', function (require) {
    "use strict";

    var NodeAbstract = require('web.node_abstract');
    var NodeRegistry = require('web.node_registry');

    var NodeAssignment = NodeAbstract.extend({
        node_path: function() {
            return ["SUCCESS"];
        },
        
        node_type: function() {
            return "node_assignment";
        },
        node_name: function() {
            return "Assign Agent";
        },

        node_icon: function() {
            return "user-circle";
        },
        
        flow_types: function() {
            return ["incoming_call"];
        }
    });

    NodeRegistry.add("node_assignment", new NodeAssignment());
    
    return NodeAssignment;
});

