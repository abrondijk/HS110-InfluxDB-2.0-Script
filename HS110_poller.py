import asyncio
from kasa import Discover, SmartPlug
import sys
from time import sleep
from influxdb_client import InfluxDBClient, WriteApi, WriteOptions
from pprint import pformat as pf


def on_exit(db_client: InfluxDBClient, write_api: WriteApi):
    """Close clients after terminate a script.

    :param db_client: InfluxDB client
    :param write_api: WriteApi
    :return: nothing
    """
    write_api.__del__()
    db_client.__del__()


async def main():
    if len(sys.argv) == 0:
        print("Argument missing. Usage:")
        print("HS110_poller.py <broadcast ip>")

    broadcast_ip = sys.argv[1]

    devices = await Discover.discover(target=broadcast_ip)

    # Create empty arrays to store potential data
    device_names = []
    device_power = []

    sleep(30)

    for addr, dev in devices.items():
        plug = SmartPlug(addr)
        await plug.update()
        power = await plug.get_emeter_realtime()
        device_names.append(dev.alias)
        device_power.append(power['power_mw'])
        print(dev.alias)
        print(power['power_mw'])


def on_exit(db_client: InfluxDBClient, write_api: WriteApi):
    """Close clients after terminate a script
    :param db_client: InfluxDB client
    :param write_api: WriteApi
    :return: nothing
    """
    write_api.close()
    db_client.close()


def line_protocol(temperature):
    """Create a InfluxDB line protocol with structure:

        iot_sensor,hostname=mine_sensor_12,type=temperature value=68

    :param temperature: the sensor temperature
    :return: Line protocol to write into InfluxDB
    """

    import socket
    return 'iot_sensor,hostname={},type=temperature value={}'.format(socket.gethostname(), temperature)


if __name__ == "__main__":
    asyncio.run(main())
