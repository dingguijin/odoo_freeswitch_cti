# -*- coding: utf-8 -*-

import odoo.http as http

import logging

_logger = logging.getLogger(__name__)

class DialplanView(http.Controller):
    
    @http.route('/freeswitch_cti/dialplan/get_info', type='json', auth='user')
    def get_dialplan_info(self, id):
        nodes = http.request.env['freeswitch_cti.dialplan_node'].search_read([('extension_id', '=', id)])
        dialplan = http.request.env['freeswitch_cti.dialplan_extension'].search_read([('id', '=', id)])
        events = http.request.env['freeswtich_cti.dialplan_node_event'].search_read([('extension_id', '=', id)])
        return dict(events=events, nodes=nodes, dialplan=dialplan[0])

    @http.route('/freeswitch_cti/dialplan/update_info', type='json', auth='user')
    def update_flow_info(self, id, nodes, events):
        node_class = http.request.env['freeswitch_cti.dialplan_node']
        event_class = http.request.env['freeswitch_cti.dialplan_node_event']

        node_class.search([('extension_id', '=', id)]).unlink()
        event_class.search([('extension_id', '=', id)]).unlink()

        node_ids = {}
        for node in nodes:
            node_id = node["node_id"]
            del node["node_id"]
            node.update({"extension_id": id})
            nodes_record = node_class.create(node)
            node_ids[str(node_id)] = nodes_record.id
            
        for event in events:
            node_id = node_ids.get(str(event["node_id"]))
            next_node = node_ids.get(str(event["next_node"]))
            if node_id == None or next_node == None:
                _logger.error("node_ids:%s no event:%s", node_ids, event)
                continue                    
            event.update({
                "extension_id": id,
                "node_id": node_id,
                "next_node": next_node
            })
            event_class.create(event)
            
        return self.get_info(id)
