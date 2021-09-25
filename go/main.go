package main

import (
	"fmt"
	"io/ioutil"
	"os"
	"runtime"

	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
	"github.com/spf13/viper"
	"github.com/urfave/cli"
	"gopkg.in/yaml.v2"
)

var (
	NetworkCfg netCfg
	DeviceList []Device
)

type netCfg struct {
	snmpCommunity string
	snmpOID       string
}

type httpCfg struct {
	port   string
	uiPath string
	addr   string
}

func configRuntime() {
	numCPU := runtime.NumCPU()
	runtime.GOMAXPROCS(numCPU)
	logrus.WithFields(logrus.Fields{
		"numCPU": numCPU,
	}).Info("Running with CPU count")
}

func readHttpConfig() *httpCfg {
	var (
		hc httpCfg
	)
	viper.SetConfigName("enforcerUI")
	viper.AddConfigPath(".")
	viper.SetConfigType("toml")
	err := viper.ReadInConfig()
	if err != nil {
		logrus.WithFields(logrus.Fields{
			"topic": "config",
			"event": "issues reading config",
		}).Error(err)
		os.Exit(1)
	}
	hc.port = viper.GetString("http.port")
	hc.uiPath = viper.GetString("http.uipath")
	hc.addr = viper.GetString("http.address")
	NetworkCfg.snmpCommunity = viper.GetString("snmp.snmpCommunity")
	NetworkCfg.snmpOID = viper.GetString("snmp.snmpOID")
	return &hc
}

func readDevices(filename string) ([]Device, error) {
	buf, err := ioutil.ReadFile(filename)
	if err != nil {
		return nil, err
	}

	var test []Device
	err = yaml.Unmarshal(buf, &test)
	if err != nil {
		return nil, fmt.Errorf("%q: %v", filename, err)
	}
	return test, nil
}

func appCLISetup() *cli.App {
	app := cli.NewApp()
	app.Name = "netenforcer - rapid snmp collector for netenforcer"
	app.Usage = "Provides a REST API function to collect SNMP information from devices orchestrated by netenforcer"
	app.Version = "0.1"
	return app
}

func main() {
	app := appCLISetup()
	hc := readHttpConfig()
	app.Action = func(c *cli.Context) {
		configRuntime()
		gin.SetMode(gin.ReleaseMode)
		router := gin.Default()
		router.GET("/collectLogs", collectLogs)

		err := router.Run(hc.addr + ":" + hc.port)
		if err != nil {
			logrus.WithFields(logrus.Fields{
				"topic": "http",
				"event": "failure starting http server",
			}).Error(err)
			os.Exit(1)
		}
	}
	app.Run(os.Args)
}
