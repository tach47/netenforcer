#!/usr/bin/env python3

import jcs
import sys

CONFIGS = {}
SINGLE_OID = ".1.3.6.1.4.1.2636.13.61.1.9.1.1.1"
MULTI_OID = ".1.3.6.1.4.1.2636.13.61.1.9.1.1.2"
WALKABLE_OID = ".1.3.6.1.4.1.2636.13.61.1.9.1.1.3"
OUTCOMES = ["[SUCCESS]", "[FAIL]", "[INFO]"]

def check_log():
    log_output = {}
    with open('/var/log/upgrade_log', 'r') as f:
        upgrade_log = f.read()
    log_output['last'] =  upgrade_log.split("\n")[-2]
    log_output['all'] = upgrade_log
    return log_output


def increment_oid(snmp_oid):
    oid = '.'
    snmp_oid_split = snmp_oid.split('.')
    last_number = snmp_oid_split.pop()
    snmp_oid_split.append(str(int(last_number) + 1))
    oid = oid.join(snmp_oid_split)
    return oid


def main():
    snmp_action = jcs.get_snmp_action()
    snmp_oid = jcs.get_snmp_oid()
    new_oid = snmp_oid
    logs = check_log()
    if len(new_oid.split('.')) == 15:
        new_oid = "%s.0" % str(new_oid)
    if snmp_action == 'get':
        if snmp_oid == SINGLE_OID:
            log_output = logs["last"]
            jcs.emit_snmp_attributes(snmp_oid, "String", log_output)
        elif snmp_oid == MULTI_OID:
            log_output = logs["all"]
            log_output_split = log_output.split("\n")
            log_output_split[:] = [x for x in log_output_split if x]
            log_lines = "\xAA"
            log_lines = log_lines.join(log_output_split)
            jcs.emit_snmp_attributes(snmp_oid, "String", log_lines)
        else:
            log_output = logs["last"]
            jcs.emit_snmp_attributes(snmp_oid, "String", log_output)
    elif snmp_action == "get-next":
        if WALKABLE_OID in new_oid:
            log_output = logs["all"]
            count = int(new_oid.split(".")[-1])
            log_lines = log_output.split("\n")
            log_lines[:] = [x for x in log_lines if x]
            #log_output = "|><|"
            # log_output = log_output.join(log_lines)
            #new_oid = increment_oid(new_oid)
            #jcs.emit_snmp_attributes(new_oid, "String", log_output)
            for line in log_lines:
                new_oid = increment_oid(new_oid)
                jcs.emit_snmp_attributes(new_oid, "String", log_lines[count])
                if line in OUTCOMES:
                    break
    else:
        log_output = "%s: %s" % (snmp_action, logs["last"])
        jcs.emit_snmp_attributes(snmp_oid, "String", log_output)

if __name__ == '__main__':
    main()