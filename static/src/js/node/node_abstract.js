odoo.define('freeswitch_cti.node_abstract', function (require) {
    "use strict";

    var Class = require("web.Class");
    var PanelInput = require("freeswitch_cti.panel_input");
    var PanelLink = require("freeswitch_cti.panel_link");
    var PanelParams = require("freeswitch_cti.panel_params");
    
    var NodeAbstract = Class.extend({

        node_path: function() {
            return [];
        },

        node_panel: function(widget, node) {
            this.node_panel_head(widget, node);
            this.node_panel_name(widget, node);
            this.node_panel_parameters(widget, node);
            this.node_panel_path(widget, node);
        },
        
        node_panel_head: function(widget, node) {
        },
        
        node_panel_name: function(widget, node) {
            var self = this;
            var panel_input_widget = new PanelInput(widget, {
                input: {
                    label: "Node Name",
                    name: "node_name",
                    value: node.operator.properties.title,
                    save: function(value, input) {
                        widget.trigger_up("panel_change_operator_title", {
                            "operator_id": node.node_id,
                            "title": value
                        });
                    }
                }
            });
            panel_input_widget.appendTo(widget.el);
        },

        node_panel_path: function(widget, node) {
            var panel_link_widget = new PanelLink(widget, {
                node: node
            });
            panel_link_widget.appendTo(widget.el);            
        },

        node_panel_parameters: function(widget, node) {
            var params = this.node_params(node);
            if (!params) {
                return;
            }

            // load node parameter
            if (node.node_param != undefined) {
                var node_params = JSON.parse(node.node_param || "{}");
                _.each(params, function(param) {
                    if (node_params[param.param_name] != undefined) {
                        param.param_value = node_params[param.param_name];
                    }
                });
            }
            
            var panel_params_widget = new PanelParams(widget, {params: params, node: node});
            panel_params_widget.appendTo(widget.el);
        },

        node_params: function() {
            return null;
        },
        
        node_type: function() {
            return null;
        },

        node_name: function() {
            return null;
        },

        node_icon: function() {
            return null;
        },

        node_seq: function() {
            return 9999;
        },
        
        flow_types: function() {
            return null;
        },
        
    });

    return NodeAbstract;
});

