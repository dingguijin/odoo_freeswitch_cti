odoo.define('freeswitch_cti.node_exit', function (require) {
    "use strict";

    var NodeAbstract = require('freeswitch_cti.node_abstract');
    var NodeRegistry = require('freeswitch_cti.node_registry');

    var NodeExit = NodeAbstract.extend({
        node_type: function() {
            return "exit";
        },
        node_name: function() {
            return "Exit Dialplan";
        },
        node_icon: function() {
            return "stop-circle-o";
        },
    });

    NodeRegistry.add("exit", new NodeExit());
    
    return NodeExit;
});

