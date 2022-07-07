Download Odoo from Github

git clone https://github.com/odoo/odoo.git

cd odoo
pip install -r requirments.txt

some_odoo_config
```
[options]
# change addon path
addons_path = /home/dding/odoo-github/odoo-15/odoo/addons,/home/dding/odoo-github/odoo-15/addons,/home/dding/odoo-github/odoo-github-addons
admin_passwd = admin
csv_internal_sep = ,
# change data_dir
data_dir = /home/dding/.local/share/Odoo
db_host = False
db_maxconn = 64

# change db_name
db_name = dding_odoo_10
db_password = x
db_port = False
db_sslmode = prefer
db_template = template0
db_user = dding
dbfilter = 
demo = {}
dev = all
email_from = False
from_filter = False
geoip_database = /usr/share/GeoIP/GeoLite2-City.mmdb
http_enable = True
http_interface = 
http_port = 8069
import_partial = 
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_request = 8192
limit_time_cpu = 60
limit_time_real = 120
limit_time_real_cron = -1
list_db = True
log_db = False
log_db_level = warning
log_handler = :INFO
log_level = info
logfile = 
longpolling_port = 8072
max_cron_threads = 2
osv_memory_age_limit = False
osv_memory_count_limit = 0
pg_path = 
pidfile = 
proxy_mode = True
reportgz = False
screencasts = 
screenshots = /tmp/odoo_tests
server_wide_modules = base,web
smtp_password = False
smtp_port = 25
smtp_server = localhost
smtp_ssl = False
smtp_ssl_certificate_filename = False
smtp_ssl_private_key_filename = False
smtp_user = False
syslog = False
test_enable = False
test_file = 
test_tags = None
transient_age_limit = 1.0
translate_modules = ['all']
unaccent = False
upgrade_path = 
without_demo = all
#workers = 4
x_sendfile = False

```

Download odoo_freeswitch_cti into an addon path.

```
cd /home/dding/odoo-github/odoo-github-addons
https://github.com/dingguijin/odoo_freeswitch_cti.git
```


Run Odoo first
```
./odoo-bin -c some_odoo_config
```

Then Run FreeSWITCH

```
cd /usr/local/freeswitch/bin
./freeswitch -nonat -c
```

Access Odoo

open browser http://localhost:8069
admin/admin to login Odoo

Install odoo_freeswitch_cti

Mai Menu->Apps->search cti->install

Access Odoo Callcenter

Main Menu->Settings->Users/Company

Add internal user and change to Callcenter User and set sip_number/sip_password.

Prepare a softphone or an IP Phone device.

Setting up the ip phone to login sip server (FreeSwitch).

Change Dialplan

Main Menu->CallCenter->Callcenter Dialplan->Open Dialplan form->Switch to dialplan View



