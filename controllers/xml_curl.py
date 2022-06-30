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

from .. import freeswitch_info

_logger = logging.getLogger(__name__)

class FreeSwitchXmlCurl(http.Controller):

    def _search_all(self, table):
        _model = http.request.env[table].sudo()
        return _model.search([])

    def _search_callcenter_tiers(self):
        return self._search_all("freeswitch_cti.callcenter_tier")
    
    def _search_callcenter_queues(self):
        return self._search_all("freeswitch_cti.callcenter_queue")

    def _search_callcenter_agents(self):
        return self._search_all("res.users")

    def _callcenter_queue_xml(self, queue):
        _xml = """<queue name="%s">%s</queue>"""
        _param_template = """<param name="%s" value="%s" />"""
        _params = []
        _params.append(_param_template % ("strategy", queue.strategy))
        _params.append(_param_template % ("moh-sound", queue.moh_sound))
        _params.append(_param_template % ("record-template", queue.record_template))
        _params.append(_param_template % ("time-base-score", queue.time_base_score))
        _params.append(_param_template % ("tier-rules-apply", queue.tier_rules_apply))
        _params.append(_param_template % ("tier-rule-wait-second", queue.tier_rule_wait_second))
        _params.append(_param_template % ("tier-rule-wait-multiply-level", queue.tier_rule_wait_multiple_level))
        _params.append(_param_template % ("tier-rule-no-agent-no-wait", queue.tier_rule_no_agent_no_wait))
        _params.append(_param_template % ("discard-abandoned-after", queue.discard_abandoned_after))
        _params.append(_param_template % ("max-wait-time", queue.max_wait_time))
        _params.append(_param_template % ("max-wait-time-with-no-agent", queue.max_wait_time_with_no_agent))
        
        _xml = _xml % (queue.name, "\n".join(_params))
        return _xml

    def _callcenter_agent_xml(self, agent):
        _xml = """<agent name="%s" type="%s" contact="%s" status="%s" max-no-answer="%s" wrap-up-time="%s" reject-delay-time="%s" busy-delay-time="%s"></agent>"""
        
        _xml = _xml % (agent.agent_name,
                       agent.agent_type,
                       agent.agent_contact,
                       agent.agent_status,
                       agent.agent_max_no_answer,
                       agent.agent_wrap_up_time,
                       agent.agent_reject_delay_time,
                       agent.agent_busy_delay_time)
        return _xml

    def _callcenter_tier_xml(self, tier):
        _xml = """<tier agent="%s" queue="%s" level="%s" position="%s"></tier>"""
        _xml = _xml % (tier.tier_agent_id.agent_name,
                       tier.tier_queue_id.name,
                       tier.tier_level,
                       tier.tier_position)
        return _xml
    
    def _get_freeswitch_ip(self):
        # _model = http.request.env["freeswitch_cti.freeswitch"].sudo()
        # _ss = _model.search_read([("is_active", '=', True)], limit=1)
        # if not _ss:
        #     return None
        # return _ss[0].get("freeswitch_ip")
        return freeswitch_info._FREESWITCH_INFO.get("freeswitch_ip")
        
    def _get_freeswitch_password(self):
        # _model = http.request.env["freeswitch_cti.freeswitch"].sudo()
        # _ss = _model.search_read([("is_active", '=', True)], limit=1)
        # if not _ss:
        #     return None
        # return _ss[0].get("freeswitch_password")
        return freeswitch_info._FREESWITCH_INFO.get("freeswitch_password")
    
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
        # _freeswitch_hostname = "freeswitch_hostname"
        # _model = http.request.env["freeswitch_cti.freeswitch"].sudo()
        # _ss = _model.search_read([("is_active", '=', True)], limit=1)
        # if not _ss:
        #     _logger.error("No freeswitch record")
        #     return False

        # if  len(_ss) > 1:
        #     _logger.error("Too many freeswitchs record")
        #     return False

        # _hostname = http.request.params.get("hostname")
        # _hostname_config = _ss[0].get("freeswitch_hostname")
        # if _hostname in [_hostname_config, _hostname_config + ".local"]:
        #     return True
        
        # _logger.error("Freeswitch name not matched, expect %s, but %s" % (_ss[0].get("freeswitch_hostname"), http.request.params.get("hostname")))
        # return False
        return True

    def _json_cdr_conf(self):
        _content = """
        <settings>
        <param name="log-b-leg" value="true"/>
        <param name="prefix-a-leg" value="false"/>
        <param name="encode-values" value="true"/>
        <param name="log-http-and-disk" value="false"/>
        <param name="log-dir" value=""/>
        <param name="rotate" value="false"/>
        <param name="url" value="http://192.168.50.121:8069/freeswitch_json_cdr"/>
        <param name="auth-scheme" value="basic"/>
        <param name="cred" value=""/>
        <param name="encode" value="base64|true|false"/>
        <param name="retries" value="0"/>
        <param name="delay" value="5000"/>
        <param name="disable-100-continue" value="false"/>
        <param name="err-log-dir" value="" />
        </settings>
        """
        _xml = _CONFIGURATION_XML_TEMPLATE % ("json_cdr", "json_cdr", _content)
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
        _content = """
        <!-- Advertise certain presence on startup . -->
        <advertise>
        <room name="3001@$${domain}" status="FreeSWITCH"/>
        </advertise>
        
        <!-- These are the default keys that map when you do not specify a caller control group -->	
        <!-- Note: none and default are reserved names for group names.  Disabled if dist-dtmf member flag is set. -->	
        <caller-controls>
        <group name="default">
        <control action="mute" digits="0"/>
        <control action="deaf mute" digits="*"/>
        <control action="energy up" digits="9"/>
        <control action="energy equ" digits="8"/>
        <control action="energy dn" digits="7"/>
        <control action="vol talk up" digits="3"/>
        <control action="vol talk zero" digits="2"/>
        <control action="vol talk dn" digits="1"/>
        <control action="vol listen up" digits="6"/>
        <control action="vol listen zero" digits="5"/>
        <control action="vol listen dn" digits="4"/>
        <control action="hangup" digits="#"/>
        </group>
        </caller-controls>

        <!-- Profiles are collections of settings you can reference by name. -->
        <profiles>
        <!--If no profile is specified it will default to "default"-->
        <profile name="default">
        <!-- Directory to drop CDR's 
        'auto' means $PREFIX/logs/conference_cdr/<confernece_uuid>.cdr.xml
	a non-absolute path means $PREFIX/logs/<value>/<confernece_uuid>.cdr.xml
	absolute path means <value>/<confernece_uuid>.cdr.xml
        -->
        <!-- <param name="cdr-log-dir" value="auto"/> -->
        
        <!-- Domain (for presence) -->
        <param name="domain" value="$${domain}"/>
        <!-- Sample Rate-->
        <param name="rate" value="8000"/>
        <!-- Number of milliseconds per frame -->
        <param name="interval" value="20"/>
        <!-- Energy level required for audio to be sent to the other users -->
        <param name="energy-level" value="100"/>
        
        <!--Can be | delim of waste|mute|deaf|dist-dtmf waste will always transmit data to each channel
        even during silence.  dist-dtmf propagates dtmfs to all other members, but channel controls
	via dtmf will be disabled. -->
        <!-- <param name="member-flags" value="waste"/> -->
        
        <!-- Name of the caller control group to use for this profile -->
        <!-- <param name="caller-controls" value="some name"/> -->
        <!-- Name of the caller control group to use for the moderator in this profile -->
        <!-- <param name="moderator-controls" value="some name"/> -->
        <!-- TTS Engine to use -->
        <!-- <param name="tts-engine" value="cepstral"/> -->
        <!-- TTS Voice to use -->
        <!-- <param name="tts-voice" value="david"/> -->

        <!-- If TTS is enabled all audio-file params beginning with -->
        <!-- 'say:' will be considered text to say with TTS -->
        <!-- Override the default path here, after which you use relative paths in the other sound params -->
        <!-- Note: The default path is the conference's first caller's sound_prefix -->
        <!-- <param name="sound-prefix" value="$${sound_prefix}"/> -->
        <!-- File to play to acknowledge succees -->
        <!-- <param name="ack-sound" value="beep.wav"/> -->
        <!-- File to play to acknowledge failure -->
        <!-- <param name="nack-sound" value="beeperr.wav"/> -->
        <!-- File to play to acknowledge muted -->
        <param name="muted-sound" value="conference/conf-muted.wav"/>
        <!-- File to play to acknowledge unmuted -->
        <param name="unmuted-sound" value="conference/conf-unmuted.wav"/>
        <!-- File to play if you are alone in the conference -->
        <param name="alone-sound" value="conference/conf-alone.wav"/>
        <!-- File to play endlessly (nobody will ever be able to talk) -->
        <!-- <param name="perpetual-sound" value="perpetual.wav"/> -->
        <!-- File to play when you're alone (music on hold)-->
        <param name="moh-sound" value="$${hold_music}"/>
        <!-- File to play when you join the conference -->
        <param name="enter-sound" value="tone_stream://%(200,0,500,600,700)"/>
        <!-- File to play when you leave the conference -->
        <param name="exit-sound" value="tone_stream://%(500,0,300,200,100,50,25)"/>
        <!-- File to play when you are ejected from the conference -->
        <param name="kicked-sound" value="conference/conf-kicked.wav"/>
        <!-- File to play when the conference is locked -->
        <param name="locked-sound" value="conference/conf-locked.wav"/>
        <!-- File to play when the conference is locked during the call-->
        <param name="is-locked-sound" value="conference/conf-is-locked.wav"/>
        <!-- File to play when the conference is unlocked during the call-->
        <param name="is-unlocked-sound" value="conference/conf-is-unlocked.wav"/>
        <!-- File to play to prompt for a pin -->
        <param name="pin-sound" value="conference/conf-pin.wav"/>
        <!-- File to play to when the pin is invalid -->
        <param name="bad-pin-sound" value="conference/conf-bad-pin.wav"/>
        <!-- Conference pin -->
        <!-- <param name="pin" value="12345"/> -->
        <!-- <param name="moderator-pin" value="54321"/> -->
        <!-- Max number of times the user can be prompted for PIN -->
        <!-- <param name="pin-retries" value="3"/> -->
        <!-- Default Caller ID Name for outbound calls -->
        <param name="caller-id-name" value="$${outbound_caller_name}"/>
        <!-- Default Caller ID Number for outbound calls -->
        <param name="caller-id-number" value="$${outbound_caller_id}"/>
        <!-- Suppress start and stop talking events -->
        <!-- <param name="suppress-events" value="start-talking,stop-talking"/> -->
        <!-- enable comfort noise generation -->
        <param name="comfort-noise" value="true"/>
        <!-- Uncomment auto-record to toggle recording every conference call. -->
        <!-- Another valid value is   shout://user:pass@server.com/live.mp3   -->
        <!--
        <param name="auto-record" value="$${recordings_dir}/${conference_name}_${strftime(%Y-%m-%d-%H-%M-%S)}.wav"/>
        -->
        
        <!-- IVR digit machine timeouts -->
        <!-- How much to wait between DTMF digits to match caller-controls -->
        <!-- <param name="ivr-dtmf-timeout" value="500"/> -->
        <!-- How much to wait for the first DTMF, 0 forever -->
        <!-- <param name="ivr-input-timeout" value="0" /> -->
        <!-- Delay before a conference is asked to be terminated -->
        <!-- <param name="endconf-grace-time" value="120" /> -->
        <!-- Can be | delim of wait-mod|audio-always|video-bridge|video-floor-only
        wait_mod will wait until the moderator in,
        audio-always will always mix audio from all members regardless they are talking or not -->
        <!-- <param name="conference-flags" value="audio-always"/> -->
        <!-- Allow live array sync for Verto -->
        <!-- <param name="conference-flags" value="livearray-sync"/> -->
        </profile>
        
        <profile name="wideband">
        <param name="domain" value="$${domain}"/>
        <param name="rate" value="16000"/>
        <param name="interval" value="20"/>
        <param name="energy-level" value="100"/>
        <!-- <param name="sound-prefix" value="$${sound_prefix}"/> -->
        <param name="muted-sound" value="conference/conf-muted.wav"/>
        <param name="unmuted-sound" value="conference/conf-unmuted.wav"/>
        <param name="alone-sound" value="conference/conf-alone.wav"/>
        <param name="moh-sound" value="$${hold_music}"/>
        <param name="enter-sound" value="tone_stream://%(200,0,500,600,700)"/>
        <param name="exit-sound" value="tone_stream://%(500,0,300,200,100,50,25)"/>
        <param name="kicked-sound" value="conference/conf-kicked.wav"/>
        <param name="locked-sound" value="conference/conf-locked.wav"/>
        <param name="is-locked-sound" value="conference/conf-is-locked.wav"/>
        <param name="is-unlocked-sound" value="conference/conf-is-unlocked.wav"/>
        <param name="pin-sound" value="conference/conf-pin.wav"/>
        <param name="bad-pin-sound" value="conference/conf-bad-pin.wav"/>
        <param name="caller-id-name" value="$${outbound_caller_name}"/>
        <param name="caller-id-number" value="$${outbound_caller_id}"/>
        <param name="comfort-noise" value="true"/>
        <!-- <param name="tts-engine" value="flite"/> -->
        <!-- <param name="tts-voice" value="kal16"/> -->
        </profile>
        
        <profile name="ultrawideband">
        <param name="domain" value="$${domain}"/>
        <param name="rate" value="32000"/>
        <param name="interval" value="20"/>
        <param name="energy-level" value="100"/>
        <!-- <param name="sound-prefix" value="$${sound_prefix}"/> -->
        <param name="muted-sound" value="conference/conf-muted.wav"/>
        <param name="unmuted-sound" value="conference/conf-unmuted.wav"/>
        <param name="alone-sound" value="conference/conf-alone.wav"/>
      <param name="moh-sound" value="$${hold_music}"/>
      <param name="enter-sound" value="tone_stream://%(200,0,500,600,700)"/>
      <param name="exit-sound" value="tone_stream://%(500,0,300,200,100,50,25)"/>
      <param name="kicked-sound" value="conference/conf-kicked.wav"/>
      <param name="locked-sound" value="conference/conf-locked.wav"/>
      <param name="is-locked-sound" value="conference/conf-is-locked.wav"/>
      <param name="is-unlocked-sound" value="conference/conf-is-unlocked.wav"/>
      <param name="pin-sound" value="conference/conf-pin.wav"/>
      <param name="bad-pin-sound" value="conference/conf-bad-pin.wav"/>
      <param name="caller-id-name" value="$${outbound_caller_name}"/>
      <param name="caller-id-number" value="$${outbound_caller_id}"/>
      <param name="comfort-noise" value="true"/>

      <!-- <param name="conference-flags" value="video-floor-only|rfc-4579|livearray-sync|auto-3d-position|transcode-video|minimize-video-encoding"/> -->

      <!-- <param name="video-mode" value="mux"/> -->
      <!-- <param name="video-layout-name" value="3x3"/> -->
      <!-- <param name="video-layout-name" value="group:grid"/> -->
      <!-- <param name="video-canvas-size" value="1280x720"/> -->
      <!-- <param name="video-canvas-bgcolor" value="#333333"/> -->
      <!-- <param name="video-layout-bgcolor" value="#000000"/> -->
      <!-- <param name="video-codec-bandwidth" value="2mb"/> -->
      <!-- <param name="video-fps" value="15"/> -->
      <!-- <param name="video-auto-floor-msec" value="100"/> -->


      <!-- <param name="tts-engine" value="flite"/> -->
      <!-- <param name="tts-voice" value="kal16"/> -->
    </profile>

    <profile name="cdquality">
      <param name="domain" value="$${domain}"/>
      <param name="rate" value="48000"/>
      <param name="interval" value="20"/>
      <param name="energy-level" value="100"/>
      <!-- <param name="sound-prefix" value="$${sound_prefix}"/> -->
      <param name="muted-sound" value="conference/conf-muted.wav"/>
      <param name="unmuted-sound" value="conference/conf-unmuted.wav"/>
      <param name="alone-sound" value="conference/conf-alone.wav"/>
      <param name="moh-sound" value="$${hold_music}"/>
      <param name="enter-sound" value="tone_stream://%(200,0,500,600,700)"/>
      <param name="exit-sound" value="tone_stream://%(500,0,300,200,100,50,25)"/>
      <param name="kicked-sound" value="conference/conf-kicked.wav"/>
      <param name="locked-sound" value="conference/conf-locked.wav"/>
      <param name="is-locked-sound" value="conference/conf-is-locked.wav"/>
      <param name="is-unlocked-sound" value="conference/conf-is-unlocked.wav"/>
      <param name="pin-sound" value="conference/conf-pin.wav"/>
      <param name="bad-pin-sound" value="conference/conf-bad-pin.wav"/>
      <param name="caller-id-name" value="$${outbound_caller_name}"/>
      <param name="caller-id-number" value="$${outbound_caller_id}"/>
      <param name="comfort-noise" value="true"/>

      <!-- <param name="conference-flags" value="video-floor-only|rfc-4579|livearray-sync|auto-3d-position|minimize-video-encoding"/> -->

      <!-- <param name="video-mode" value="mux"/> -->
      <!-- <param name="video-layout-name" value="3x3"/> -->
      <!-- <param name="video-layout-name" value="group:grid"/> -->
      <!-- <param name="video-canvas-size" value="1920x1080"/> -->
      <!-- <param name="video-canvas-bgcolor" value="#333333"/> -->
      <!-- <param name="video-layout-bgcolor" value="#000000"/> -->
      <!-- <param name="video-codec-bandwidth" value="2mb"/> -->
      <!-- <param name="video-fps" value="15"/> -->

    </profile>

    <profile name="video-mcu-stereo">
      <param name="domain" value="$${domain}"/>
      <param name="rate" value="48000"/>
      <param name="channels" value="2"/>
      <param name="interval" value="20"/>
      <param name="energy-level" value="200"/>
      <!-- <param name="tts-engine" value="flite"/> -->
      <!-- <param name="tts-voice" value="kal16"/> -->
      <param name="muted-sound" value="conference/conf-muted.wav"/>
      <param name="unmuted-sound" value="conference/conf-unmuted.wav"/>
      <param name="alone-sound" value="conference/conf-alone.wav"/>
      <param name="moh-sound" value="$${hold_music}"/>
      <param name="enter-sound" value="tone_stream://%(200,0,500,600,700)"/>
      <param name="exit-sound" value="tone_stream://%(500,0,300,200,100,50,25)"/>
      <param name="kicked-sound" value="conference/conf-kicked.wav"/>
      <param name="locked-sound" value="conference/conf-locked.wav"/>
      <param name="is-locked-sound" value="conference/conf-is-locked.wav"/>
      <param name="is-unlocked-sound" value="conference/conf-is-unlocked.wav"/>
      <param name="pin-sound" value="conference/conf-pin.wav"/>
      <param name="bad-pin-sound" value="conference/conf-bad-pin.wav"/>
      <param name="caller-id-name" value="$${outbound_caller_name}"/>
      <param name="caller-id-number" value="$${outbound_caller_id}"/>
      <param name="comfort-noise" value="false"/>
      <param name="conference-flags" value="livearray-json-status|json-events|video-floor-only|rfc-4579|livearray-sync|minimize-video-encoding|manage-inbound-video-bitrate|video-required-for-canvas|video-mute-exit-canvas|mute-detect"/>
      <param name="video-auto-floor-msec" value="1000"/>
      <param name="video-mode" value="mux"/>
      <param name="video-layout-name" value="3x3"/>
      <param name="video-layout-name" value="group:grid"/>
      <param name="video-canvas-size" value="1920x1080"/>
      <param name="video-canvas-bgcolor" value="#333333"/>
      <param name="video-layout-bgcolor" value="#000000"/>
      <param name="video-codec-bandwidth" value="3mb"/>
      <param name="video-fps" value="30"/>
      <!-- <param name="video-codec-config-profile-name" value="conference"/> -->
    </profile>

    <profile name="video-mcu-stereo-720">
      <param name="domain" value="$${domain}"/>
      <param name="rate" value="48000"/>
      <param name="channels" value="2"/>
      <param name="interval" value="20"/>
      <param name="energy-level" value="200"/>
      <!-- <param name="tts-engine" value="flite"/> -->
      <!-- <param name="tts-voice" value="kal16"/> -->
      <param name="muted-sound" value="conference/conf-muted.wav"/>
      <param name="unmuted-sound" value="conference/conf-unmuted.wav"/>
      <param name="alone-sound" value="conference/conf-alone.wav"/>
      <param name="moh-sound" value="$${hold_music}"/>
      <param name="enter-sound" value="tone_stream://%(200,0,500,600,700)"/>
      <param name="exit-sound" value="tone_stream://%(500,0,300,200,100,50,25)"/>
      <param name="kicked-sound" value="conference/conf-kicked.wav"/>
      <param name="locked-sound" value="conference/conf-locked.wav"/>
      <param name="is-locked-sound" value="conference/conf-is-locked.wav"/>
      <param name="is-unlocked-sound" value="conference/conf-is-unlocked.wav"/>
      <param name="pin-sound" value="conference/conf-pin.wav"/>
      <param name="bad-pin-sound" value="conference/conf-bad-pin.wav"/>
      <param name="caller-id-name" value="$${outbound_caller_name}"/>
      <param name="caller-id-number" value="$${outbound_caller_id}"/>
      <param name="comfort-noise" value="false"/>
      <param name="conference-flags" value="livearray-json-status|json-events|video-floor-only|rfc-4579|livearray-sync|minimize-video-encoding|manage-inbound-video-bitrate|video-required-for-canvas|video-mute-exit-canvas|mute-detect"/>
      <param name="video-auto-floor-msec" value="1000"/>
      <param name="video-mode" value="mux"/>
      <param name="video-layout-name" value="3x3"/>
      <param name="video-layout-name" value="group:grid"/>
      <param name="video-canvas-size" value="1280x720"/>
      <param name="video-canvas-bgcolor" value="#333333"/>
      <param name="video-layout-bgcolor" value="#000000"/>
      <param name="video-codec-bandwidth" value="3mb"/>
      <param name="video-fps" value="30"/>
    </profile>

    <profile name="video-mcu-stereo-480">
      <param name="domain" value="$${domain}"/>
      <param name="rate" value="48000"/>
      <param name="channels" value="2"/>
      <param name="interval" value="20"/>
      <param name="energy-level" value="200"/>
      <!-- <param name="tts-engine" value="flite"/> -->
      <!-- <param name="tts-voice" value="kal16"/> -->
      <param name="muted-sound" value="conference/conf-muted.wav"/>
      <param name="unmuted-sound" value="conference/conf-unmuted.wav"/>
      <param name="alone-sound" value="conference/conf-alone.wav"/>
      <param name="moh-sound" value="$${hold_music}"/>
      <param name="enter-sound" value="tone_stream://%(200,0,500,600,700)"/>
      <param name="exit-sound" value="tone_stream://%(500,0,300,200,100,50,25)"/>
      <param name="kicked-sound" value="conference/conf-kicked.wav"/>
      <param name="locked-sound" value="conference/conf-locked.wav"/>
      <param name="is-locked-sound" value="conference/conf-is-locked.wav"/>
      <param name="is-unlocked-sound" value="conference/conf-is-unlocked.wav"/>
      <param name="pin-sound" value="conference/conf-pin.wav"/>
      <param name="bad-pin-sound" value="conference/conf-bad-pin.wav"/>
      <param name="caller-id-name" value="$${outbound_caller_name}"/>
      <param name="caller-id-number" value="$${outbound_caller_id}"/>
      <param name="comfort-noise" value="false"/>
      <param name="conference-flags" value="livearray-json-status|json-events|video-floor-only|rfc-4579|livearray-sync|minimize-video-encoding|manage-inbound-video-bitrate|video-required-for-canvas|video-mute-exit-canvas|mute-detect"/>
      <param name="video-auto-floor-msec" value="1000"/>
      <param name="video-mode" value="mux"/>
      <param name="video-layout-name" value="3x3"/>
      <param name="video-layout-name" value="group:grid"/>
      <param name="video-canvas-size" value="640x480"/>
      <param name="video-canvas-bgcolor" value="#333333"/>
      <param name="video-layout-bgcolor" value="#000000"/>
      <param name="video-codec-bandwidth" value="3mb"/>
      <param name="video-fps" value="30"/>
    </profile>

    <profile name="video-mcu-stereo-320">
      <param name="domain" value="$${domain}"/>
      <param name="rate" value="48000"/>
      <param name="channels" value="2"/>
      <param name="interval" value="20"/>
      <param name="energy-level" value="200"/>
      <!-- <param name="tts-engine" value="flite"/> -->
      <!-- <param name="tts-voice" value="kal16"/> -->
      <param name="muted-sound" value="conference/conf-muted.wav"/>
      <param name="unmuted-sound" value="conference/conf-unmuted.wav"/>
      <param name="alone-sound" value="conference/conf-alone.wav"/>
      <param name="moh-sound" value="$${hold_music}"/>
      <param name="enter-sound" value="tone_stream://%(200,0,500,600,700)"/>
      <param name="exit-sound" value="tone_stream://%(500,0,300,200,100,50,25)"/>
      <param name="kicked-sound" value="conference/conf-kicked.wav"/>
      <param name="locked-sound" value="conference/conf-locked.wav"/>
      <param name="is-locked-sound" value="conference/conf-is-locked.wav"/>
      <param name="is-unlocked-sound" value="conference/conf-is-unlocked.wav"/>
      <param name="pin-sound" value="conference/conf-pin.wav"/>
      <param name="bad-pin-sound" value="conference/conf-bad-pin.wav"/>
      <param name="caller-id-name" value="$${outbound_caller_name}"/>
      <param name="caller-id-number" value="$${outbound_caller_id}"/>
      <param name="comfort-noise" value="false"/>
      <param name="conference-flags" value="livearray-json-status|json-events|video-floor-only|rfc-4579|livearray-sync|minimize-video-encoding|manage-inbound-video-bitrate|video-required-for-canvas|video-mute-exit-canvas|mute-detect"/>
      <param name="video-auto-floor-msec" value="1000"/>
      <param name="video-mode" value="mux"/>
      <param name="video-layout-name" value="3x3"/>
      <param name="video-layout-name" value="group:grid"/>
      <param name="video-canvas-size" value="480x320"/>
      <param name="video-canvas-bgcolor" value="#333333"/>
      <param name="video-layout-bgcolor" value="#000000"/>
      <param name="video-codec-bandwidth" value="3mb"/>
      <param name="video-fps" value="30"/>
    </profile>

    <profile name="sla">
      <param name="domain" value="$${domain}"/>
      <param name="rate" value="16000"/>
      <param name="interval" value="20"/>
      <param name="caller-controls" value="none"/>
      <param name="energy-level" value="200"/>
      <param name="moh-sound" value="silence"/>
        <param name="comfort-noise" value="true"/>
        </profile>

        </profiles>
        """
        return _CONFIGURATION_XML_TEMPLATE % ("conference", "conference", _content)

    def _callcenter_conf(self):
        _content = """
        <settings>
        </settings>
        {{queues}}
        {{agents}}
        {{tiers}}
        """
        _queues = self._search_callcenter_queues() or []
        _xmls = []
        for _queue in _queues:
            _xmls.append(self._callcenter_queue_xml(_queue))
        _queues = "<queues>%s\n</queues>" % "\n".join(_xmls)

        _agents = self._search_callcenter_agents() or []
        _xmls = []
        for _agent in _agents:            
            if not _agent.sip_number:
                continue
            if not _agent.has_group("odoo_freeswitch_cti.group_sip_user"):
                continue
            _xmls.append(self._callcenter_agent_xml(_agent))
        _agents = "<agents>%s\n</agents>" % "\n".join(_xmls)

        _tiers = self._search_callcenter_tiers() or []
        _xmls = []
        for _tier in _tiers:
            _xmls.append(self._callcenter_tier_xml(_tier))
        _tiers = "<tiers>%s\n</tiers>" % "\n".join(_xmls)

        _content = _content.replace("{{queues}}", _queues)
        _content = _content.replace("{{agents}}", _agents)
        _content = _content.replace("{{tiers}}", _tiers)

        _xml = _CONFIGURATION_XML_TEMPLATE % ("callcenter", "callcenter", _content)
        return _xml

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

    def _voicemail_conf(self):
        _content = """
        <settings>
        </settings>
        <profiles>
        <profile name="default">
        <param name="file-extension" value="wav"/>
        <param name="terminator-key" value="#"/>
        <param name="max-login-attempts" value="3"/>
        <param name="digit-timeout" value="10000"/>
        <param name="min-record-len" value="3"/>
        <param name="max-record-len" value="300"/>
        <param name="max-retries" value="3"/>
        <param name="tone-spec" value="%(1000, 0, 640)"/>
        <param name="callback-dialplan" value="XML"/>
        <param name="callback-context" value="default"/>
        <param name="play-new-messages-key" value="1"/>
        <param name="play-saved-messages-key" value="2"/>
        <!-- play-new-messages-lifo and play-saved-messages-lifo default is false, playing oldest messages first
	<param name="play-new-messages-lifo" value="false"/>
	<param name="play-saved-messages-lifo" value="false"/>
        -->
        <param name="login-keys" value="0"/>
        <param name="main-menu-key" value="0"/>
        <param name="config-menu-key" value="5"/>
        <param name="record-greeting-key" value="1"/>
        <param name="choose-greeting-key" value="2"/>
        <param name="change-pass-key" value="6"/>
        <param name="record-name-key" value="3"/>
        <param name="record-file-key" value="3"/>
        <param name="listen-file-key" value="1"/>
        <param name="save-file-key" value="2"/>
        <param name="delete-file-key" value="7"/>
        <param name="undelete-file-key" value="8"/>
        <param name="email-key" value="4"/>
        <param name="pause-key" value="0"/>
        <param name="restart-key" value="1"/>
        <param name="ff-key" value="6"/>
        <param name="rew-key" value="4"/>
        <param name="skip-greet-key" value="#"/>
        <param name="previous-message-key" value="1"/>
        <param name="next-message-key" value="3"/>
        <param name="skip-info-key" value="*"/>
        <param name="repeat-message-key" value="0"/>
        <param name="record-silence-threshold" value="200"/>
        <param name="record-silence-hits" value="2"/>
        <param name="web-template-file" value="web-vm.tpl"/>
        <param name="db-password-override" value="false"/>
        <param name="allow-empty-password-auth" value="true"/>
        <!-- if you need to change the sample rate of the recorded files e.g. gmail voicemail player -->
        <!--<param name="record-sample-rate" value="11025"/>-->
        <!-- the next two both must be set for this to be enabled
        the extension is in the format of <dest> [<dialplan>] [<context>]
        -->
        <param name="operator-extension" value="operator XML default"/>
        <param name="operator-key" value="9"/>
        <param name="vmain-extension" value="vmain XML default"/>
        <param name="vmain-key" value="*"/>
        <!-- playback created files as soon as they were recorded by default -->
        <!--<param name="auto-playback-recordings" value="true"/>-->
        <email>
	<param name="template-file" value="voicemail.tpl"/>
	<param name="notify-template-file" value="notify-voicemail.tpl"/>
	<!-- this is the format voicemail_time will have -->
        <param name="date-fmt" value="%A, %B %d %Y, %I %M %p"/>
        <param name="email-from" value="${voicemail_account}@${voicemail_domain}"/>
        </email>
        <!--<param name="storage-dir" value="$${storage_dir}"/>-->
        <!--<param name="odbc-dsn" value="dsn:user:pass"/>-->
        <!--<param name="record-comment" value="Your Comment"/>-->
        <!--<param name="record-title" value="Your Title"/>-->
        <!--<param name="record-copyright" value="Your Copyright"/>-->
        </profile>
        </profiles>
        """
        _xml = _CONFIGURATION_XML_TEMPLATE % ("voicemail", "voicemail", _content)
        return _xml

    def _loopback_conf(self):
        _content = ""
        _xml = _CONFIGURATION_XML_TEMPLATE % ("loopback", "loopback", _content)
        return _xml

    def _post_load_modules_conf(self):
        _content = "<modules></modules>"
        _xml = _CONFIGURATION_XML_TEMPLATE % ("loopback", "loopback", _content)
        return _xml

    def _switch_conf(self):
        _content = """
        <cli-keybindings>
        <key name="1" value="help"/>
        <key name="2" value="status"/>
        <key name="3" value="show channels"/>
        <key name="4" value="show calls"/>
        <key name="5" value="sofia status"/>
        <key name="6" value="reloadxml"/>
        <key name="7" value="console loglevel 0"/>
        <key name="8" value="console loglevel 7"/>
        <key name="9" value="sofia status profile internal"/>
        <key name="10" value="sofia profile internal siptrace on"/>
        <key name="11" value="sofia profile internal siptrace off"/>
        <key name="12" value="version"/>
        </cli-keybindings> 
  
        <default-ptimes>
        
        </default-ptimes>
  
        <settings>
        <param name="colorize-console" value="true"/>

        <param name="dialplan-timestamps" value="false"/>

        <!-- <param name="1ms-timer" value="true"/> -->
        <!-- <param name="switchname" value="freeswitch"/> -->
        <!-- <param name="cpu-idle-smoothing-depth" value="30"/> -->


        <!-- Maximum number of simultaneous DB handles open -->
        <param name="max-db-handles" value="50"/>
        <!-- Maximum number of seconds to wait for a new DB handle before failing -->
        <param name="db-handle-timeout" value="10"/>

        <!-- Minimum idle CPU before refusing calls -->
        <!-- <param name="min-idle-cpu" value="25"/> -->

        <!-- Interval between heartbeat events -->
        <!-- <param name="event-heartbeat-interval" value="20"/> -->

        <!--
	Max number of sessions to allow at any given time.
	
	NOTICE: If you're driving 28 T1's in a single box you should set this to 644*2 or 1288
	this will ensure you're able to use the entire DS3 without a problem.  Otherwise you'll
	be 144 channels short of always filling that DS3 up which can translate into waste.
        -->
        <param name="max-sessions" value="1000"/>

        <!--Most channels to create per second -->
        <param name="sessions-per-second" value="30"/>
        <!-- Default Global Log Level - value is one of debug,info,notice,warning,err,crit,alert -->
        <param name="loglevel" value="debug"/>

        <!-- Set the core DEBUG level (0-10) -->
        <!-- <param name="debug-level" value="10"/> -->

        <!-- <param name="sql-buffer-len" value="1m"/> -->
        <!-- <param name="max-sql-buffer-len" value="2m"/> -->        
        <!-- <param name="min-dtmf-duration" value="400"/> -->
        
        <!-- <param name="max-dtmf-duration" value="192000"/> -->
        
        <!-- <param name="default-dtmf-duration" value="2000"/> -->
        
        <param name="mailer-app" value="sendmail"/>
        <param name="mailer-app-args" value="-t"/>
        <param name="dump-cores" value="yes"/>

        <!-- <param name="verbose-channel-events" value="no"/> -->
        
        <!-- Enable clock nanosleep -->
        <!-- <param name="enable-clock-nanosleep" value="true"/> -->
        
        <!-- Enable monotonic timing -->
        <!-- <param name="enable-monotonic-timing" value="true"/> -->
        
        <!-- NEEDS DOCUMENTATION -->
        <!-- <param name="enable-softtimer-timerfd" value="true"/> -->
        <!-- <param name="enable-cond-yield" value="true"/> -->
        <!-- <param name="enable-timer-matrix" value="true"/> -->
        <!-- <param name="threaded-system-exec" value="true"/> -->
        <!-- <param name="tipping-point" value="0"/> -->
        <!-- <param name="timer-affinity" value="disabled"/> -->
        <!-- NEEDS DOCUMENTATION -->
        
        <!-- RTP port range -->
        <!-- <param name="rtp-start-port" value="16384"/> -->
        <!-- <param name="rtp-end-port" value="32768"/> -->
        
        <!-- Test each port to make sure it is not in use by some other process before allocating it to RTP -->
        <!-- <param name="rtp-port-usage-robustness" value="true"/> -->
        
        <param name="rtp-enable-zrtp" value="false"/>
        
        <!-- <param name="rtp-retain-crypto-keys" value="true"/> -->
        <!-- <param name="core-db-name" value="/dev/shm/core.db" /> -->
                
        <!-- Allow multiple registrations to the same account in the central registration table -->
        <!-- <param name="multiple-registrations" value="true"/> -->
        
        <!-- <param name="max-audio-channels" value="2"/> -->
        
        </settings>
        """
        _xml = _CONFIGURATION_XML_TEMPLATE % ("switch", "switch", _content)
        return _xml
        
    def _local_stream_conf(self):
        _content = """
        <!-- fallback to default if requested moh class isn't found -->
        <directory name="default" path="$${sounds_dir}/music/8000">
        <param name="rate" value="8000"/>
        <param name="shuffle" value="true"/>
        <param name="channels" value="1"/>
        <param name="interval" value="20"/>
        <param name="timer-name" value="soft"/>
        <!-- list of short files to break in with every so often -->
        <!--<param name="chime-list" value="file1.wav,file2.wav"/>-->
        <!-- frequency of break-in (seconds)-->
        <!--<param name="chime-freq" value="30"/>-->
        <!-- limit to how many seconds the file will play -->
        <!--<param name="chime-max" value="500"/>-->
        </directory>
        
        <directory name="moh/8000" path="$${sounds_dir}/music/8000">
        <param name="rate" value="8000"/>
        <param name="shuffle" value="true"/>
        <param name="channels" value="1"/>
        <param name="interval" value="20"/>
        <param name="timer-name" value="soft"/>
        </directory>
        
        <directory name="moh/16000" path="$${sounds_dir}/music/16000">
        <param name="rate" value="16000"/>
        <param name="shuffle" value="true"/>
        <param name="channels" value="1"/>
        <param name="interval" value="20"/>
        <param name="timer-name" value="soft"/>
        </directory>
        
        <directory name="moh/32000" path="$${sounds_dir}/music/32000">
        <param name="rate" value="32000"/>
        <param name="shuffle" value="true"/>
        <param name="channels" value="1"/>
        <param name="interval" value="20"/>
        <param name="timer-name" value="soft"/>
        </directory>
        
        <directory name="moh/48000" path="$${sounds_dir}/music/48000">
        <param name="rate" value="48000"/>
        <param name="shuffle" value="true"/>
        <param name="channels" value="1"/>
        <param name="interval" value="10"/>
        <param name="timer-name" value="soft"/>
        </directory>
        
        """
        return _CONFIGURATION_XML_TEMPLATE % ("local_stream", "local_stream", _content)

    def _sndfile_conf(self):
        _content = """
	<settings>      
	<param name="allowed-extensions" value="wav,raw,r8,r16"/>
	</settings>
        """
        return _CONFIGURATION_XML_TEMPLATE % ("sndfile", "sndfile", _content)

    def _shout_conf(self):
        _content = """
        <settings>
        <!-- Don't change these unless you are insane -->
        <!--<param name="decoder" value="i586"/>-->
        <!--<param name="volume" value=".1"/>-->
        <!--<param name="outscale" value="8192"/>-->
        </settings>
        """
        return _CONFIGURATION_XML_TEMPLATE % ("shout", "shout", _content)

    def _spandsp_conf(self):
        _content = """
        <modem-settings>
        
        <param name="total-modems" value="0"/>
        <param name="context" value="default"/>
        <param name="dialplan" value="XML"/>

        <!-- Extra tracing for debugging -->
        <param name="verbose" value="false"/>
        </modem-settings>

        <fax-settings>
	<param name="use-ecm"		value="true"/>
	<param name="verbose"		value="false"/>
	<!--param name="verbose-log-level"	value="INFO"/-->
	<param name="disable-v17"	value="false"/>
	<param name="ident"		value="SpanDSP Fax Ident"/>
	<param name="header"		value="SpanDSP Fax Header"/>

	<param name="spool-dir"		value="$${temp_dir}"/>
	<param name="file-prefix"	value="faxrx"/>
	<!-- How many packets to process before sending the re-invite on tx/rx -->
	<!-- <param name="t38-rx-reinvite-packet-count" value="50"/> -->
	<!-- <param name="t38-tx-reinvite-packet-count" value="100"/> -->
        </fax-settings>

        <descriptors>

        <!-- North America -->
        <descriptor name="1">
        <tone name="CED_TONE">
        <element freq1="2100" freq2="0" min="700" max="0"/>
        </tone>
        <tone name="SIT">
        <element freq1="950" freq2="0" min="256" max="400"/>
        <element freq1="1400" freq2="0" min="256" max="400"/>
        <element freq1="1800" freq2="0" min="256" max="400"/>
        </tone>
        <tone name="RING_TONE" description="North America ring">
        <element freq1="440" freq2="480" min="1200" max="0"/>
       </tone>
        <tone name="REORDER_TONE">
        <element freq1="480" freq2="620" min="224" max="316"/>
        <element freq1="0" freq2="0" min="168" max="352"/>
        <element freq1="480" freq2="620" min="224" max="316"/>
        </tone>
        <tone name="BUSY_TONE">
        <element freq1="480" freq2="620" min="464" max="536"/>
        <element freq1="0" freq2="0" min="464" max="572"/>
        <element freq1="480" freq2="620" min="464" max="536"/>
        </tone>
        </descriptor>
        
        <!-- United Kingdom -->
        <descriptor name="44">
        <tone name="CED_TONE">
        <element freq1="2100" freq2="0" min="500" max="0"/>
        </tone>
        <tone name="SIT">
        <element freq1="950" freq2="0" min="256" max="400"/>
        <element freq1="1400" freq2="0" min="256" max="400"/>
        <element freq1="1800" freq2="0" min="256" max="400"/>
        </tone>
        <tone name="REORDER_TONE">
        <element freq1="400" freq2="0" min="368" max="416"/>
        <element freq1="0" freq2="0" min="336" max="368"/>
        <element freq1="400" freq2="0" min="256" max="288"/>
        <element freq1="0" freq2="0" min="512" max="544"/>
        </tone>
        <tone name="BUSY_TONE">
        <element freq1="400" freq2="0" min="352" max="384"/>
        <element freq1="0" freq2="0" min="352" max="384"/>
        <element freq1="400" freq2="0" min="352" max="384"/>
        <element freq1="0" freq2="0" min="352" max="384"/>
        </tone>
        </descriptor>
        
        <!-- Germany -->
        <descriptor name="49">
        <tone name="CED_TONE">
        <element freq1="2100" freq2="0" min="500" max="0"/>
        </tone>
        <tone name="SIT">
        <element freq1="900" freq2="0" min="256" max="400"/>
        <element freq1="1400" freq2="0" min="256" max="400"/>
        <element freq1="1800" freq2="0" min="256" max="400"/>
        </tone>
        <tone name="REORDER_TONE">
        <element freq1="425" freq2="0" min="224" max="272"/>
        <element freq1="0" freq2="0" min="224" max="272"/>
        </tone>
        <tone name="BUSY_TONE">
        <element freq1="425" freq2="0" min="464" max="516"/>
        <element freq1="0" freq2="0" min="464" max="516"/>
        </tone>
        </descriptor>
        </descriptors>
        """
        return _CONFIGURATION_XML_TEMPLATE % ("spandsp", "spandsp", _content)

    def _opus_conf(self):
        _content = """
        <settings>
        <param name="use-vbr" value="1"/>
        <!--<param name="use-dtx" value="1"/>-->
        <param name="complexity" value="10"/>
	<!-- Set the initial packet loss percentage 0-100 -->
        <!--<param name="packet-loss-percent" value="10"/>-->
	<!-- Support asymmetric sample rates -->
        <!--<param name="asymmetric-sample-rates" value="1"/>-->

	<!-- Enable bitrate negotiation -->
        <!--<param name="bitrate-negotiation" value="1"/>-->

	<!-- Keep FEC Enabled -->
        <param name="keep-fec-enabled" value="1"/>
	<!--<param name="use-jb-lookahead" value="true"/> -->
        <!--
           maxaveragebitrate: the maximum average codec bitrate (values: 6000 to 510000 in bps) 0 is not considered
           maxplaybackrate: the maximum codec internal frequency (values: 8000, 12000, 16000, 24000, 48000 in Hz) 0 is not considered
           This will set the local encoder and instruct the remote encoder trough specific "fmtp" attibute in the SDP.

           Example: if you receive "maxaveragebitrate=20000" from SDP and you have set "maxaveragebitrate=24000" in this configuration
                    the lowest will prevail in this case "20000" is set on the encoder and the corresponding fmtp attribute will be set
                    to instruct the remote encoder to do the same.
        -->
        <param name="maxaveragebitrate" value="0"/>
        <param name="maxplaybackrate" value="0"/>
	<!-- Max capture rate, 8000, 12000, 16000, 24000 and 48000 are valid options -->
        <!--<param name="sprop-maxcapturerate" value="0"/>-->
	<!-- Enable automatic bitrate variation during the call based on RTCP feedback -->
	<!--<param name="adjust-bitrate" value="1"/>-->
	<!-- will enforce mono even if the remote party wants stereo. must be used in conjunction with param "max-audio-channels" set to 1 in switch.conf.xml. -->
		<param name="mono" value="0"/>
        </settings>
        
        """
        return _CONFIGURATION_XML_TEMPLATE % ("opus", "opus", _content)

    def _amr_conf(self):
        _content = """
	<settings>
	<!-- AMR modes (supported bitrates) :
        mode   0     AMR 4.75  kbps
        mode   1     AMR 5.15  kbps
        mode   2     AMR 5.9 kbps
        mode   3     AMR 6.7 kbps
        mode   4     AMR 7.4  kbps
        mode   5     AMR 7.95 kbps 
        mode   6     AMR 10.2 kbps 
        mode   7     AMR 12.2 kbps
        -->
	<param name="default-bitrate" value="7"/> 
	<!-- Enable VoLTE specific FMTP -->
	<param name="volte" value="0"/>
	<!-- Enable automatic bitrate variation during the call based on RTCP feedback -->
	<param name="adjust-bitrate" value="0"/> 
	<!-- force OA when originating -->
	<param name="force-oa" value="0"/> 
	</settings>
        """
        return _CONFIGURATION_XML_TEMPLATE % ("amr", "amr", _content)        

    def _hash_conf(self):
        _content = """
        <remotes>
        </remotes>
        """
        return _CONFIGURATION_XML_TEMPLATE % ("hash", "hash", _content)        

    def _fifo_conf(self):
        _content = """
        <settings>
        <param name="delete-all-outbound-member-on-startup" value="false"/>
        </settings>
        <fifos>
        <fifo name="cool_fifo@$${domain}" importance="0">
        <!--<member timeout="60" simo="1" lag="20">{member_wait=nowait}user/1005@$${domain}</member>-->
        </fifo>
        </fifos>

        """
        return _CONFIGURATION_XML_TEMPLATE % ("fifo", "fifo", _content)        
    
    def _db_conf(self):
        _content = """
        <settings>
        <!--<param name="odbc-dsn" value="dsn:user:pass"/>-->
        </settings>
        """
        return _CONFIGURATION_XML_TEMPLATE % ("db", "db", _content)
        
    # def _timezones_conf(self):
    #     _path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../freeswitch/conf/timezones.conf.xml")
    #     with open(_path, "r") as _file:
    #         _content = _file.read(_content)
    #     return _content

    def _verto_conf(self):
        _content = """
        <settings>
        <param name="debug" value="0"/>
        <!-- <param name="kslog" value="true"/> -->
        <!-- seconds to wait before hanging up a disconnected channel -->
        <!-- <param name="detach-timeout-sec" value="120"/> -->
        <!-- enable broadcasting all FreeSWITCH events in Verto -->
        <!-- <param name="enable-fs-events" value="false"/> -->
        <!-- enable broadcasting FreeSWITCH presence events in Verto -->
        <!-- <param name="enable-presence" value="true"/> -->
        </settings>

        <profiles>
        <profile name="default-v4">
        <param name="bind-local" value="$${local_ip_v4}:8081"/>
        <param name="bind-local" value="$${local_ip_v4}:8082" secure="true"/>
        <param name="force-register-domain" value="$${domain}"/>
        <param name="secure-combined" value="$${certs_dir}/wss.pem"/>
        <param name="secure-chain" value="$${certs_dir}/wss.pem"/>
        <param name="userauth" value="true"/>
        <!-- setting this to true will allow anyone to register even with no account so use with care -->
        <param name="blind-reg" value="false"/>
        <param name="mcast-ip" value="224.1.1.1"/>
        <param name="mcast-port" value="1337"/>
        <param name="rtp-ip" value="$${local_ip_v4}"/>
        <param name="ext-rtp-ip" value="$${external_rtp_ip}"/>
        <param name="local-network" value="localnet.auto"/>
        <param name="outbound-codec-string" value="opus,h264,vp8"/>
        <param name="inbound-codec-string" value="opus,h264,vp8"/>
        
        <param name="apply-candidate-acl" value="localnet.auto"/>
        <param name="apply-candidate-acl" value="wan_v4.auto"/>
        <param name="apply-candidate-acl" value="rfc1918.auto"/>
        <param name="apply-candidate-acl" value="any_v4.auto"/>
        <param name="timer-name" value="soft"/>
        </profile>
        
        </profiles>

        """
        return _CONFIGURATION_XML_TEMPLATE % ("verto", "verto", _content)
        
    @http.route('/freeswitch_xml_curl/configuration', type='http', auth='none', csrf=False)
    def configuration(self, *args, **kw):
        _logger.info("Configuration: [%s]" % http.request.params)

        if not self._is_hostname_matched():
            return _EMPTY_XML

        if not self._is_section_name_matched("configuration"):
            return _EMPTY_XML

        if self._is_key_value("json_cdr.conf"):
            return self._json_cdr_conf()

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
            return self._voicemail_conf()

        if self._is_key_value("loopback.conf"):
            return self._loopback_conf()

        if self._is_key_value("post_load_modules.conf"):
            return self._post_load_modules_conf()

        if self._is_key_value("switch.conf"):
            return self._switch_conf()

        if self._is_key_value("local_stream.conf"):
            return self._local_stream_conf()

        if self._is_key_value("shout.conf"):
            return self._shout_conf()

        if self._is_key_value("sndfile.conf"):
            return self._sndfile_conf()

        if self._is_key_value("opus.conf"):
            return self._opus_conf()

        if self._is_key_value("spandsp.conf"):
            return self._spandsp_conf()

        if self._is_key_value("amr.conf"):
            return self._amr_conf()

        if self._is_key_value("hash.conf"):
            return self._hash_conf()

        if self._is_key_value("fifo.conf"):
            return self._fifo_conf()

        if self._is_key_value("db.conf"):
            return self._db_conf()

        if self._is_key_value("verto.conf"):
            return self._verto_conf()

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


