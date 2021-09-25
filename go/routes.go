package main

import "github.com/gin-gonic/gin"

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
