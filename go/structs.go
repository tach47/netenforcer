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

type DeviceLogs struct {
	Hostname   string
	Hardware   string
	Version    string
	UpgradeLog string
	Error      string
}
