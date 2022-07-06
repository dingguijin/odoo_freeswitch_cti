odoo.define('freeswitch_cti.DialplanModel', function (require) {
    "use strict";

    var AbstractModel = require('web.AbstractModel');

    /**
     * Model
     */
    var Model = AbstractModel.extend({
        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------

        /**
         * @override
         * @returns {Object}
         */
        get: function () {
            return $.extend(true, {}, {
                res_id: this.res_id,
                dialplan: this.dialplan,
                nodes: this.nodes,
                events: this.events
            });
        },
        
        /**
         * @override
         * @param {Object} params
         * @returns {Promise}
         */
        load: function (params) {
            this.res_id = params.res_id;
            return this._fetchInfo();
        },
        
        reload: function(_, params) {
            this.res_id = params.currentId;
            return this._fetchInfo();
        },

        save: function(data) {
            this._updateInfo(data);
        },

        getName: function() {
            if (this.dialplan) {
                return this.dialplan.name;
            }
            return "";
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * @private
         * @param {any} record
         * @returns {Promise}
         */
        _fetchInfo: function () {
            var self = this;
            return this._rpc({
                route: '/freeswitch_cti/dialplan/get_info',
                params: {
                    id: self.res_id
                },
            }).then(function (data) {
                self.nodes = data.nodes;
                self.dialplan = data.dialplan;
                self.events = data.events;
                console.log("dialplan/get_info ", data);
            });
        },

        _updateInfo: function(data) {
            var self = this;
            return this._rpc({
                route: '/freeswitch_cti/dialplan/update_info',
                params: {
                    id: self.res_id,
                    nodes: data.nodes,
                    events: data.events
                },
            }).then(function(res) {
                self.nodes = res.nodes;
                self.events = res.events;
            });
        },

    });

    return Model;
});
