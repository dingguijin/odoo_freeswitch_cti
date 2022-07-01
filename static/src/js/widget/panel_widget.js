odoo.define('freeswitch_cti.panel_widget', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var NodeRegistry = require("web.node_registry");

    var QWeb = core.qweb;

    var PanelWidget = Widget.extend({
        template: 'panel_widget_template',
        events: {
        },
        /**  
         * PanelWidget options {operator: operator}
         * @constructor
         * @override
         * @param {Widget} parent
         * @param {Array<Object>} attachments list of attachments
         */
        init: function (parent, options) {
            this._super.apply(this, arguments);
            console.log("init panel widget", options);
            this.node = options.node;
        },
        /**
         * Render attachment.
         *
         * @override
         */
        start: function () {
            this._renderWidget();
            return this._super.apply(this, arguments);
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        _renderWidget: function() {
            if (!this.node) {
                return;
            }
            console.log("renderWidget ....", this.node);
            var node_class = NodeRegistry.get(this.node.node_type);
            node_class.node_panel(this, this.node);
        },
        
        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        
    });

    return PanelWidget;
});
