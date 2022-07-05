odoo.define('freeswitch_cti.node_playback', function (require) {
    "use strict";

    var NodeAbstract = require('freeswitch_cti.node_abstract');
    var NodeRegistry = require('freeswitch_cti.node_registry');

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
            return "playback";
        },

        node_name: function() {
            return "Playback";
        },

        node_icon: function() {
            return "play-circle-o";
        },

        node_params: function() {
            return [
                {
                    param_name: "data",
                    param_display: "Data",
                    param_type: "input"
                }
            ];
        },

        node_seq: function() {
            return 5;
        },

        flow_types: function() {
            return ["incoming_call"];
        }
    });

    NodeRegistry.add("playback", new NodePlayback());
    
    return NodePlayback;
});

