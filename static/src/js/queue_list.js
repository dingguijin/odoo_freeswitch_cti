/** @odoo-module **/

import { _t } from 'web.core';
import ListController from 'web.ListController';
import ListView from 'web.ListView';
import viewRegistry from 'web.view_registry';

const AgentListController = ListController.extend({
    init: function() {
        this._super.apply(this, arguments);
        owl.Component.env.services.bus_service.onNotification(this, (notifications) => {
            console.log(">>>>>>>>>>>>>>> GET notifications", notifications);
		    for (const { payload, type } of notifications) {

                if (type == "queue_update") {
                    
                    this.trigger_up("reload");
                }
            }
        });
    }
});

export const AgentListView = ListView.extend({
    config: Object.assign({}, ListView.prototype.config, {
        Controller: AgentListController,
    }),
});

viewRegistry.add('agent_list', AgentListView);
