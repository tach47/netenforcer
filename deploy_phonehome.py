#!/usr/bin/env python3

import os
import sys
import yaml
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.utils.scp import SCP

sys.path.append(os.path.abspath('..'))

import py_onepassword.op as op

CONFIGS = {}
DEVICE_LIST = {}


def generate_device_list():
    global DEVICE_LIST
    with open('devices.yaml', 'r') as f:
        devices = yaml.safe_load(f.read())['devices']
    DEVICE_LIST = devices
    return devices


def set_timer(dev):
    print("%s: Setting daily event options" % dev.hostname)
    with Config(dev, mode="private") as ch:
        ch.load('set event-options generate-event phoneHome time-of-day "%s"' % CONFIGS['daily_check_time'], format='set')
        ch.load('set event-options policy phoneHome.py events phoneHome', format='set')
        ch.load('set event-options policy then execute-commands commands "op phonehome.py"', format='set')
        ch.pdiff()
        ch.commit(comment="Applying event timer configs for phonehome.py")


def enable_script(dev):
    print("%s: Adding python script configs" % dev.hostname)
    with Config(dev, mode="private") as ch:
        ch.load('set system scripts language python3', format='set')
        ch.load('set system scripts op file phonehome.py', format='set')
        ch.pdiff()
        ch.commit(comment="Enabling python3 and adding 'phonehome.py' op script")


def scp_scripts(dev):
    print("%s: SCPing scripts and phonehome_config.yaml" % dev.hostname)
    with SCP(dev, progress=True) as scp:
        scp.put("phonehome/phonehome_config.yaml", remote_path="/var/db/scripts/op/")
        scp.put("phonehome/phonehome.py", remote_path="/var/db/scripts/op/")


def bootstrap():
    global CONFIGS
    with open("phonehome/phonehome_config.yaml", "r") as f:
        CONFIGS = yaml.safe_load(f.read())


def main():
    bootstrap()
    devices = generate_device_list()
    for device in devices:
        device_info = DEVICE_LIST['%s' % hostname]
        with Device(host=device_info['hostname'],
                    user=op.get_username(device_info['1password_title']),
                    passwd=op.get_password(device_info['1password_title'])) as dev:
            scp_scripts(dev)
            enable_script(dev)
            set_timer(dev)


if __name__ == '__main__':
    main()