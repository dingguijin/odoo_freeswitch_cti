odoo.define('freeswitch_cti.DialplanRenderer', function (require) {
    "use strict";

    var AbstractRenderer = require('web.AbstractRenderer');
    var NodeRegistry = require('freeswitch_cti.node_registry');
    var PanelWidget = require("freeswitch_cti.panel_widget");

    /**
     * Flow Renderer
     *
     */

    var createUUID = (function (uuidRegEx, uuidReplacer) {
        return function () {
            return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(uuidRegEx, uuidReplacer).toUpperCase();
        };
    })(/[xy]/g, function (c) {
        var r = Math.random() * 16 | 0,
            v = c == "x" ? r : (r & 3 | 8);
        return v.toString(16);
    });

    var Renderer = AbstractRenderer.extend({
        className: 'o_flow_view',

        custom_events: {
            "panel_create_link": '_onPanelCreateLink',
            "panel_remove_link": '_onPanelRemoveLink',
            "panel_change_operator_title": "_onPanelChangeOperatorTitle"
        },

        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            this.isInDom = false;
            this.flowIsInit = false;
            this.$flowchart = null;
            this.$flowcontainer = null;
            this.$operatorOverlay = null;

            this.$toolbar = null;
            this.$panel = null;
            this.$zoom = null;

            this.tempPos = null;
            this.tempSeq = null;

            this.isZoomRendering = false;
            this.isZoomPending = false;

            this.originFlowCanvas = null;
        },

        /**
         * @override
         * @returns {Promise}
         */
        start: function () {
            return this._super.apply(this, arguments).then(function () {
            });
        },

        /*
         * Called each time the renderer is attached into the DOM.
         */
        on_attach_callback: function () {
            console.log("on attach callback");

            this.isInDom = true;
            this._initializeFlow();

            this._renderToolbar();
            this._renderPanel();
            this._renderFlowChart();
            this._renderZoom();

            this.stateToFlowchart();
        },

        /*
         *called each time the renderer is detached from the DOM.
         */
        on_detach_callback: function () {
            this.isInDom = false;
        },

        /**
         * @override
         * manually destroys the handlers to avoid memory leaks
         * destroys manually the map
         */
        destroy: function () {
            return this._super.apply(this, arguments);
        },

        flowchartToState: function () {
            var _nodes = [];
            var _events = [];

            var data = this.$flowchart.flowchart("getData");
            _.each(data.operators, function (operator, operatorId) {
                var _node = {
                    node_timeout: operator.properties.node.node_timeout,
                    node_param: operator.properties.node.node_param,
                    node_type: operator.type,
                    node_id: operatorId,
                    name: operator.properties.title,
                    display_top: operator.top,
                    display_left: operator.left
                };
                _nodes.push(_node);
            });

            _.each(data.links, function (link) {
                var _event = {
                    name: link.fromConnector,
                    node_id: link.fromOperator,
                    next_node: link.toOperator,
                };
                _events.push(_event);
            });

            return { events: _events, nodes: _nodes };
        },

        stateToFlowchart: function (state) {
            var data = this._convertStateToFlowchartData(state);
            this.$flowchart.flowchart("setData", data);
            this._rerenderZoom();
            this._renderNoItemPanel();
        },

        _convertStateToFlowchartData: function (state) {
            var _operators = {};
            var _links = {};
            var _state = state;
            if (!_state) {
                _state = this.state;
            }

            _.each(_state.nodes, function (node) {
                var _node_class = NodeRegistry.get(node.node_type);
                var _operator = {
                    type: node.node_type,
                    top: node.display_top,
                    left: node.display_left,
                    properties: {
                        "node": {
                            node_id: node.id,
                            node_type: node.node_type,
                            node_path: _node_class.node_path(),
                        },
                        "class": "o_operator_icon o_operator_icon_" + _node_class.node_icon(),
                        title: node.name,
                        body: " ",
                        inputs: {},
                        outputs: {}
                    }
                };
                _operators[node.id] = _operator;
            });

            _.each(_state.events, function (event) {
                var _fromOperatorId = event.node_id[0];
                var _toOperatorId = event.next_node[0];

                if (!_operators[_fromOperatorId] || !_operators[_toOperatorId]) {
                    console.log("no operator event", event);
                    return;
                }

                var _linkId = _fromOperatorId + "." + event.name + "." + _toOperatorId;
                var _link = {
                    fromOperator: _fromOperatorId,
                    fromConnector: event.name,
                    toOperator: _toOperatorId,
                    toConnector: _linkId
                };
                _links[_linkId] = _link;

                // FIXME: translate the event.name
                _operators[_fromOperatorId].properties.outputs[event.name] = {
                    label: event.name,
                    multiple: false,
                    multipleLinks: false
                };
                _operators[_toOperatorId].properties.inputs[_linkId] = {
                    label: event.name,
                    multiple: false,
                    multipleLinks: false
                };
            });

            return { links: _links, operators: _operators };
        },

        _onPanelChangeOperatorTitle: function (event) {
            this.$flowchart.flowchart("setOperatorTitle", event.data.operator_id, event.data.title);
        },

        _onPanelCreateLink: function (event) {
            var fromOperator = this.$flowchart.flowchart("getOperatorData", event.data.from_operator_id);
            var toOperator = this.$flowchart.flowchart("getOperatorData", event.data.to_operator_id);

            var fromOperatorId = event.data.from_operator_id;
            var toOperatorId = event.data.to_operator_id;

            var toConnectorId = event.data.from_operator_id + "." + event.data.from_connector + "." + toOperatorId;
            var fromConnectorId = event.data.from_connector;

            fromOperator.properties.outputs[fromConnectorId] = {
                label: fromConnectorId,
                multiple: false,
                multipleLinks: false
            };

            toOperator.properties.inputs[toConnectorId] = {
                label: fromConnectorId,
                multiple: false,
                multipleLinks: false
            };

            this.$flowchart.flowchart("setOperatorData", fromOperatorId, fromOperator);
            this.$flowchart.flowchart("setOperatorData", toOperatorId, toOperator);

            var link = {
                fromOperator: fromOperatorId,
                fromConnector: fromConnectorId,
                toOperator: toOperatorId,
                toConnector: toConnectorId,
            };
            var linkId = toConnectorId;
            this.$flowchart.flowchart("createLink", linkId, link);
        },

        _onPanelRemoveLink: function (event) {
            var fromOperatorId = event.data.from_operator_id;
            var toOperatorId = event.data.to_operator_id;
            var fromConnector = event.data.from_connector;
            this._removeLink(fromOperatorId, toOperatorId, fromConnector);
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        _removeLink: function (fromOperatorId, toOperatorId, fromConnector) {
            var fromOperator = this.$flowchart.flowchart("getOperatorData", fromOperatorId);
            var toOperator = this.$flowchart.flowchart("getOperatorData", toOperatorId);

            // TO CONNECTOR 和 LINKID 一样
            // TO CONNECTOR = FROM OPERATOR ID . FROM CONNECTOR . TO OPERATOR ID
            var toConnector = fromOperatorId + "." + fromConnector + "." + toOperatorId;

            var linkId = toConnector;
            this.$flowchart.flowchart("deleteLink", linkId);

            delete fromOperator.properties.outputs[fromConnector];
            delete toOperator.properties.inputs[toConnector];

            this.$flowchart.flowchart("setOperatorData", fromOperatorId, fromOperator);
            this.$flowchart.flowchart("setOperatorData", toOperatorId, toOperator);
        },

        /**
         * @override
         * @returns {Promise}
         */
        _render: function () {
            return this._super.apply(this, arguments);
        },

        _initializeFlow: function () {
            if (this.flowIsInit) {
                return;
            }
            this.flowIsInit = true;
            var self = this;

            var flowContainer = document.createElement("div");
            var flowChart = document.createElement("div");
            var toolbarContainer = document.createElement("div");
            var toolbar = document.createElement("div");
            var panelContainer = document.createElement("div");
            var panel = document.createElement("div");

            var zoomContainer = document.createElement("div");
            var zoom = document.createElement("div");
            var right = document.createElement("div");
            var viewPointMask = document.createElement("div");

            toolbarContainer.classList.add('o_flow_toolbar_container');
            toolbar.classList.add('o_flow_toolbar');
            toolbarContainer.appendChild(toolbar);
            this.el.appendChild(toolbarContainer);

            flowContainer.classList.add('o_flow_container');
            flowChart.classList.add('o_flow_chart');
            flowContainer.appendChild(flowChart);
            this.el.appendChild(flowContainer);

            right.classList.add('o_flow_right');
            panelContainer.classList.add('o_flow_panel_container');
            panel.classList.add('o_flow_panel');

            zoomContainer.classList.add('o_flow_zoom_container');
            zoom.classList.add('o_flow_zoom');
            zoomContainer.appendChild(zoom);

            viewPointMask.classList.add('o_flow_view_point_mask');
            zoomContainer.appendChild(viewPointMask);

            panelContainer.appendChild(panel);
            right.appendChild(panelContainer);
            right.appendChild(zoomContainer);
            this.el.appendChild(right);

            this.$toolbarcontainer = this.$el.find('.o_flow_toolbar_container');
            this.$toolbar = this.$toolbarcontainer.find('.o_flow_toolbar');

            this.$flowcontainer = this.$el.find('.o_flow_container');
            this.$flowchart = this.$flowcontainer.find('.o_flow_chart');

            this.$panelcontainer = this.$el.find('.o_flow_panel_container');
            this.$panel = this.$panelcontainer.find('.o_flow_panel');
            this.$zoom = this.$el.find(".o_flow_zoom");
            this.$zoomCanvas = this.$el.find(".o_flow_zoom_canvas");

            var self = this;
            this.$zoom.on("click", function (ev) {
                self._focusFlowChartCenter(ev);
            });
        },

        _focusFlowChartCenter: function (ev) {
            console.log("ZOOM ", ev);
            var zoomPos = { x: ev.offsetX, y: ev.offsetY };
            var zoomSize = { x: this.$zoom.width(), y: this.$zoom.height() };
            var flowContainerSize = { x: this.$flowcontainer.width(), y: this.$flowcontainer.height() };
            var flowSize = { x: this.$flowchart.width(), y: this.$flowchart.height() };
            var scale = { x: flowSize.x / zoomSize.x, y: flowSize.y / zoomSize.y };
            var flowPos = { x: zoomPos.x * scale.x, y: zoomPos.y * scale.y };
            var flowContainerPos = { x: flowContainerSize.x / 2, y: flowContainerSize.y / 2 };

            console.log(zoomPos, zoomSize, flowContainerSize, flowSize, scale, flowPos, flowContainerPos);

            var xOffset = flowPos.x - flowContainerPos.x;
            var yOffset = flowPos.y - flowContainerPos.y;
            console.log(xOffset, yOffset);

            if (xOffset < 0) {
                xOffset = 0;
            }
            if (yOffset < 0) {
                yOffset = 0;
            }

            if (flowSize.x - xOffset < flowContainerPos.x * 2) {
                xOffset = flowSize.x - flowContainerPos.x * 2;
            }
            if (flowSize.y - yOffset < flowContainerPos.y * 2) {
                yOffset = flowSize.y - flowContainerPos.y * 2;
            }

            console.log(xOffset, yOffset);
            this.$flowchart.panzoom("pan", 0 - xOffset, 0 - yOffset, {

            });
            this._drawViewPointMask(xOffset, yOffset);
        },

        _renderZoom: function () {
        },

        _debounceRenderZoom: function() {
            _.debounce(this._rerenderZoom.bind(this), 1000, false)();
        },
        
        _rerenderZoom: function () {
            var self = this;
            html2canvas(self.$flowchart[0]).then(function (canvas) {
                // draw view point
                self._drawViewPointRect(canvas);
                /* 
                   var img = new Image();
                   img.src = canvas.toDataURL("image/png");
                   self.$zoom.empty();
                   self.$zoom.append(img);
                */
                if (self.$zoom.find("canvas")) {
                    self.$zoom.find("canvas").remove();
                }
                self.$zoom[0].appendChild(canvas);
            });
        },

        _drawViewPointRect: function (canvas) {
            if (!canvas) {
                return;
            }

            var flowContainerSize = { x: this.$flowcontainer.width(), y: this.$flowcontainer.height() };
            var viewPointSize = { x: flowContainerSize.x, y: flowContainerSize.y };

            var containerLeft = this.$flowcontainer[0].scrollLeft;
            var containerTop = this.$flowcontainer[0].scrollTop;

            var zoomPos = { x: containerLeft, y: containerTop };

            var ctx = canvas.getContext("2d");
            ctx.strokeStyle = "#767676";
            ctx.lineWidth = 15;
            ctx.strokeRect(zoomPos.x, zoomPos.y, viewPointSize.x, viewPointSize.y);
        },

        _drawViewPointMask: function (left, top) {
            var $mask = this.$el.find(".o_flow_view_point_mask");

            var zoomSize = { x: this.$zoom.width(), y: this.$zoom.height() };
            var flowSize = { x: this.$flowchart.width(), y: this.$flowchart.height() };
            var scale = { x: flowSize.x / zoomSize.x, y: flowSize.y / zoomSize.y };

            var flowContainerSize = { x: this.$flowcontainer.width(), y: this.$flowcontainer.height() };
            var viewPointSize = { x: flowContainerSize.x / scale.x, y: flowContainerSize.y / scale.y };

            $mask.css({
                "width": viewPointSize.x + "px",
                "height": viewPointSize.y + "px",
                "left": left / scale.x + "px",
                "top": top / scale.y + "px"
            });
        },

        _renderNoItemPanel: function () {
            this.$panel.empty();
            var html = "<div>No node selected.<div>"
            this.$panel.append($(html));
        },

        _renderOperatorPanel: function (operator) {
            console.log("renderOperatorPanel", operator);
            this.$el.find(".o_flow_panel").empty();
            var data = this.$flowchart.flowchart("getDataRef");
            var node = operator.properties.node;
            node.operator = data.operators[node.node_id];
            node.operators = data.operators;
            node.links = data.links;
            var panelWidget = new PanelWidget(this, { node: node });
            //panelWidget.appendTo(".o_flow_panel");
            panelWidget.appendTo(this.$panel);
            return;
        },

        _renderPanel: function (operator) {
            console.log("renderPanel", operator);
            var self = this;
            if (!operator) {
                this._renderNoItemPanel();
                return;
            }
            this._renderOperatorPanel(operator);
            return;
        },

        _renderToolbar: function () {
            var self = this;
            var node_types = this._flowTypeNodes("incoming_call");
            node_types = _.sortBy(node_types, function(node_item) {
                return node_item.node_seq();
            });
            _.each(node_types, function (node_item) {
                var _toolbar_item = $(self._nodeToolbarItem(node_item));
                _toolbar_item.data("node-type", node_item.node_type());
                self.$toolbar.append(_toolbar_item);
            });

            this.$toolbar.find(".o_flow_toolbar_item").on('click', function (e) {
                var node_type = $(this).data("node-type");
                self._newOperator(node_type);
            });
        },

        _renderFlowChart: function () {
            var self = this;
            this.$flowchart.flowchart({
                data: {},
                verticalConnection: false,

                onOperatorSelect: function (operatorId) {
                    self.$flowchart.find('.o_flow_operator_overlay').remove();

                    var operator_clone = self.$flowchart.flowchart("getOperatorData", operatorId);
                    console.log("select render panel.... ", operator_clone);
                    
                    self._renderPanel(operator_clone);

                    var data = self.$flowchart.flowchart("getDataRef");
                    var operator = data.operators[operatorId];
                    var operatorElement = operator.internal.els.operator;
                    operatorElement.append($(self._operatorOverlay()));
                    operatorElement.find('.o_flow_operator_overlay').data("operator_id", operatorId);
                    operatorElement.find('.o_flow_operator_overlay_button.operator_remove').on("click", function () {
                        self._removeOperator(operatorId);
                    });
                    return true;
                },

                onOperatorUnselect: function () {
                    console.log("unselect render panel");
                    self.$flowchart.find('.o_flow_operator_overlay').remove();
                    self._renderNoItemPanel();
                    return true;
                },

                onOperatorMoved: function (operatorId) {
                    self._resetTempPos();
                    return true;
                },

                onOperatorCreate: function (operatorId) {
                    //self._rerenderPanel(operatorId);
                    return true;
                },

                onOperatorDelete: function (operatorId) {
                    return true;
                },

                onAfterChange: function (changeType) {
                    self._debounceRenderZoom();
                }

            });

            this.$flowchart.panzoom({
                disableZoom: true,
                onEnd: function (e, panzoom, matrix, changed) {
                    console.log(matrix);
                    var left = 0 - matrix[4];
                    var top = 0 - matrix[5];
                    self._drawViewPointMask(left, top);
                }
            });

        },

        _rerenderPanel: function (cId) {
            var operatorId = this.$flowchart.flowchart("getSelectedOperatorId");
            if (cId == operatorId) {
                return;
            }
            console.log("rerender panel cid: ", cId, operatorId);

            if (operatorId) {
                var operator = this.$flowchart.flowchart("getOperatorData", operatorId);
                this._renderPanel(operator);
            } else {
                this._renderPanel();
            }
            return;
        },

        _operatorOverlay: function () {
            var html = '<div class="o_flow_operator_overlay">' +
                '<div class="o_flow_operator_overlay_button operator_remove">' +
                '<span class="fa fa-close"/>' +
                '</div>' +
                '</div>';
            return html;
        },

        _nodeToolbarItem: function (node_type) {
            var item = '<div class="o_flow_toolbar_item">' +
                '<div><span class="fa fa-ICON"></span></div>' +
                '<p>NAME</p>' +
                '</div>';
            return item.replace("ICON", node_type.node_icon()).replace("NAME", node_type.node_name());
        },

        _flowTypeNodes: function (flow_type) {
            var _all_nodes = NodeRegistry.values();
            console.log("ALL NODES", _all_nodes);
            var _filtered_nodes = _.filter(_all_nodes, function (x) {
                var _flow_types = x.flow_types();
                if (_flow_types == null) {
                    return true;
                }

                if (_.find(_flow_types, function (y) {
                    return y === flow_type;
                })) {
                    return true;
                }
            });
            return _filtered_nodes;
        },

        _removeOperator: function (operatorId) {
            var _links = this._getConntectLinks(operatorId);
            var self = this;
            _.each(_links, function (_link) {
                var _ids = _link.toConnector.split(".");
                var _fromOperatorId = _ids[0];
                var _fromConnector = _ids[1];
                var _toOperatorId = _ids[2];
                self._removeLink(_fromOperatorId, _toOperatorId, _fromConnector);
            });


            this.$flowchart.flowchart("deleteOperator", operatorId);
        },

        _getConntectLinks: function (operatorId) {
            var _data = this.$flowchart.flowchart("getData");
            var _links = _.filter(_data.links, function (_link) {
                if (_link.fromOperator == operatorId || _link.toOperator == operatorId) {
                    return true;
                }
            });
            return _links;
        },

        _newOperator: function (node_type) {
            var _node = NodeRegistry.get(node_type);
            var _pos = this._getTempPos();
            var _uuid = createUUID();
            var _seq = this._getTempSeq();

            var _title = _node.node_name() + "-" + _seq;
            var _operator = {
                type: node_type,
                top: _pos.y,
                left: _pos.x,
                properties: {
                    "node": {
                        node_id: _uuid,
                        node_type: node_type,
                        node_path: _node.node_path(),
                    },
                    "class": "o_operator_icon o_operator_icon_" + _node.node_icon(),
                    title: _title,
                    body: " ",
                    inputs: {},
                    outputs: {}
                }
            };
            this.$flowchart.flowchart("createOperator", _uuid, _operator);
        },

        _resetTempPos: function () {
            var _x = this.$flowcontainer.width() / 2;
            var _y = this.$flowcontainer.height() / 2;
            this.tempPos = { "x": _x, "y": _y };
            return this.tempPos;
        },

        _getTempPos: function () {
            if (this.tempPos == null) {
                return this._resetTempPos();
            }
            this.tempPos = { "x": this.tempPos.x + 20, "y": this.tempPos.y + 20 };
            return this.tempPos;
        },

        _getTempSeq: function () {
            if (!this.tempSeq) {
                this.tempSeq = 1;
                return this.tempSeq;
            }
            this.tempSeq = this.tempSeq + 1;
            return this.tempSeq;
        },

        _demoToolbarItems: function () {
            var item = '<div class="o_flow_toolbar_item"><span class="fa fa-music"></span></div>';
            return item;
        },

        _demoOperators: function () {
            return {
                "operator_1": {
                    top: 20,
                    left: 100,
                    properties: {
                        "class": "o_operator_icon o_operator_icon_music",
                        title: "operator_1",
                        body: " ",
                        inputs: {},
                        outputs: {}
                    }
                },
                "operator_2": {
                    top: 80,
                    left: 100,
                    properties: {
                        title: "operator_2",
                        body: " ",
                        inputs: {},
                        outputs: {}
                    }
                }
            };
        },

    });

    return Renderer;

});
