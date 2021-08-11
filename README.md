# HS110-InfluxDB-2.0-Script
This is meant to be a simple script that polls the power usage of the TP-Link HS110 Smart socker and stores the information in InfluxDB 2.0

This sceipt requires the following python packages:
```
python3 -m pip install pyyaml 'influxdb-client[ciso]' python-kasa --pre
```

This script expects a yaml config file. Below is an example:

```yaml
influx_db:
  org: "<>"
  token: "<>"
  server_ip: "<>"
  server_port: "<>"
  bucket: "<>"

sockets:
  - "xxx.xxx.xxx.xxx"
  - ...
```

For every socket that you want to poll, add an entry to `sockets` with its IP address.
The name of the socket that was given to the device in the TP-Link Kasa app, will be used to filter in InfluxDB 2.0.

I run this script as a cronjob, every 30 seconds.
Because crontab does not go down to sub-minute resolutions, the second line is added.

```
# Need these to run on 30-sec boundaries, keep commands in sync.
* * * * *              /usr/bin/python3 /path/to/script/HS11_poller.py >/dev/null 2>&1
* * * * * ( sleep 30 ; /usr/bin/python3 /path/to/script/HS11_poller.py >/dev/null 2>&1 )
```
When running the script through cron, it might not be able to find it's config with a relative path. If so, simply change the line where it opens the config file to an absolute path.
