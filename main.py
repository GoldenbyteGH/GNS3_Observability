#!/home/gbadmin/Dev/NETLabs/venv/bin/python
"""

GNS3 lab builder:
    This script define graphs and sessions for all virtual devices into GNS3
    lab topology
"""
from dotenv import load_dotenv
from LibreNMS import LibreNMS
from TIGtools import Flex_telegraf, Flex_grafana
import os

load_dotenv()


class NetDevice:
    def __init__(self, hostname, tftp_path=os.getenv('TFTP_PATH')):
        self.hostname = hostname
        self.interfaces = []
        self.tftp_path = tftp_path

    def addinterfaces(self, ifalias, ifname, ip):
        if 'Lo' not in ifname:
            self.interfaces.append((ifalias, ifname, ip))

    def del_tftp_conf(self):
        try:
            os.remove(os.path.join(self.tftp_path, self.hostname))
        except FileNotFoundError:
            return 404

    def add_tftp_conf(self, extension='-config'):
        open(os.path.join(self.tftp_path, self.hostname+extension), 'w')

    def count_ifs(self):
        return len(self.interfaces)


lab_net = LibreNMS()
device_list = []
f_addresses = []
# get flex devices from LNMS
lab_devices = lab_net.get_flex_devices_ip(lab_net.get_flex_ids())

for ld in lab_devices:
    netdevice = NetDevice(ld[0])
    device_list.append(netdevice)

for device in device_list:
    # delete old flex tftp conf
    device.del_tftp_conf()
# delete old flex devices
lab_net.del_flex_devices(lab_net.get_flex_ids())

# clear old obj list
device_list.clear()

# add flex devices +  tftp_conf
lab_net.scan_flex_devices()
lab_devices = lab_net.get_flex_devices_ip(lab_net.get_flex_ids())
print(len(lab_devices))
# todo--> inside class?
for ld in lab_devices:
    netdevice = NetDevice(ld[0])
    for interface in ld[1]['addresses']:
        port_alias = lab_net.get_port_by_id(interface['port_id'])['ifDescr']
        port_name = lab_net.get_port_by_id(interface['port_id'])['ifName']


        netdevice.addinterfaces(port_alias, port_name, interface['ipv4_address'])

        if lab_net.flex_net.strip('0') in interface['ipv4_address']:
            f_addresses.append(interface['ipv4_address'])

    device_list.append(netdevice)
#
#    except Exception as error:
#        print(error)
#        print('errore')
#        exit()
#
# create device_config in tftpboot
for device in device_list:
    device.add_tftp_conf()

# update telegraf
flex_tg = Flex_telegraf(tg_conf=open(os.getenv('TELEGRAF_SNMP_FILE'), 'w'))
flex_tg.confapply(influx_ip=os.getenv('INFLUX_IP'),
                  influx_port=os.getenv('INFLUX_PORT'),
                  flex_ips=f_addresses)

# generate grafana dashboard
flex_grf = Flex_grafana()
flex_grf.build_dash(device_list)

# restart containers
os.system('docker restart telegraf-snmp')
os.system('docker restart influxdb-snmp')


