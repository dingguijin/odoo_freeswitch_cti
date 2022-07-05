odoo.define('freeswitch_cti.node_app', function (require) {
    "use strict";

    var NodeAbstract = require('freeswitch_cti.node_abstract');
    var NodeRegistry = require('freeswitch_cti.node_registry');

    var Node = NodeAbstract.extend({
        node_path: function() {
            return ["SUCCESS"];
        },
        
        node_type: function() {
            return "app";
        },
        node_name: function() {
            return "App";
        },

        node_icon: function() {
            return "th";
        },

        node_seq: function() {
            return 2;
        },

        node_params: function() {
            return [
                {
                    param_name: "app",
                    param_display: "Application",
                    param_type: "input"
                },

                {
                    param_name: "data",
                    param_display: "Data",
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

