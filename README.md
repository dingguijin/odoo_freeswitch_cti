# odoo_freeswitch_cti
Odoo FreeSWITCH CTI run as a standalone process spawned by Odoo and connect FreeSWITCH inbound service.

It provides a CTI service which can process Computer Telephone Interface requests such as dial, hangup, answer phone call.
Odoo FreeSWITCH CTI connect FreeSWITCH inbound service, so that it can get FreeSWITCH realtime status and push back to Odoo user screen.

It run as a standalone process to keep the connection with FreeSWITCH, monitoring FreeSWITCH status changed and push back to Odoo user in realtime.

Odoo user can send CTI command directly to the service and it will execute it via FreeSWITCH inbound interface.
