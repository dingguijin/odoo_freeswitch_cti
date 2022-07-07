安装FreeSWITCH,参考FreeSWITCH网站

https://freeswitch.org/confluence/display/FREESWITCH/Installation


自己编译

git clone https://github.com/freeswitch/sofia-sip.git
git clone https://github.com/freeswitch/spandsp.git
git clone https://github.com/signalwire/freeswitch.git

cd sofia-sip
./bootstrap.sh
./configure
make
make install

cd spandsp
./bootstrap.sh
./configure
make
make install

cd freeswitch
vi modules.conf

```
applications/mod_callcenter
applications/mod_commands
applications/mod_conference
applications/mod_dptools
applications/mod_expr
applications/mod_fifo
applications/mod_hash
applications/mod_spandsp
applications/mod_spy

applications/mod_test
applications/mod_valet_parking
applications/mod_voicemail
applications/mod_voicemail_ivr
codecs/mod_amr
codecs/mod_b64
codecs/mod_g723_1
codecs/mod_g729
codecs/mod_h26x
codecs/mod_opus
databases/mod_pgsql
dialplans/mod_dialplan_xml
dialplans/mod_loopback
dialplans/mod_rtc
endpoints/mod_skinny
endpoints/mod_sofia
endpoints/mod_verto

event_handlers/mod_event_socket
event_handlers/mod_json_cdr

formats/mod_local_stream
formats/mod_native_file
formats/mod_png
formats/mod_shout
formats/mod_sndfile
formats/mod_tone_stream
loggers/mod_console
loggers/mod_logfile
xml_int/mod_xml_curl
```

./bootstrap.sh
./configure
make
make install
make sounds-install

cd /usr/local/freeswitch/conf

vi autoload_config/modules.conf.xml
```
<configuration name="modules.conf" description="Modules">
  <modules>
    <load module="mod_console"/>
    <load module="mod_logfile"/>
    <load module="mod_xml_curl"/>
    <load module="mod_event_socket"/>
    <load module="mod_sofia"/>
    <load module="mod_loopback"/>
    <load module="mod_rtc"/>
    <load module="mod_verto"/>
    <load module="mod_json_cdr"/>

    <load module="mod_commands"/>
    <load module="mod_conference"/>
    <load module="mod_dptools"/>
    <load module="mod_expr"/>
    <load module="mod_fifo"/>
    <load module="mod_hash"/>
    <load module="mod_voicemail"/>
    <load module="mod_valet_parking"/>
    <load module="mod_dialplan_xml"/>


   <!-- Codec Interfaces -->
    <load module="mod_spandsp"/>
    <load module="mod_g723_1"/>
    <load module="mod_g729"/>
    <load module="mod_amr"/>
    <load module="mod_b64"/>
    <load module="mod_opus"/>

    <!-- File Format Interfaces -->
    <load module="mod_sndfile"/>
    <load module="mod_native_file"/>
    <!--<load module="mod_opusfile"/>-->
    <load module="mod_png"/>
    <load module="mod_shout"/>
    <!--For local streams (play all the files in a directory)-->
    <load module="mod_local_stream"/>
    <load module="mod_tone_stream"/>

    <load module="mod_callcenter"/>

  </modules>
</configuration>
```

vi autoload_configs/xml_curl.conf.xml

```
<configuration name="xml_curl.conf" description="cURL XML Gateway">
  <bindings>
    <binding name="dialplan">
      <param name="gateway-url" value="http://localhost:8069/freeswitch_xml_curl/dialplan" bindings="dialplan"/>
    </binding>
    <binding name="directory">
      <param name="gateway-url" value="http://localhost:8069/freeswitch_xml_curl/directory" bindings="directory"/>
    </binding>
    <binding name="configuration">
      <param name="gateway-url" value="http://localhost:8069/freeswitch_xml_curl/configuration" bindings="configuration"/>
    </binding>
  </bindings>
</configuration>
```
