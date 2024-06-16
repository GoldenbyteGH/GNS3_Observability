"""
This script use LNMS as a device collector to monitor devices from lab
network

Requirements vars from .env:
    - LIBRENMS_URL
    - LIBRENMS_TOKEN
    - FLEX_NET          # lab network
    - container         # container_name: 'librenms' as default

"""


from dotenv import load_dotenv
from time import sleep
import requests
import os
import json


load_dotenv()

class LibreNMS:
    def __init__(self, librenms_url=os.getenv('LIBRENMS_URL'), container="librenms"):
        self.headers = {'X-Auth-Token': os.getenv('LIBRENMS_TOKEN')}
        self.librenms_url = librenms_url
        self.container = container
        self.flex_net = os.getenv('FLEX_NET')

    def get_flex_ids(self):
        nms_devices = requests.get(
            "{}/api/v0/devices".format(self.librenms_url),
            headers=self.headers)
        devices = json.loads(nms_devices.text)
        flex_ids = []
        for device in devices['devices']:
            if self.flex_net.strip('0') in device['ip']:
                flex_ids.append((device['hostname'][:-4], device['device_id']))

        return (flex_ids)

    def del_flex_devices(self, flex_ids):
        print('{} devices are going to be delete'.format(len(flex_ids)))
        for flex in flex_ids:
            requests.delete(
                "{}/api/v0/devices/{}".format(self.librenms_url, flex[1]),
                headers=self.headers)

    def get_flex_devices_ip(self, flex_ids):
        IPs = []
        for flex in flex_ids:
            while (True):
                sleep(0.5)
                req = json.loads(requests.get(
                        "{}/api/v0/devices/{}/ip".format(self.librenms_url, flex[1]),
                        headers=self.headers).text)
                # check LibreNMS data consistency 
                if req['status'] == 'ok':
                    break
            IPs.append((flex[0],req))
        print(IPs)
        return (IPs)

    def get_port_by_id(self, port_id):
        return (json.loads(requests.get(
                "{}/api/v0/ports/{}".format(
                    self.librenms_url, port_id),  headers=self.headers).text)['port'][0])

    def scan_flex_devices(self):
        os.system('docker exec -i {} sh -c \
                  "python /opt/librenms/snmp-scan.py"'.format(self.container))


# lab_net = LibreNMS()
# lab_net.del_flex_devices(lab_net.get_flex_ids())
# scan new devices
# lab_net.scan_flex_devices()
# lab_devices=lab_net.get_flex_devices_ip(lab_net.get_flex_ids())
# print(len(lab_devices))
# for ld in lab_devices:
#    print(ld[0])
#    for interface in ld[1]['addresses']:
#        print(lab_net.get_port_by_id(interface['port_id'])['ifDescr'] + ' : ' + interface['ipv4_address'])
