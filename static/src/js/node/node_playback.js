odoo.define('web.node_playback', function (require) {
    "use strict";

    var NodeAbstract = require('web.node_abstract');
    var NodeRegistry = require('web.node_registry');

    var NodePlayback = NodeAbstract.extend({
        node_path: function() {
            return [
                "FAILED",
                "PLAYBACK_END",
                "PLAYBACK_BREAK",
                "ASR_FAILED",
                "TIMEOUT",
                "HANGUP",
                "UNKNOWN",
                
                "INPUT_0",
                "INPUT_1",
                "INPUT_2",
                "INPUT_3",
                "INPUT_4",
                "INPUT_5",
                "INPUT_6",
                "INPUT_7",
                "INPUT_8",
                "INPUT_9",

                "INPUT_SHARP",
                "INPUT_ASTERISK"
            ];
        },

        node_type: function() {
            return "node_playback";
        },

        node_name: function() {
            return "Playback";
        },

        node_icon: function() {
            return "play-circle-o";
        },

        flow_types: function() {
            return ["incoming_call"];
        }
    });

    NodeRegistry.add("node_playback", new NodePlayback());
    
    return NodePlayback;
});
