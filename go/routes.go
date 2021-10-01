package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
)

func collectLogs(c *gin.Context) {
	DeviceList, err := readDevices("../devices.yaml")
	if err != nil {
		c.JSON(500, err.Error())
		return
	}
	if len(DeviceList) > 0 {
		collectedLogs := pollJunipers(DeviceList)
		c.JSON(200, collectedLogs)
	} else {
		c.JSON(200, nil)
	}
}

func collectDevice(c *gin.Context) {
	DeviceList, err := readDevices("../devices.yaml")
	if err != nil {
		c.JSON(500, err.Error())
		return
	}
	var QueriedDeviceName string
	var QueriedDevice Device
	QueriedDeviceName = c.Query("device")

	if len(QueriedDeviceName) > 0 {
		for _, device := range DeviceList {
			if device.Hostname == QueriedDeviceName {
				QueriedDevice = device
			}
		}
		collectedLogs := queryDevice(QueriedDevice)
		c.JSON(200, collectedLogs)
	} else {
		c.JSON(200, nil)
	}
}

func displayDeviceLogs(c *gin.Context) {
	var devlogs []DeviceExtendedLog
	QueriedDeviceName := c.Query("device")
	url := "http://localhost:3000/logDetails?device=" + QueriedDeviceName
	resp, err := http.Get(url)
	if err != nil {
		c.JSON(200, nil)
	}

	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		c.JSON(200, nil)
	}
	err = json.Unmarshal(body, &devlogs)
	if err != nil {
		fmt.Println(err)
	}
	devlog := devlogs[0]
	splitRune := '\xAA'
	upgradeLog := strings.Split(devlog.UpgradeLog[0], string(splitRune))
	devlog.UpgradeLog = upgradeLog
	c.HTML(http.StatusOK, "device.tmpl", gin.H{
		"hostname":   devlog.Hostname,
		"hardware":   devlog.Hardware,
		"version":    devlog.Version,
		"upgradeLog": devlog.UpgradeLog,
		"errorLog":   devlog.ErrorLog,
		"uptime":     devlog.Uptime,
	})
}

func displayLogs(c *gin.Context) {
	var devlogs []DeviceLog
	resp, err := http.Get("http://localhost:3000/collectLogs")
	if err != nil {
		c.JSON(200, nil)
	}

	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		c.JSON(200, nil)
	}
	err = json.Unmarshal(body, &devlogs)
	if err != nil {
		fmt.Println(err)
	}
	c.HTML(http.StatusOK, "indextest.tmpl", gin.H{
		"logs": devlogs,
	})
}
