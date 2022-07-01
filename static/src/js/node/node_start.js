odoo.define('web.node_start', function (require) {
    "use strict";

    var NodeAbstract = require('web.node_abstract');
    var NodeRegistry = require('web.node_registry');

    var NodeStart = NodeAbstract.extend({
        node_path: function() {
            return ["SUCCESS"];
        },        
        node_type: function() {
            return "node_start";
        },
        node_name: function() {
            return "Start Dialplan";
        },
        node_icon: function() {
            return "circle-o";
        }
    });

    NodeRegistry.add("node_start", new NodeStart());
    
    return NodeStart;
});

