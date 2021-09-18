#!/usr/bin/env python3

import json
import os
import sys

import yaml
from jnpr.junos import Device
from jnpr.junos.exception import ConnectAuthError

sys.path.append(os.path.abspath('..'))

import py_onepassword.op as op
from utils import utils

JUNOS_VERSIONS = ''
upgrades_queued = []


def generate_device_list():
    with open('devices.yaml', 'r') as f:
        devices = yaml.safe_load(f.read())['devices']
    return devices


def get_version_and_model(device):
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
    print(upgrades_queued)


if __name__ == '__main__':
    main()
