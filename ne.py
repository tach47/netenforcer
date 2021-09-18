#!/usr/bin/env python3

import json
import os
import sys

import yaml
from jnpr.junos import Device
from jnpr.junos.utils.sw import SW
from jnpr.junos.exception import ConnectAuthError, ConnectError

sys.path.append(os.path.abspath('..'))

import py_onepassword.op as op
from utils import utils

JUNOS_VERSIONS = ''
DEVICE_LIST = {}
upgrades_queued = []


def generate_device_list():
    global DEVICE_LIST
    with open('devices.yaml', 'r') as f:
        devices = yaml.safe_load(f.read())['devices']
    DEVICE_LIST = devices
    return devices


def get_version_and_model(device):
    print("%s: collecting info" % device['hostname'])
    try:
        with Device(host=device['hostname'], 
                    user=op.get_username(device['1password_title']),
                    passwd=op.get_password(device['1password_title'])) as dev:
            _ = dev.facts
            facts = dev.facts
            _ = facts['version']
    except ConnectAuthError as err:
        sys.exit('Connection failure: %s' % err)
    return (device['hostname'], facts['version'], facts['model'])


def load_version_map():
    global JUNOS_VERSIONS
    with open('hw_sw_mappings.yaml', 'r') as f:
        JUNOS_VERSIONS = yaml.safe_load(f.read())


def upgrade_device(device_map):
    hostname = device_map['hostname']
    software = device_map['sw']
    reboot_time = device_map['reboot_time']
    software = "firmware/%s" % software
    device_info = DEVICE_LIST['%s' % hostname]
    try:
        with Device(host=device_info['hostname'],
                    user=op.get_username(device_info['1password_title']),
                    passwd=op.get_password(device_info['1password_title'])) as dev:
            sw = SW(dev)
            print("%s: Pushing package %s and installing, with a reboot time of %s" % (hostname, software, reboot_time))
            ok, msg = sw.install(
                package=software,
                validate=False,
                checksum_algorithm='sha256',
                remote_path='/tmp',
                progress=progress_out)
            print(hostname + ":  Status: " + str(ok) + ", Message: " + msg)
            if ok:
                if "never" in reboot_time:
                    print("%s: Installation staged, reboot at will." % hostname)
                elif "now" in reboot_time:
                    print("%s: Installation staged, rebooting now." % hostname)
                    print(sw.reboot())
                elif ":" in reboot_time:
                    print("%s: Installation staged, rebooting at %s UTC" % (hostname, reboot_time))
                    print(sw.reboot(at='%s' % reboot_time))
            else:
                print("%s: Installation not ok, see logs." % hostname)
    except ConnectError as err:
        sys.exit("%s: %s" % (hostname, err))
    except:
        sys.exit("Something else happened in upgrade_device. %s" % device_map)


def progress_out(dev, report):
    print("%s: %s" % (dev.hostname, report))


def main():
    load_version_map()
    devices = generate_device_list()
    for device in devices:
        hostname, version, model = get_version_and_model(devices['%s' % device])
        model_map = {
            'hardware': JUNOS_VERSIONS['hardware']['%s' % model],
            'software': JUNOS_VERSIONS['software']['%s' % JUNOS_VERSIONS['hardware']['%s' % model]['platform']],
            'expected_sw': JUNOS_VERSIONS['hardware']['%s' % model]['version']
        }
        if version != model_map['hardware']['version']:
            print("%s: Version mismatch" % hostname)
            print(" Installed: %s" % version)
            print(" Expected: %s" % model_map['expected_sw'])
            print(" Installer: firmware/%s\n" % model_map['software']['%s' % model_map['expected_sw']])
            if utils.yes_no("Would you like to stage an upgrade?"):
                if utils.yes_no("Immediate upgrade and reboot?"):
                    upgrades_queued.append({
                        'hostname': hostname,
                        'sw': model_map['software']['%s' % model_map['expected_sw']],
                        'reboot_time': 'now'
                    })
                else:
                    if utils.yes_no("Upgrade and no reboot?"):
                        upgrades_queued.append({
                            'hostname': hostname,
                            'sw': model_map['software']['%s' % model_map['expected_sw']],
                            'reboot_time': 'never'
                        })
                        continue
                    else:
                        print("When would you like the device to reboot in the next 24 hours?")
                        hour = utils.question_answer("Hour (24 hour clock, UTC):")
                        minute = utils.question_answer("Minute:")
                        upgrades_queued.append({
                            'hostname': hostname,
                            'sw': model_map['software']['%s' % model_map['expected_sw']],
                            'reboot_time': '%s:%s' % (hour, minute)
                        })
        else:
            print("%s: Version matches expectation\n")
    for device in upgrades_queued:
        upgrade_device(device)


if __name__ == '__main__':
    main()
