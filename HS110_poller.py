import asyncio
from kasa import SmartPlug
from influxdb_client import InfluxDBClient, WriteOptions
import yaml


async def main():
    read_config()

    device_num = len(config['sockets'])

    if device_num == 0:
        print("Faulty config, no sockets defined")
        exit()

    devices = []

    for addr in config['sockets']:
        devices.append(SmartPlug(addr))

    client = InfluxDBClient(url="http://{}:{}".format(config['influx_db']['server_ip'], config['influx_db']['server_port']),
                            token=config['influx_db']['token'], org=config['influx_db']['org'],
                            debug=False)

    device_names, device_power = await get_device_properties(devices)

    # Create datapoints according to line procotol
    influx_data = []
    for i in range(0, device_num):
        influx_data.append(line_protocol(device_names[i], device_power[i]))

    write_to_influx(client, influx_data)


async def get_device_properties(devices):
    """Gets the names and power in miliwatts from the devices

    :param devices: array of devices
    :return: array of device names and array of power in mW
    """

    # Create empty arrays to store potential data
    device_names = []
    device_power = []

    for device in devices:
        await device.update()
        power = await device.get_emeter_realtime()

        # Store the name of the device
        device_names.append(device.alias)

        # Store the measured power in watts, convert from miliwatts
        device_power.append(power['power_mw'] / 1000)
        print("Power for device %s: %d" % (device.alias, power['power_mw'] / 1000))

    return device_names, device_power


def line_protocol(device_name, device_power):
    """Create a datapoint according to the line protocol:

    :param device_name: the device name
    :param device_power: the socket power
    :return: Line protocol to write into InfluxDB
    """

    return 'homelab_power,hostname={},type=power value={}'.format(device_name, device_power)


def read_config():
    """Read a yaml config file:

        :return: Line protocol to write into InfluxDB
        """

    with open(r'./config.yml') as file:
        global config
        config = yaml.load(file, Loader=yaml.FullLoader)


def write_to_influx(client, line_data):
    """Push data to influxdb2.0:

        :param client: influxdb_client instance
        :param line_data: array of datapoints according to the line protocol
        :return: Line protocol to write into InfluxDB
        """

    write_api = client.write_api(write_options=WriteOptions(batch_size=2))

    write_api.write(config['influx_db']['bucket'], config['influx_db']['org'], line_data)


if __name__ == "__main__":
    asyncio.run(main())
