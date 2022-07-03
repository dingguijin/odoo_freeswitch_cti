odoo.define('freeswitch_cti.node_set', function (require) {
    "use strict";

    var NodeAbstract = require('freeswitch_cti.node_abstract');
    var NodeRegistry = require('freeswitch_cti.node_registry');

    var Node = NodeAbstract.extend({
        node_path: function() {
            return ["SUCCESS"];
        },
        
        node_type: function() {
            return "set";
        },
        node_name: function() {
            return "Set";
        },

        node_icon: function() {
            return "gear";
        },

        node_seq: function() {
            return 2;
        },

        node_params: function() {
            return [
                {
                    param_name: "variable",
                    param_display: "Variable",
                    param_type: "input"
                },

                {
                    param_name: "value",
                    param_display: "Value",
                    param_type: "input"
                }
            ];
        },
        
        flow_types: function() {
            return ["incoming_call"];
        }
    });

    NodeRegistry.add("set", new Node());
    
    return Node;
});

