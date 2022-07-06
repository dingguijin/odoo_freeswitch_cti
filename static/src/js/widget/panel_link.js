odoo.define('freeswitch_cti.panel_link', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');

    var QWeb = core.qweb;

    var PanelLink = Widget.extend({
        template: 'panel_link_template',
        events: {
        },

        init: function (parent, options) {
            this._super.apply(this, arguments);
            this.node = options.node;
            console.log("PanelLink options", options);
        },
        /**
         * Render attachment.
         *
         * @override
         */
        start: function () {
            var self = this;
            var nodes = [];
            
            _.each(this.node.operators, function (operator, operatorId) {
                if (operator.type == "start") {
                    return;
                }
                if (operatorId == self.node.node_id) {
                    return;
                }
                nodes.push({
                    id: operatorId,
                    text: operator.properties.title
                });
            });

            _.each(this.node.node_path, function (path) {
                var _id = "#o_flow_panel_node_select_" + path;
                // self.$(_id).select2({
                //     multiple: false,
                //     placeholder: "Next Node",
                //     allowClear: true,
                //     data: nodes,
                // });

                self.$(_id).append($('<option/>', {
                }));
                
                _.each(nodes, function(operator_node) {
                    self.$(_id).append($('<option/>', {
                        value:  operator_node.id,
                        text: operator_node.text
                    }));
                });
                
                // render link in right panel attributes             
                _.each(self.node.links, function (_link) {
                    if (_link.fromOperator == self.node.node_id && _link.fromConnector == path) {
                        self.$(_id).val(_link.toOperator).trigger("change");
                    }
                });

                self.$(_id).on("mousedown", function(ev) {
                    console.log("MOUSE DOWN ..............", self.$(_id).val());
                    self.previous_val = self.$(_id).val();
                });
                
                // register on change
                self.$(_id).on("change", function (ev) {
                    console.log("on changed", ev);
                    var _operator_id = self.$(_id).val();
                    console.log("on changed opid", _operator_id, self.previous_val);
                    if (self.previous_val == _operator_id) {
                        return;
                    }
                    if (self.previous_val) {
                        self.trigger_up("panel_remove_link", {
                            "from_operator_id": self.node.node_id,
                            "from_connector": path,
                            "to_operator_id": self.previous_val // this is link id
                        });
                    }

                    if (_operator_id) {
                        self.trigger_up("panel_create_link", {
                            "from_operator_id": self.node.node_id,
                            "from_connector": path,
                            "to_operator_id": _operator_id
                        });
                    }

                });

            });

            return this._super.apply(this, arguments);
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * On click ok.
         *
         * @private
         * @param {MouseEvent} ev
         */
        _onClickOk: function (ev) {
            ev.preventDefault();
        },

        _onClickCancel: function (ev) {
            ev.preventDefault();
        },

    });

    return PanelLink;
});
