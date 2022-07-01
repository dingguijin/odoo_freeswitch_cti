odoo.define('freeswitch_cti.DialplanView', function (require) {
    "use strict";

    var BasicView = require('web.BasicView');
    var AbstractView = require('web.AbstractView');
    var core = require('web.core');
    var Model = require('freeswitch_cti.DialplanModel');
    var Renderer = require('freeswitch_cti.DialplanRenderer');
    var Controller = require('freeswitch_cti.DialplanController');

    var view_registry = require('web.view_registry');
    var _lt = core._lt;

    /**
     * Dialplan View
     */
    var DialplanView = AbstractView.extend({
        display_name: _lt('Dialplan'),
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

    view_registry.add('dialplan', DialplanView);
    return DialplanView;

});
