odoo.define('freeswitch_cti.DialplanView', function (require) {
    "use strict";

    var Model = require('freeswitch_cti.DialplanModel');
    var Renderer = require('freeswitch_cti.DialplanRenderer');
    var Controller = require('freeswitch_cti.DialplanController');

    var AbstractView = require('web.AbstractView');
    var viewRegistry = require('web.view_registry');

    /**
     * Dialplan View
     */
    var DialplanView = AbstractView.extend({
        display_name: 'Dialplan',
        icon: 'fa-code-fork',
        multi_record: false,
        withSearchBar: false,
        searchMenuTypes: [],
        jsLibs: [[]],
        config: _.extend({}, AbstractView.prototype.config, {
            Model: Model,
            Renderer: Renderer,
            Controller: Controller,
        }),
        
        viewType: 'dialplan',

        /**
         * @override
         * @param {Object} viewInfo
         * @param {Object} params
         */
        init: function (viewInfo, params) {
            this._super.apply(this, arguments);
        },

    });

    viewRegistry.add('dialplan', DialplanView);
    return DialplanView;

});
