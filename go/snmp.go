package main

import (
	"strconv"
	"strings"
	"sync"
	"time"

	g "github.com/gosnmp/gosnmp"
)

func walkSNMP(device string, oid string) ([]string, error) {
	targetDevice := device
	targetPort := "161"
	port, _ := strconv.ParseUint(targetPort, 10, 16)

	params := &g.GoSNMP{
		Target:    targetDevice,
		Port:      uint16(port),
		Community: NetworkCfg.snmpCommunity,
		Version:   g.Version2c,
		Timeout:   time.Duration(2) * time.Second,
	}
	err := params.Connect()
	if err != nil {
		return nil, err
	}
	defer params.Conn.Close()
	var oids []string
	oids = append(oids, oid)
	result, err2 := params.Get(oids)
	if err2 != nil {
		return nil, err2
	}

	for _, variable := range result.Variables {
		var returnvalue []string
		switch variable.Type {
		case g.OctetString:
			output := variable.Value.([]byte)
			returnvalue = append(returnvalue, string(output))
		default:
			output := g.ToBigInt(variable.Value)
			returnvalue = append(returnvalue, output.String())
		}
		return returnvalue, nil
	}
	return nil, nil
}

func pollSNMP(wg *sync.WaitGroup, device Device, devInfo *[]DeviceLog) {
	defer wg.Done()
	var deviceOutput DeviceLog
	deviceOutput.Hostname = device.Hostname
	reply, err := walkSNMP(device.IPAddress, NetworkCfg.snmpOID)
	if err != nil {
		deviceOutput.Error = "[ERROR] - SNMP Timeout"
		*devInfo = append(*devInfo, deviceOutput)
	} else {
		deviceOutput.UpgradeLog = reply[0]
		reply, _ = walkSNMP(device.IPAddress, "1.3.6.1.2.1.1.1.0")
		s := strings.Split(reply[0], ",")
		deviceOutput.Version = strings.Split(s[2], " ")[3]
		deviceOutput.Hardware = strings.Split(s[1], " ")[2]
		*devInfo = append(*devInfo, deviceOutput)
	}
}

func collectExtendedLogs(device Device, deviceLog *[]DeviceExtendedLog) {
	var deviceOutput DeviceExtendedLog
	deviceOutput.Hostname = device.Hostname
	deviceOutput.IPAddress = device.IPAddress
	reply, err := walkSNMP(device.IPAddress, NetworkCfg.snmpLogsOID)
	if err != nil {
		deviceOutput.ErrorLog[0] = "[ERROR] - SNMP Timeout"
		*deviceLog = append(*deviceLog, deviceOutput)
	} else {
		deviceOutput.UpgradeLog = reply
		reply, _ = walkSNMP(deviceOutput.IPAddress, "1.3.6.1.2.1.1.1.0")
		s := strings.Split(reply[0], ",")
		deviceOutput.Version = strings.Split(s[2], " ")[3]
		deviceOutput.Hardware = strings.Split(s[1], " ")[2]
		reply, _ = walkSNMP(deviceOutput.IPAddress, "1.3.6.1.2.1.1.3.0")
		uptimeHR := centisecondsToString(reply[0])
		deviceOutput.Uptime = uptimeHR + " / " + reply[0]
		*deviceLog = append(*deviceLog, deviceOutput)
	}
}

func pollJunipers(DeviceList []Device) []DeviceLog {
	var devices []DeviceLog
	wg := &sync.WaitGroup{}
	wg.Add(len(DeviceList))
	for _, device := range DeviceList {
		go pollSNMP(wg, device, &devices)
	}
	wg.Wait()
	return devices
}

func queryDevice(QueriedDevice Device) []DeviceExtendedLog {
	var deviceLog []DeviceExtendedLog
	collectExtendedLogs(QueriedDevice, &deviceLog)
	return deviceLog
}
