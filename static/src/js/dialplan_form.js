/** @odoo-module **/

import { _t } from 'web.core';
import FormController from 'web.FormController';
import FormView from 'web.FormView';
import viewRegistry from 'web.view_registry';

const DialplanFormController = FormController.extend({
    custom_events: _.extend({}, FormController.prototype.custom_events, {
        switch_view: '_onSwitchView',
    }),

    init: function() {
        this._super.apply(this, arguments);
    },

    _onSwitchView: function (ev) {   
        this._super.apply(this, arguments);
        ev.data.res_id = this.getState().id;
    },
});

export const DialplanFormView = FormView.extend({
    config: _.extend({}, FormView.prototype.config, {
        Controller: DialplanFormController
    }),
});

viewRegistry.add('dialplan_form', DialplanFormView);
