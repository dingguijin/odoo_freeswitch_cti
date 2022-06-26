# -*- coding: utf-8 -*-

from odoo import http

import logging


_EMPTY_XML = """
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<document type="freeswitch/xml">
<section name="result">
<result status="not found" />
</section>
</document>
"""


_CONFIGURATION_XML_TEMPLATE = """
<document type="freeswitch/xml">
<section name="configuration">
  
<configuration name="%s.conf" description="%s">
%s
</configuration>
 
</section>
</document>
"""

_logger = logging.getLogger(__name__)

class FreeSwitchXmlCurl(http.Controller):
    def _get_freeswitch_ip(self):
        _model = http.request.env["freeswitch_cti.freeswitch"].sudo()
        _ss = _model.search_read([("is_active", '=', True)], limit=1)
        if not _ss:
            return None
        return _ss[0].get("freeswitch_ip")
    
    def _get_freeswitch_password(self):
        _model = http.request.env["freeswitch_cti.freeswitch"].sudo()
        _ss = _model.search_read([("is_active", '=', True)], limit=1)
        if not _ss:
            return None
        return _ss[0].get("freeswitch_password")

    def _get_key_value(self):
        if http.request.params.get("key_name") != "name":
            return None
        return http.request.params.get("key_value")

    def _is_key_value(self, value):
        return self._get_key_value() == value
    
    def _is_section_name_matched(self, name):
        if http.request.params.get("section") != name:
            return False
        # directory tag_name is domain
        # if http.request.params.get("tag_name") != name:
        #     return False
        return True

    def _is_purpose_matched(self, purpose):
        if http.request.params.get("purpose") == purpose:
            return True
        return False
    
    def _is_action_matched(self, action):
        if http.request.params.get("action") == action:
            return True
        return False

    def _is_hostname_matched(self):
        _freeswitch_hostname = "freeswitch_hostname"
        _model = http.request.env["freeswitch_cti.freeswitch"].sudo()
        _ss = _model.search_read([("is_active", '=', True)], limit=1)
        if not _ss:
            _logger.error("No freeswitch record")
            return False

        if  len(_ss) > 1:
            _logger.error("Too many freeswitchs record")
            return False

        _hostname = http.request.params.get("hostname")
        _hostname_config = _ss[0].get("freeswitch_hostname")
        if _hostname in [_hostname_config, _hostname_config + ".local"]:
            return True
        
        _logger.error("Freeswitch name not matched, expect %s, but %s" % (_ss[0].get("freeswitch_hostname"), http.request.params.get("hostname")))
        return False

    def _xml_cdr_conf(self):
        _content = """
        <settings>
        <param name="url" value="http://127.0.0.1:8069/freeswitch_xml_cdr"/>
        <param name="retries" value="2"/>
        <param name="delay" value="120"/>
        <param name="log-dir" value="/var/log/cdr"/>
        <param name="err-log-dir" value="/var/log/cdr/errors"/>
        <param name="encode" value="True"/>
        </settings>
        """
        _xml = _CONFIGURATION_XML_TEMPLATE % ("xml_cdr", "xml_cdr", _content)
        return _xml

    def _sofia_conf_config_sofia(self):
        _template = """        
        <global_settings>
        <param name="log-level" value="0"/>
        <param name="debug-presence" value="0"/>
        </global_settings>

        <profiles>

        <profile name="internal">
        <domains>
        <domain name="all" alias="true" parse="true"/>
        </domains>

        <settings>
        <param name="debug" value="0"/>
        <param name="sip-trace" value="no"/>
        <param name="sip-capture" value="no"/>
        <param name="watchdog-enabled" value="no"/>
        <param name="watchdog-step-timeout" value="30000"/>
        <param name="watchdog-event-timeout" value="30000"/>
        
        <param name="log-auth-failures" value="false"/>
        <param name="forward-unsolicited-mwi-notify" value="false"/>
        
        <param name="context" value="public"/>
        <param name="rfc2833-pt" value="101"/>
        <param name="sip-port" value="$${internal_sip_port}"/>
        <param name="dialplan" value="XML"/>
        <param name="dtmf-duration" value="2000"/>
        <param name="inbound-codec-prefs" value="$${global_codec_prefs}"/>
        <param name="outbound-codec-prefs" value="$${global_codec_prefs}"/>
        <param name="rtp-timer-name" value="soft"/>
        <param name="rtp-ip" value="{{SIP_IP}}"/>
        <param name="sip-ip" value="{{SIP_IP}}"/>

        <param name="hold-music" value="$${hold_music}"/>
        <param name="apply-nat-acl" value="nat.auto"/>
        <param name="apply-inbound-acl" value="domains"/>
        <param name="local-network-acl" value="localnet.auto"/>
        <param name="record-path" value="$${recordings_dir}"/>
        <param name="record-template" value="${caller_id_number}.${target_domain}.${strftime(%Y-%m-%d-%H-%M-%S)}.wav"/>
        <param name="manage-presence" value="true"/>
        <param name="presence-hosts" value="$${domain},$${local_ip_v4}"/>
        <param name="presence-privacy" value="$${presence_privacy}"/>
        <param name="inbound-codec-negotiation" value="generous"/>

        <param name="tls" value="$${internal_ssl_enable}"/>
        <param name="tls-only" value="false"/>
        <param name="tls-bind-params" value="transport=tls"/>
        <param name="tls-sip-port" value="$${internal_tls_port}"/>
        <param name="tls-verify-date" value="true"/>
        <param name="tls-verify-policy" value="none"/>
        <param name="tls-verify-depth" value="2"/>
        <param name="tls-verify-in-subjects" value=""/>

        <param name="tls-version" value="$${sip_tls_version}"/>
        <param name="tls-ciphers" value="$${sip_tls_ciphers}"/>

        <param name="inbound-late-negotiation" value="true"/>
        <param name="inbound-zrtp-passthru" value="true"/>
        <param name="nonce-ttl" value="60"/>
        
        <param name="auth-calls" value="$${internal_auth_calls}"/>
        <param name="inbound-reg-force-matching-username" value="true"/>
        <param name="auth-all-packets" value="false"/>
        
        <param name="ext-rtp-ip" value="{{SIP_IP}}"/>
        <param name="ext-sip-ip" value="{{SIP_IP}}"/>
        
        <param name="rtp-timeout-sec" value="300"/>
        <param name="rtp-hold-timeout-sec" value="1800"/>
        
        <param name="force-register-domain" value="$${domain}"/>
        <param name="force-subscription-domain" value="$${domain}"/>
        <param name="force-register-db-domain" value="$${domain}"/>

        <param name="ws-binding"  value=":5066"/>
        <param name="wss-binding" value=":7443"/>
        <param name="challenge-realm" value="auto_from"/>
        
        </settings>
        </profile>

        <profile name="external"> 
        <domains>
        <domain name="all" alias="false" parse="true"/>
        </domains>

        <settings>
        <param name="debug" value="0"/>
        <param name="sip-trace" value="no"/>
        <param name="sip-capture" value="no"/>
        <param name="rfc2833-pt" value="101"/>

        <param name="sip-port" value="$${external_sip_port}"/>
        <param name="dialplan" value="XML"/>
        <param name="context" value="public"/>
        <param name="dtmf-duration" value="2000"/>
        <param name="inbound-codec-prefs" value="$${global_codec_prefs}"/>
        <param name="outbound-codec-prefs" value="$${outbound_codec_prefs}"/>
        <param name="hold-music" value="$${hold_music}"/>
        <param name="rtp-timer-name" value="soft"/>
        <param name="local-network-acl" value="localnet.auto"/>
        <param name="manage-presence" value="false"/>

        <param name="inbound-codec-negotiation" value="generous"/>
        <param name="nonce-ttl" value="60"/>
        <param name="auth-calls" value="false"/>
        <param name="inbound-late-negotiation" value="true"/>
        <param name="inbound-zrtp-passthru" value="true"/> <!-- (also enables late negotiation) -->
        <param name="rtp-ip" value="{{SIP_IP}}"/>
        <param name="sip-ip" value="{{SIP_IP}}"/>
        <param name="ext-rtp-ip" value="{{SIP_IP}}"/>
        <param name="ext-sip-ip" value="{{SIP_IP}}"/>
        <param name="rtp-timeout-sec" value="300"/>
        <param name="rtp-hold-timeout-sec" value="1800"/>

        <param name="tls" value="$${external_ssl_enable}"/>
        <param name="tls-only" value="false"/>
        <param name="tls-bind-params" value="transport=tls"/>
        <param name="tls-sip-port" value="$${external_tls_port}"/>
        <param name="tls-passphrase" value=""/>
        <param name="tls-verify-date" value="true"/>
        <param name="tls-verify-policy" value="none"/>
        <param name="tls-verify-depth" value="2"/>
        <param name="tls-verify-in-subjects" value=""/>

        <param name="tls-verify-in-subjects" value=""/>
        <param name="tls-version" value="$${sip_tls_version}"/>
        </settings>

        <gateways>
        {{GATEWAYS}}
        </gateways>
        </profile>         
        </profiles>

        """
        _freeswitch_ip = self._get_freeswitch_ip() or "$${local_ip_v4}"
        _template = _template.replace("{{SIP_IP}}", _freeswitch_ip)
        _template = _template.replace("{{GATEWAYS}}", "")
        _xml = _CONFIGURATION_XML_TEMPLATE % ("sofia", "sofia", _template)

        return _xml

    def _sofia_conf_internal(self):
        _template = """        

        <profiles>

        <profile name="internal">
        <domains>
        <domain name="all" alias="true" parse="true"/>
        </domains>

        <settings>
        <param name="debug" value="0"/>
        <param name="sip-trace" value="no"/>
        <param name="sip-capture" value="no"/>
        <param name="watchdog-enabled" value="no"/>
        <param name="watchdog-step-timeout" value="30000"/>
        <param name="watchdog-event-timeout" value="30000"/>
        
        <param name="log-auth-failures" value="false"/>
        <param name="forward-unsolicited-mwi-notify" value="false"/>
        
        <param name="context" value="public"/>
        <param name="rfc2833-pt" value="101"/>
        <param name="sip-port" value="$${internal_sip_port}"/>
        <param name="dialplan" value="XML"/>
        <param name="dtmf-duration" value="2000"/>
        <param name="inbound-codec-prefs" value="$${global_codec_prefs}"/>
        <param name="outbound-codec-prefs" value="$${global_codec_prefs}"/>
        <param name="rtp-timer-name" value="soft"/>
        <param name="rtp-ip" value="{{SIP_IP}}"/>
        <param name="sip-ip" value="{{SIP_IP}}"/>

        <param name="hold-music" value="$${hold_music}"/>
        <param name="apply-nat-acl" value="nat.auto"/>
        <param name="apply-inbound-acl" value="domains"/>
        <param name="local-network-acl" value="localnet.auto"/>
        <param name="record-path" value="$${recordings_dir}"/>
        <param name="record-template" value="${caller_id_number}.${target_domain}.${strftime(%Y-%m-%d-%H-%M-%S)}.wav"/>
        <param name="manage-presence" value="true"/>
        <param name="manage-shared-appearance" value="true"/>
        <param name="presence-hosts" value="$${domain},$${local_ip_v4}"/>
        <param name="presence-privacy" value="$${presence_privacy}"/>
        <param name="inbound-codec-negotiation" value="generous"/>

        <param name="tls" value="$${internal_ssl_enable}"/>
        <param name="tls-only" value="false"/>
        <param name="tls-bind-params" value="transport=tls"/>
        <param name="tls-sip-port" value="$${internal_tls_port}"/>
        <param name="tls-verify-date" value="true"/>
        <param name="tls-verify-policy" value="none"/>
        <param name="tls-verify-depth" value="2"/>
        <param name="tls-verify-in-subjects" value=""/>

        <param name="tls-version" value="$${sip_tls_version}"/>
        <param name="tls-ciphers" value="$${sip_tls_ciphers}"/>

        <param name="inbound-late-negotiation" value="true"/>
        <param name="inbound-zrtp-passthru" value="true"/>
        <param name="nonce-ttl" value="60"/>
        
        <param name="auth-calls" value="$${internal_auth_calls}"/>
        <param name="inbound-reg-force-matching-username" value="true"/>
        <param name="auth-all-packets" value="false"/>
        
        <param name="ext-rtp-ip" value="{{SIP_IP}}"/>
        <param name="ext-sip-ip" value="{{SIP_IP}}"/>
        
        <param name="rtp-timeout-sec" value="300"/>
        <param name="rtp-hold-timeout-sec" value="1800"/>
        
        <param name="force-register-domain" value="$${domain}"/>
        <param name="force-subscription-domain" value="$${domain}"/>
        <param name="force-register-db-domain" value="$${domain}"/>

        <param name="ws-binding"  value=":5066"/>
        <param name="wss-binding" value=":7443"/>
        <param name="challenge-realm" value="auto_from"/>
        
        </settings>
        </profile>
        </profiles>

        """
        _freeswitch_ip = self._get_freeswitch_ip() or "$${local_ip_v4}"
        _template = _template.replace("{{SIP_IP}}", _freeswitch_ip)
        _template = _template.replace("{{GATEWAYS}}", "")
        _xml = _CONFIGURATION_XML_TEMPLATE % ("sofia", "sofia", _template)
        
        return _xml

    def _sofia_conf_external(self):
        _template = """        

        <profiles>

        <profile name="external"> 
        <domains>
        <domain name="all" alias="false" parse="true"/>
        </domains>

        <settings>
        <param name="debug" value="0"/>
        <param name="sip-trace" value="no"/>
        <param name="sip-capture" value="no"/>
        <param name="rfc2833-pt" value="101"/>

        <param name="sip-port" value="$${external_sip_port}"/>
        <param name="dialplan" value="XML"/>
        <param name="context" value="public"/>
        <param name="dtmf-duration" value="2000"/>
        <param name="inbound-codec-prefs" value="$${global_codec_prefs}"/>
        <param name="outbound-codec-prefs" value="$${outbound_codec_prefs}"/>
        <param name="hold-music" value="$${hold_music}"/>
        <param name="rtp-timer-name" value="soft"/>
        <param name="local-network-acl" value="localnet.auto"/>
        <param name="manage-presence" value="false"/>

        <param name="inbound-codec-negotiation" value="generous"/>
        <param name="nonce-ttl" value="60"/>
        <param name="auth-calls" value="false"/>
        <param name="inbound-late-negotiation" value="true"/>
        <param name="inbound-zrtp-passthru" value="true"/> <!-- (also enables late negotiation) -->
        <param name="rtp-ip" value="{{SIP_IP}}"/>
        <param name="sip-ip" value="{{SIP_IP}}"/>
        <param name="ext-rtp-ip" value="{{SIP_IP}}"/>
        <param name="ext-sip-ip" value="{{SIP_IP}}"/>
        <param name="rtp-timeout-sec" value="300"/>
        <param name="rtp-hold-timeout-sec" value="1800"/>

        <param name="tls" value="$${external_ssl_enable}"/>
        <param name="tls-only" value="false"/>
        <param name="tls-bind-params" value="transport=tls"/>
        <param name="tls-sip-port" value="$${external_tls_port}"/>
        <param name="tls-passphrase" value=""/>
        <param name="tls-verify-date" value="true"/>
        <param name="tls-verify-policy" value="none"/>
        <param name="tls-verify-depth" value="2"/>
        <param name="tls-verify-in-subjects" value=""/>

        <param name="tls-verify-in-subjects" value=""/>
        <param name="tls-version" value="$${sip_tls_version}"/>
        </settings>

        <gateways>
        {{GATEWAYS}}
        </gateways>
        </profile>         

        </profiles>

        """
        _freeswitch_ip = self._get_freeswitch_ip() or "$${local_ip_v4}"
        _template = _template.replace("{{SIP_IP}}", _freeswitch_ip)
        _template = _template.replace("{{GATEWAYS}}", "")
        _xml = _CONFIGURATION_XML_TEMPLATE % ("sofia", "sofia", _template)

        return _xml
    
    def _sofia_conf(self):
        if http.request.params.get("Event-Calling-Function") == "config_sofia":
            return self._sofia_conf_config_sofia()

        if http.request.params.get("Event-Calling-Function") == "launch_sofia_worker_thread":
            if http.request.params.get("profile") == "internal":
                return self._sofia_conf_internal()
            if http.request.params.get("profile") == "external":
                return self._sofia_conf_external()
        _logger.error("Unknown sofia conf request:  [%s]" % http.request.params)
        return _EMPTY_XML
    
    def _conference_conf(self):
        return _EMPTY_XML

    def _callcenter_conf(self):
        return _EMPTY_XML
    
    def _acl_conf(self):
        _content = """
        <network-lists>
        <list name="lan" default="deny">
        </list>
        <list name="loopback.auto" default="allow">
        </list>
        <list name="localnet.auto" default="allow">
        </list>

        <list name="domains" default="deny">
        <node type="allow" domain="$${domain}"/>
        </list>
        </network-lists>
        """
        _ip = self._get_freeswitch_ip() or "$${domain}"
        _content = _content.replace("{{domain}}", _ip)

        _xml = _CONFIGURATION_XML_TEMPLATE % ("acl", "acl", _content)
        return _xml

    def _event_socket_conf(self):

        _password = self._get_freeswitch_password()
        if not _password:
            _logger.error("Not find freeswitch password")
            return _EMPTY_XML
        
        _content = """
        <settings>
        <param name="nat-map" value="false"/>
        <param name="listen-ip" value="::"/>
        <param name="listen-port" value="8021"/>
        <param name="password" value="%s"/>
        </settings>
        """
        _content = _content % _password
        _xml = _CONFIGURATION_XML_TEMPLATE % ("event_socket", "event_socket", _content)
        return _xml

    def _directory_user_template(self, sip_number, sip_password):
        # user_context "default" is higher priority than profile "public"
        _template = """
        <user id="{{user_extension}}">
        <params>
        <param name="password" value="{{user_extension_password}}"/>
        <param name="vm-password" value="{{user_extension_password}}"/>
        </params>
        <variables>
        <variable name="toll_allow" value="domestic,international,local"/>
        <variable name="accountcode" value="{{user_extension}}"/>
        <variable name="user_context" value="default"/>
        <variable name="effective_caller_id_name" value="{{user_extension}}"/>
        <variable name="effective_caller_id_number" value="{{user_extension}}"/>
        <variable name="outbound_caller_id_name" value="$${outbound_caller_name}"/>
        <variable name="outbound_caller_id_number" value="$${outbound_caller_id}"/>
        </variables>
        </user>
        """
        _template = _template.replace("{{user_extension}}", sip_number)
        _template = _template.replace("{{user_extension_password}}", sip_password)
        return _template

    def _directory_directory_template(self, domain, user_xml):
        _template = """
        <document type="freeswitch/xml">
        <section name="directory">
        <domain name="{{domain}}">
        <params>
        <param name="dial-string" value="{^^:sip_invite_domain=${dialed_domain}:presence_id=${dialed_user}@${dialed_domain}}${sofia_contact(*/${dialed_user}@${dialed_domain})},${verto_contact(${dialed_user}@${dialed_domain})}"/>
        <param name="jsonrpc-allowed-methods" value="verto"/>
        </params>

        <variables>
        <variable name="record_stereo" value="true"/>
        </variables>

        <groups>
        <group name="default">
        <users>
        {{user_element}}
        </users>
        </group>
        </groups>
        </domain>
        </section>
        </document>
        """
        _template = _template.replace("{{domain}}", domain)
        _template = _template.replace("{{user_element}}", user_xml)
        return _template

    def _directory_network_list(self):
        return _EMPTY_XML
    
    def _directory_sip_auth(self):
        _user = http.request.params.get("sip_auth_username") or http.request.params.get("user")
        if not _user:
            _logger.error("no user %s" % http.request.params)
            return _EMPTY_XML
        _domain = http.request.params.get("domain") # sip_auth_realm
        if not _domain:
            _logger.error("no domain %s" % http.request.params)
            return _EMPTY_XML
        _res_users_model = http.request.env["res.users"].sudo()    
        _res_user = _res_users_model.search([("sip_number", "=", "%s" % _user)], limit=1)
        if not _res_user:
            _logger.error("Sip number: [%s] not bind user" % _user)
            return _EMPTY_XML
        _user_xml = self._directory_user_template(_user, _res_user.sip_password)
        _directory_xml = self._directory_directory_template(_domain, _user_xml)
        return _directory_xml
    
    @http.route('/freeswitch_xml_curl/configuration', type='http', auth='none', csrf=False)
    def configuration(self, *args, **kw):
        _logger.info("Configuration: [%s]" % http.request.params)

        if not self._is_hostname_matched():
            return _EMPTY_XML

        if not self._is_section_name_matched("configuration"):
            return _EMPTY_XML

        if self._is_key_value("xml_cdr.conf"):
            return self._xml_cdr_conf()

        if self._is_key_value("sofia.conf"):
            return self._sofia_conf()

        if self._is_key_value("conference.conf"):
            return self._conference_conf()

        if self._is_key_value("callcenter.conf"):
            return self._callcenter_conf()

        if self._is_key_value("event_socket.conf"):
            return self._event_socket_conf()

        if self._is_key_value("acl.conf"):
            return self._acl_conf()

        if self._is_key_value("voicemail.conf"):
            return _EMPTY_XML

        if self._is_key_value("loopback.conf"):
            return _EMPTY_XML

        if self._is_key_value("post_load_modules.conf"):
            return _EMPTY_XML

        if self._is_key_value("post_load_switch.conf"):
            return _EMPTY_XML

        if self._is_key_value("local_stream.conf"):
            return _EMPTY_XML

        if self._is_key_value("shout.conf"):
            return _EMPTY_XML

        if self._is_key_value("sndfile.conf"):
            return _EMPTY_XML

        if self._is_key_value("opus.conf"):
            return _EMPTY_XML

        if self._is_key_value("spandsp.conf"):
            return _EMPTY_XML

        if self._is_key_value("amr.conf"):
            return _EMPTY_XML

        if self._is_key_value("httapi.conf"):
            return _EMPTY_XML

        if self._is_key_value("hash.conf"):
            return _EMPTY_XML

        if self._is_key_value("fifo.conf"):
            return _EMPTY_XML

        if self._is_key_value("db.conf"):
            return _EMPTY_XML

        _logger.error("Configuration [%s] is not recognized." % self._get_key_value())
        return _EMPTY_XML

    def _is_internal_dialplan(self):
        if http.request.params.get("Caller-Context") == "default":
            return True
        return False

    def _is_external_dialplan(self):
        if http.request.params.get("Caller-Context") == "public":
            return True
        return False

    def _internal_diaplan(self):
        # extension 1000 - 1199
        _template = """
        <?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <document type="freeswitch/xml">
        <section name="dialplan" description="Xml Curl Universal Dialplan">
        
        <context name="default">

        <extension name="unloop">
        <condition field="${unroll_loops}" expression="^true$"/>
        <condition field="${sip_looped_call}" expression="^true$">
        <action application="deflect" data="${destination_number}"/>
        </condition>
        </extension>
        

        <extension name="global-intercept">
        <condition field="destination_number" expression="^886$">
        <action application="answer"/>
        <action application="intercept" data="${hash(select/${domain_name}-last_dial_ext/global)}"/>
        <action application="sleep" data="2000"/>
        </condition>
        </extension>
        
        <extension name="group-intercept">
        <condition field="destination_number" expression="^\*8$">
        <action application="answer"/>
        <action application="intercept" data="${hash(select/${domain_name}-last_dial_ext/${callgroup})}"/>
        <action application="sleep" data="2000"/>
        </condition>
        </extension>
        
        <extension name="intercept-ext">
        <condition field="destination_number" expression="^\*\*(\d+)$">
        <action application="answer"/>
        <action application="intercept" data="${hash(select/${domain_name}-last_dial_ext/$1)}"/>
        <action application="sleep" data="2000"/>
        </condition>
        </extension>
        
        
        <extension name="redial">
        <condition field="destination_number" expression="^(redial|870)$">
        <action application="transfer" data="${hash(select/${domain_name}-last_dial/${caller_id_number})}"/>
        </condition>
        </extension>
        
        <extension name="eavesdrop">
        <condition field="destination_number" expression="^88(\d{4})$|^\*0(.*)$">
        <action application="answer"/>
        <action application="eavesdrop" data="${hash(select/${domain_name}-spymap/$1$2)}"/>
        </condition>
        </extension>
        
        <extension name="eavesdrop">
        <condition field="destination_number" expression="^779$">
        <action application="answer"/>
        <action application="set" data="eavesdrop_indicate_failed=tone_stream://%(500, 0, 320)"/>
        <action application="set" data="eavesdrop_indicate_new=tone_stream://%(500, 0, 620)"/>
        <action application="set" data="eavesdrop_indicate_idle=tone_stream://%(250, 0, 920)"/>
        <action application="eavesdrop" data="all"/>
        </condition>
        </extension>
        
        <extension name="call_return">
        <condition field="destination_number" expression="^\*69$|^869$|^lcr$">
        <action application="transfer" data="${hash(select/${domain_name}-call_return/${caller_id_number})}"/>
        </condition>
        </extension>
        
        <extension name="del-group">
        <condition field="destination_number" expression="^80(\d{2})$">
        <action application="answer"/>
        <action application="group" data="delete:$1@${domain_name}:${sofia_contact(${sip_from_user}@${domain_name})}"/>
        <action application="gentones" data="%(1000, 0, 320)"/>
        </condition>
        </extension>
        
        <extension name="add-group">
        <condition field="destination_number" expression="^81(\d{2})$">
        <action application="answer"/>
        <action application="group" data="insert:$1@${domain_name}:${sofia_contact(${sip_from_user}@${domain_name})}"/>
        <action application="gentones" data="%(1000, 0, 640)"/>
        </condition>
        </extension>
        
        <extension name="call-group-simo">
        <condition field="destination_number" expression="^82(\d{2})$">
        <action application="bridge" data="{leg_timeout=15,ignore_early_media=true}${group(call:$1@${domain_name})}"/>
        </condition>
        </extension>
        
        <extension name="call-group-order">
        <condition field="destination_number" expression="^83(\d{2})$">
        <action application="bridge" data="{leg_timeout=15,ignore_early_media=true}${group(call:$1@${domain_name}:order)}"/>
        </condition>
        </extension>
        
        <extension name="extension-intercom">
        <condition field="destination_number" expression="^8(10[01][0-9])$">
        <action application="set" data="dialed_extension=$1"/>
        <action application="export" data="sip_auto_answer=true"/>
        <action application="bridge" data="user/${dialed_extension}@${domain_name}"/>
        </condition>
        </extension>
        
        
        <extension name="group_dial_sales">
        <condition field="destination_number" expression="^2000$">
        <action application="bridge" data="${group_call(sales@${domain_name})}"/>
        </condition>
        </extension>
        
        <extension name="group_dial_support">
        <condition field="destination_number" expression="^2001$">
        <action application="bridge" data="group/support@${domain_name}"/>
        </condition>
        </extension>
        
        <extension name="group_dial_billing">
        <condition field="destination_number" expression="^2002$">
        <action application="bridge" data="group/billing@${domain_name}"/>
        </condition>
        </extension>
        
        <!-- voicemail operator extension -->
        <extension name="operator">
        <condition field="destination_number" expression="^(operator|0)$">
        <action application="set" data="transfer_ringback=$${hold_music}"/>
        <action application="transfer" data="1000 XML features"/>
        </condition>
        </extension>
        
        <!-- voicemail main extension -->
        <extension name="vmain">
        <condition field="destination_number" expression="^vmain$|^4000$|^\*98$">
        <action application="answer"/>
        <action application="sleep" data="1000"/>
        <action application="voicemail" data="check default ${domain_name}"/>
        </condition>
        </extension>
        
        <!--
        start a dynamic conference with the settings of the "default" conference profile in conference.conf.xml
        -->
        <extension name="nb_conferences">
        <condition field="destination_number" expression="^(30\d{2})$">
        <action application="answer"/>
        <action application="conference" data="$1-${domain_name}@default"/>
        </condition>
        </extension>
        
        <extension name="wb_conferences">
        <condition field="destination_number" expression="^(31\d{2})$">
        <action application="answer"/>
        <action application="conference" data="$1-${domain_name}@wideband"/>
        </condition>
        </extension>
        
        <extension name="uwb_conferences">
        <condition field="destination_number" expression="^(32\d{2})$">
        <action application="answer"/>
        <action application="conference" data="$1-${domain_name}@ultrawideband"/>
        </condition>
        </extension>
        
        <!-- MONO 48kHz conferences -->
        <extension name="cdquality_conferences">
        <condition field="destination_number" expression="^(33\d{2})$">
        <action application="answer"/>
        <action application="conference" data="$1-${domain_name}@cdquality"/>
        </condition>
        </extension>
        
        <!-- STEREO 48kHz conferences / Video MCU -->
        <extension name="cdquality_stereo_conferences">
        <condition field="destination_number" expression="^(35\d{2}).*?-screen$">
        <action application="answer"/>
        <action application="send_display" data="FreeSWITCH Conference|$1"/>
        <action application="set" data="conference_member_flags=join-vid-floor"/>
        <action application="conference" data="$1@video-mcu-stereo"/>
        </condition>
        </extension>
        
        <extension name="conference-canvases" continue="true">
        <condition field="destination_number" expression="(35\d{2})-canvas-(\d+)">
        <action application="push" data="conference_member_flags=second-screen"/>
        <action application="set" data="video_initial_watching_canvas=$2"/>
        <action application="transfer" data="$1"/>
        </condition>
        </extension>
        
        <extension name="conf mod">
        <condition field="destination_number" expression="^6070-moderator$">
        <action application="answer"/>
        <action application="set" data="conference_member_flags=moderator"/>
        <action application="conference" data="$1-${domain_name}@video-mcu-stereo"/>
        </condition>
        </extension>
        
        <extension name="delay_echo">
        <condition field="destination_number" expression="^9195$">
        <action application="answer"/>
        <action application="delay_echo" data="5000"/>
        </condition>
        </extension>
        
        <extension name="echo">
        <condition field="destination_number" expression="^9196$">
        <action application="answer"/>
        <action application="echo"/>
        </condition>
        </extension>
        
        <extension name="milliwatt">
        <condition field="destination_number" expression="^9197$">
        <action application="answer"/>
        <action application="playback" data="{loops=-1}tone_stream://%(251,0,1004)"/>
        </condition>
        </extension>
        
        <extension name="tone_stream">
        <condition field="destination_number" expression="^9198$">
        <action application="answer"/>
        <action application="playback" data="{loops=10}tone_stream://path=${conf_dir}/tetris.ttml"/>
        </condition>
        </extension>
        
        <extension name="hold_music">
        <condition field="destination_number" expression="^9664$"/>
        <condition field="${rtp_has_crypto}" expression="^(AES_CM_128_HMAC_SHA1_32|AES_CM_128_HMAC_SHA1_80)$">
        <action application="answer"/>
        <action application="execute_extension" data="is_secure XML features"/>
        <action application="playback" data="$${hold_music}"/>
        <anti-action application="set" data="zrtp_secure_media=true"/>
        <anti-action application="answer"/>
        <anti-action application="playback" data="silence_stream://2000"/>
        <anti-action application="execute_extension" data="is_zrtp_secure XML features"/>
        <anti-action application="playback" data="$${hold_music}"/>
        </condition>
        </extension>

        <extension name="laugh break">
        <condition field="destination_number" expression="^9386$">
        <action application="answer"/>
        <action application="sleep" data="1500"/>
        <action application="playback" data="phrase:funny_prompts"/>
        <action application="hangup"/>
        </condition>
        </extension>
        
        
        <extension name="Local_Extension">
        <condition field="destination_number" expression="^(1[01][0-9]{2})$">
        <action application="export" data="dialed_extension=$1"/>
        <!-- bind_meta_app can have these args <key> [a|b|ab] [a|b|o|s] <app> -->
        <action application="bind_meta_app" data="1 b s execute_extension::dx XML features"/>
        <action application="bind_meta_app" data="2 b s record_session::$${recordings_dir}/${caller_id_number}.${strftime(%Y-%m-%d-%H-%M-%S)}.wav"/>
        <action application="bind_meta_app" data="3 b s execute_extension::cf XML features"/>
        <action application="bind_meta_app" data="4 b s execute_extension::att_xfer XML features"/>
        <action application="set" data="ringback=${us-ring}"/>
        <action application="set" data="transfer_ringback=$${hold_music}"/>
        <action application="set" data="call_timeout=30"/>
        <!-- <action application="set" data="sip_exclude_contact=${network_addr}"/> -->
        <action application="set" data="hangup_after_bridge=true"/>
        <!--<action application="set" data="continue_on_fail=NORMAL_TEMPORARY_FAILURE,USER_BUSY,NO_ANSWER,TIMEOUT,NO_ROUTE_DESTINATION"/> -->
        <action application="set" data="continue_on_fail=true"/>
        <action application="hash" data="insert/${domain_name}-call_return/${dialed_extension}/${caller_id_number}"/>
        <action application="hash" data="insert/${domain_name}-last_dial_ext/${dialed_extension}/${uuid}"/>
        <action application="set" data="called_party_callgroup=${user_data(${dialed_extension}@${domain_name} var callgroup)}"/>
        <action application="hash" data="insert/${domain_name}-last_dial_ext/${called_party_callgroup}/${uuid}"/>
        <action application="hash" data="insert/${domain_name}-last_dial_ext/global/${uuid}"/>

        <!--<action application="export" data="nolocal:rtp_secure_media=${user_data(${dialed_extension}@${domain_name} var rtp_secure_media)}"/>-->
        <action application="hash" data="insert/${domain_name}-last_dial/${called_party_callgroup}/${uuid}"/>
        <action application="bridge" data="user/${dialed_extension}@${domain_name}"/>
        <action application="answer"/>
        <action application="sleep" data="1000"/>
        <action application="bridge" data="loopback/app=voicemail:default ${domain_name} ${dialed_extension}"/>
  
        </condition>
        </extension>

        
        <extension name="acknowledge_call">
        <condition field="destination_number" expression="^(.*)$">
        <action application="acknowledge_call"/>
        <action application="ring_ready"/>
        <action application="playback" data="$${hold_music}"/>
        </condition>
        </extension>

        </context>

        </section>
        </document>
        """
        
        # _caller_id = http.request.params.get("Caller-Caller-ID-Number")
        # _template = _template % len(_caller_id)
        # _template = _template.replace("{{context}}",
        #                               http.request.params.get("Caller-Context"))
                                      
        return _template

    def _external_dialplan(self):
        _template = """
        <?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <document type="freeswitch/xml">
        <section name="dialplan" description="Xml Curl Universal Dialplan">

        <context name="public">
        <extension name="universal">
        <condition field="destination_number" expression="^.*$">
        <action application="socket" data="localhost:8900 async full" />
        </condition>
        </extension>
        </context>

        </section>
        </document>
        """

        return _template

    @http.route('/freeswitch_xml_curl/dialplan', type='http', auth='none', csrf=False)
    def dialplan(self, *args, **kwargs):
        _logger.info("DIALPLAN for [%s], [%s]" % (http.request.params["Caller-Caller-ID-Name"],
                                                  http.request.params["Caller-Context"]))

        if not self._is_hostname_matched():
            return _EMPTY_XML

        if not self._is_section_name_matched("dialplan"):
            return _EMPTY_XML

        if self._is_internal_dialplan():
            return self._internal_diaplan()

        if self._is_external_dialplan():
            return self._external_dialplan()
        
        return _EMPTY_XML

    @http.route('/freeswitch_xml_curl/directory', type='http', auth='none', csrf=False)
    def directory(self, *args, **kw):
        # _logger.info("DIRECTORY XML CURL---> %s" % http.request.params)

        if not self._is_hostname_matched():
            return _EMPTY_XML

        if not self._is_section_name_matched("directory"):
            return _EMPTY_XML

        if self._is_purpose_matched("gateways"):
            return _EMPTY_XML

        if self._is_purpose_matched("network-list"):
            return self._directory_network_list()

        if self._is_action_matched("sip_auth"):
            return self._directory_sip_auth()

        if self._is_action_matched("user_call"):
            return self._directory_sip_auth()

        if self._is_action_matched("message-count"):
            return _EMPTY_XML

        if http.request.params.get("Event-Name") == "REQUEST_PARAMS":
            _logger.error("DIRECTORY REQUEST_PARAMS: [%s] [%s] [%s]" % (
                http.request.params["user"],
                http.request.params["domain"],
                http.request.params["Core-UUID"]))
            return _EMPTY_XML
        
        _logger.error(">>>>> DIRECTORY UNKNOWN request %s" % http.request.params)

        return _EMPTY_XML


    @http.route('/freeswitch_xml_cdr', type='http', auth='none', csrf=False)
    def xml_cdr(self, *args, **kw):
        _logger.info(http.request.params)
        return ""
