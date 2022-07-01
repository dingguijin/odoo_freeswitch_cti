odoo.define('freeswitch_cti.DialplanController', function (require) {
    "use strict";

    var AbstractController = require('web.AbstractController');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var view_dialogs = require('web.view_dialogs');

    var _t = core._t;
    var QWeb = core.qweb;
    var FormViewDialog = view_dialogs.FormViewDialog;

    /**
     * Controller
     */
    var Controller = AbstractController.extend({
        custom_events: {
        },

        /**
         * @override
         * @param {Widget} parent
         * @param {Model} model
         * @param {Renderer} renderer
         * @param {Object} params
         */
        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
            this.currentId = params.currentId;
        },

        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------

        /**
         * Render the buttons according to the DialplanView.buttons template and add
         * listeners on it. Set this.$buttons with the produced jQuery element
         *
         * @param {jQuery} [$node] a jQuery node where the rendered buttons should
         *   be inserted $node may be undefined, in which case they are inserted
         *   into this.options.$buttons
         */
        renderButtons: function ($node) {
            this.$buttons = $('<div/>');
            this.$buttons.append(QWeb.render("DialplanView.buttons", {widget: this}));
            this.$buttons.on('click', '.o_flow_button_save', this._onSave.bind(this));
            this.$buttons.on('click', '.o_flow_button_cancel', this._onCancel.bind(this));
            this._updateButtons();
            this.$buttons.appendTo($node);
        },

        _updateButtons: function () {
        },

        _onSave: function() {
            var data = this.renderer.flowchartToState();
            this.model.save(data);
        },

        _onCancel: function() {
            var state = this.model.get();
            this.renderer.stateToFlowchart(state);
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------
        
    });

    return Controller;

});
