odoo.define('freeswitch_cti.node_start', function (require) {
    "use strict";

    var NodeAbstract = require('freeswitch_cti.node_abstract');
    var NodeRegistry = require('freeswitch_cti.node_registry');

    var NodeStart = NodeAbstract.extend({
        node_path: function() {
            return ["SUCCESS"];
        },        
        node_type: function() {
            return "start";
        },
        node_name: function() {
            return "Start Dialplan";
        },
        node_icon: function() {
            return "circle-o";
        },
        node_seq: function() {
            return 0;
        }
    });

    NodeRegistry.add("start", new NodeStart());
    
    return NodeStart;
});

