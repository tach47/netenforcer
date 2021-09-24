#!/usr/bin/env python3

import jcs

CONFIGS = {}


def check_log():
    with open('/var/log/upgrade_log', 'r') as f:
        upgrade_log = f.read()
    log_output = upgrade_log.split("\n")[-2]
    return log_output


def main():
    snmp_action = jcs.get_snmp_action()
    snmp_oid = jcs.get_snmp_oid()
    log_output = check_log()
    if snmp_action == 'get':
        jcs.emit_snmp_attributes(snmp_oid, "String", log_output)


if __name__ == '__main__':
    main()