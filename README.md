# HS110-InfluxDB-2.0-Script
This is meant to be a simple script that polls the power usage of the TP-Link HS110 Smart socker and stores the information in InfluxDB 2.0

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