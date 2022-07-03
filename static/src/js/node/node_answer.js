odoo.define('freeswitch_cti.node_answer', function (require) {
    "use strict";

    var NodeAbstract = require('freeswitch_cti.node_abstract');
    var NodeRegistry = require('freeswitch_cti.node_registry');

    var NodeAnswer = NodeAbstract.extend({
        node_path: function() {
            return ["SUCCESS"];
        },
        
        node_type: function() {
            return "answer";
        },
        node_name: function() {
            return "Answer";
        },

        node_icon: function() {
            return "phone";
        },

        node_seq: function() {
            return 5;
        },
        
        flow_types: function() {
            return ["incoming_call"];
        }
    });

    NodeRegistry.add("answer", new NodeAnswer());
    
    return NodeAnswer;
});

