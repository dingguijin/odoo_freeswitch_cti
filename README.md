# odoo_freeswitch_cti
Odoo FreeSWITCH CTI run as a standalone process spawned by Odoo and connect FreeSWITCH inbound service.
Based on Odoo and FreeSwitch, it provides a total PBX/Callcenter solution.

![](https://github.com/dingguijin/odoo_freeswitch_cti/raw/main/doc/images/pbx.png)

# Highlight Features

## Callcenter Features

  * Call log
  * Call Recording
  * Call Queue
  * Supervisor/Agent Support
  * Agent Monitoring/Controlling
  * Visual Dialplan Configuration/Call Flow Visualization
  * ASR/TTS Integration (English/Chinese)
  * Voice Service Bot Support
  * Screen Popup Odoo Contact Form
  * IP Phone Hardware / Software Support
  * Phone Standy / Callback Support

## FreeSwitch Features

   * Event Log
   * Api Command Sending/Logging
   * Gateway Configuration
   * Visual Dialplan Configuration

# Install and Run

> FreeSWITCH and Odoo must install in one Linux machine.

## Install and config FreeSWITCH
   > Assuming you know to how to build FreeSWITCH by yourself.
   
   * Download FreeSWITCH source from [Github](https://github.com/signalwire/freeswitch.git)
   * Configure FreeSWITCH
   * Build and Install FreeSWITCH
   * [Modules](doc/freeswitch_module.md) must be included
   * XML_CURL module [config](doc/freeswitch_xml_curl.md)

## Install Odoo

   > Assuming you know Odoo and how to run it by yourself.
   
   * Download Odoo from [Github](https://github.com/odoo/odoo.git)
   * Configure Python environment
   * Install requirements
   * Add database user

## Run

> Assuming you know how to run Odoo with a customized addon path.

   * Download this [repo](https://github.com/dingguijin/odoo_freeswitch_cti.git) into Odoo addons path.
   
   * Run Odoo with this addon at first.
   * Run FreeSWITCH with XML_CURL module configed.

## Install odoo_freeswitch_cti Odoo module

   * Login to Odoo ---- https://localhost:8069 with admin/admin.
   * Menu -> Apps -> odoo_freeswitch_cti install.

## Config Dialplan

   * Login to Odoo
   * Menu -> Callcenter -> Callcenter Dialplan.
   * In dialplan list view, create new dialplan.
   * In dialplan form view, switch view to dialplan flow graph view.

## Config Dialplan Flow Graph

   * Every dialplan flow start from "Start Node" and end with "Exit Node".
   * Start Node -> ... -> Exit Node.
   * Every call into FreeSWITCH will be routed by dialplan flow.
   * To match the special call, change dialplan condition field and condition expression.
   * Every variable and application in dialplan flow graph is the same with FreeSwitch dialplan.


Any question please drop me an email.
Email: dingguijin@gmail.com
Wechat: ding_guijin
