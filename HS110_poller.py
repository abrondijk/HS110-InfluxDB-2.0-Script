import asyncio
from kasa import SmartPlug
from influxdb_client import InfluxDBClient, WriteOptions
import yaml


async def main():
    read_config()

    if len(config['sockets']) == 0:
        print("Faulty config, no sockets defined")
        exit()

    devices = []

    for addr in config['sockets']:
        devices.append(SmartPlug(addr))

    device_names = []
    device_power = []

    device_num = len(devices)

    client = InfluxDBClient(url="http://{}:{}".format(config['influx_db']['server_ip'], config['influx_db']['server_port']),
                            token=config['influx_db']['token'], org=config['influx_db']['org'],
                            debug=False)

    if device_num != 0:
        device_names, device_power = await get_device_properties(devices)
    else:
        print("No devices found")
        exit()

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

        # Store the measured power in miliwatts
        device_power.append(power['power_mw'])
        print(device.alias)
        print(power['power_mw'])

    return device_names, device_power


def line_protocol(device_name, device_power):
    """Create a InfluxDB line protocol with structure:

        homelab_power,hostname=device_name,type=power value=68

    :param device_name: the device name
    :param device_power: the socket power
    :return: Line protocol to write into InfluxDB
    """

    # device_power comes in miliwatts, conversion to watts
    device_power /= 1000
    return 'homelab_power,hostname={},type=power value={}'.format(device_name, device_power)


def read_config():
    with open(r'./config.yml') as file:
        global config
        config = yaml.load(file, Loader=yaml.FullLoader)


def write_to_influx(client, line_data):
    write_api = client.write_api(write_options=WriteOptions(batch_size=2))

    print(write_api.write(config['influx_db']['bucket'], config['influx_db']['org'], line_data))


if __name__ == "__main__":
    asyncio.run(main())
