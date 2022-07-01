odoo.define('web.node_exit', function (require) {
    "use strict";

    var NodeAbstract = require('web.node_abstract');
    var NodeRegistry = require('web.node_registry');

    var NodeExit = NodeAbstract.extend({
        node_type: function() {
            return "node_exit";
        },
        node_name: function() {
            return "Exit Flow";
        },
        node_icon: function() {
            return "stop-circle-o";
        },
    });

    NodeRegistry.add("node_exit", new NodeExit());
    
    return NodeExit;
});

