odoo.define('freeswitch_cti.panel_input', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');

    var QWeb = core.qweb;

    var PanelInput = Widget.extend({
        template: 'panel_input_template',
        events: {
            'click .o_flow_panel_card_input_button_ok': '_onClickOk',
            'click .o_flow_panel_card_input_button_cancel': '_onClickCancel',
        },
        /**  
         * PanelInput options {input: input}
         * @constructor
         * @override
         * @param {Widget} parent
         * @param {input: input}
         */
        init: function (parent, options) {
            this._super.apply(this, arguments);
            this.input = options.input;
            this.hide_buttons = options.hide_buttons || false;
            console.log("PanelInput options", options);
        },
        /**
         * Render attachment.
         *
         * @override
         */
        start: function () {
            return this._super.apply(this, arguments);
        },

        // for params load and save
        get_widget_value: function() {
            return this.$el.find("input[name='" + this.input.name + "']").val();
        },

        set_widget_value: function(v) {
            this.$el.find("input[name='" + this.input.name + "']").val(v);
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
            var v = this.$el.find("input[name='" + this.input.name + "']").val();
            if (this.input.save && v != this.input.value) {
                this.input.save(v, this.input, this);
                this.input.value = v;
            }
        },

        _onClickCancel: function (ev) {
            ev.preventDefault();
            this.$el.find("input[name='" + this.input.name + "']").val(this.input.value);
        },
        
    });

    return PanelInput;
});
