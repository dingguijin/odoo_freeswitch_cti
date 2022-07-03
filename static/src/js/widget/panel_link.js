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
            var nodes = [];
            _.each(this.node.operators, function (operator, operatorId) {
                if (operator.type == "start") {
                    return;
                }
                nodes.push({
                    id: operatorId,
                    text: operator.properties.title
                });
            });

            var self = this;
            _.each(this.node.node_path, function (path) {
                var _id = "#o_flow_panel_node_select_" + path;
                // self.$(_id).select2({
                //     multiple: false,
                //     placeholder: "Next Node",
                //     allowClear: true,
                //     data: nodes,
                // });

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

                // register on change
                self.$(_id).on("change", function (ev) {
                    console.log("changed", arguments);
                    var _operator_id = self.$(_id).val();

                    if (ev.removed) {
                        self.trigger_up("panel_remove_link", {
                            "from_operator_id": self.node.node_id,
                            "from_connector": path,
                            "to_operator_id": ev.removed.id // this is link id
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
