package main

type Devices struct {
	Device []Device
}

type Device struct {
	Hostname         string
	IPAddress        string `yaml:"ip_address"`
	OnePasswordTitle string `yaml:"1password_title"`
	Version          []string
	UpgradeLog       []string
}

type DeviceLog struct {
	Hostname   string
	Hardware   string
	Version    string
	UpgradeLog string
	Error      string
}

type DeviceLogs struct {
	Device []DeviceLog
}

type DeviceExtendedLog struct {
	Hostname          string
	IPAddress         string
	Hardware          string
	Version           string
	Uptime            string
	PendingReboot     bool
	PendingRebootTime string
	UpgradeLog        []string
	ErrorLog          []string
}
