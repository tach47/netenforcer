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
		returnvalue = append(returnvalue, string(variable.Value.([]byte)))
		return returnvalue, nil
	}
	return nil, nil
}

func pollSNMP(wg *sync.WaitGroup, device Device, devInfo *[]DeviceLogs) {
	defer wg.Done()
	var deviceOutput DeviceLogs
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

func pollJunipers(DeviceList []Device) []DeviceLogs {
	var devices []DeviceLogs
	wg := &sync.WaitGroup{}
	wg.Add(len(DeviceList))
	for _, device := range DeviceList {
		go pollSNMP(wg, device, &devices)
	}
	wg.Wait()
	return devices
}
