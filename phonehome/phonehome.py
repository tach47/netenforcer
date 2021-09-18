#!/usr/bin/env python3

import psutil
import requests
import sys
import yaml
from jnpr.junos import Device
from jnpr.junos.utils.sw import SW

CONFIGS = {}
JUNOS_VERSIONS = {}


def _Debug(msg):
    if CONFIGS['debug'] == True:
        print(msg)


def check_free(min_free, dir):
    available_space = psutil.disk_usage(dir).free
    if available_space > min_free:
        return (True, available_space)
    else:
        return (False, available_space)


def fetch_and_install(url):
    try:
        min_free = requests.get(url, stream=True).headers['Content-Length']
    except KeyError:
        _Debug("Installer not at %s. Exiting" % url)
        sys.exit()
    enough_space, available_space = check_free(min_free, CONFIGS['installer']['temp_dir'])
    if enough_space:
        with Device() as dev:
            sw = SW(dev)
            ok, msg = sw.install(
                package=url,
                remote_path=CONFIGS['installer']['temp_dir'],
                validate=CONFIGS['installer']['validate'],
                checksum_algorithm='sha256',
                progress=progress_out
            )
            if ok:
                _Debug("Install completed, pending reboot. %s" % msg)
            else:
                _Debug("Install NOT successful. %s" % msg)
    else:
        _Debug("Insufficient disk space: %s required, %s available" % (min_free, available_space))


def get_version_and_model():
    with Device() as dev:
        facts = dev.facts
        _ = facts["version"]
    return (facts["fqdn"], facts["version"], facts["model"])


def load_version_map():
    global JUNOS_VERSIONS
    mappings = requests.get(CONFIGS["mappings_url"]).content
    JUNOS_VERSIONS = yaml.safe_load(mappings)


def bootstrap():
    global CONFIGS
    with open("phonehome_config.yaml", "r") as f:
        CONFIGS = yaml.safe_load(f.read())
    load_version_map()
    update_config_yaml()


def update_config_yaml():
    if CONFIGS["auto_update_config"]:
        config = requests.get(CONFIGS["config_url"])
        with open("phonehome_config.yaml", "wb") as f:
            f.write(config.content)


def progress_out(dev, report):
    _Debug("%s: %s" % (dev.hostname, report))


def main():
    bootstrap()
    fqdn, version, model = get_version_and_model()
    model_map = {
        'hardware': JUNOS_VERSIONS['hardware']['%s' % model],
        'software': JUNOS_VERSIONS['software']['%s' % JUNOS_VERSIONS['hardware']['%s' % model]['platform']],
        'expected_sw': JUNOS_VERSIONS['hardware']['%s' % model]['version']
    }
    if version != model_map['hardware']['version']:
        _Debug("%s: Version mismatch" % hostname)
        _Debug(" Installed: %s" % version)
        _Debug(" Expected: %s" % model_map['expected_sw'])
        _Debug(" Installer: firmware/%s\n" % model_map['software']['%s' % model_map['expected_sw']])
        firmware_url = "%s/%s" % (CONFIGS['firmware_url'], model_map['software']['%s' % model_map['expected_sw']])
        fetch_and_install(firmware_url)


if __name__ == "__main__":
    main()
