odoo.define('freeswitch_cti.panel_params', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');

    var QWeb = core.qweb;

    var PanelInput = require('freeswitch_cti.panel_input');

    var PanelParams = Widget.extend({
        template: 'panel_params_template',
        events: {
        },

        init: function (parent, options) {
            this._super.apply(this, arguments);
            this.params = options.params;
            console.log("PanelParams options", options);
        },
        /**
         * Render params.
         *
         * @override
         */
        start: function () {
            var self = this;
            _.each(this.params, function(param) {
                if (param.param_type == "input") {
                    var _param_el = new PanelInput(self, {
                        hide_buttons: true,
                        input: {
                            label: param.param_display,
                            name: param.param_name,
                            value: param.param_value,
                            save: function(value, input) {
                                param.param_value = value;
                                self.trigger_up("panel_change_operator_param", {
                                    "operator_id": param.operator_id,
                                    "param": param
                                });
                            }
                        }
                    });
                    console.log("appending ......");
                    _param_el.appendTo(self.$(".o_flow_panel_params_params")[0]);
                }                
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

    return PanelParams;
});
