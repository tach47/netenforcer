package main

import (
	"encoding/json"
	"math"
	"net/http"
	"strconv"
	"time"
)

var myClient = &http.Client{Timeout: 10 * time.Second}

func getJson(url string, target interface{}) error {
	r, err := myClient.Get(url)
	if err != nil {
		return err
	}
	defer r.Body.Close()
	return json.NewDecoder(r.Body).Decode(target)
}

func centisecondsToString(input string) (result string) {
	input_int, _ := strconv.Atoi(input)
	input_int = input_int / 100
	years := math.Floor(float64(input_int) / 60 / 60 / 24 / 365)
	seconds := input_int % (60 * 60 * 24 * 365)
	months := math.Floor(float64(seconds) / 60 / 60 / 24 / 7 / 30)
	seconds = input_int % (60 * 60 * 24 * 7 * 365)
	weeks := math.Floor(float64(seconds) / 60 / 60 / 24 / 7)
	seconds = input_int % (60 * 60 * 24 * 7)
	days := math.Floor(float64(seconds) / 60 / 60 / 24)
	seconds = input_int % (60 * 60 * 24)
	hours := math.Floor(float64(seconds) / 60 / 60)
	seconds = input_int % (60 * 60)
	minutes := math.Floor(float64(seconds) / 60)
	seconds = input_int % 60

	if years > 0 {
		result = strconv.Itoa(int(years)) + " years, " + strconv.Itoa(int(months)) + " months, " + strconv.Itoa(int(weeks)) + " weeks, " + strconv.Itoa(int(days)) + " days, " + strconv.Itoa(int(hours)) + " hours, " + strconv.Itoa(int(minutes)) + " minutes, " + strconv.Itoa(int(seconds)) + " seconds"
	} else if months > 0 {
		result = strconv.Itoa(int(months)) + " months, " + strconv.Itoa(int(weeks)) + " weeks, " + strconv.Itoa(int(days)) + " days, " + strconv.Itoa(int(hours)) + " hours, " + strconv.Itoa(int(minutes)) + " minutes, " + strconv.Itoa(int(seconds)) + " seconds"
	} else if weeks > 0 {
		result = strconv.Itoa(int(weeks)) + " weeks, " + strconv.Itoa(int(days)) + " days, " + strconv.Itoa(int(hours)) + " hours, " + strconv.Itoa(int(minutes)) + " minutes, " + strconv.Itoa(int(seconds)) + " seconds"
	} else if days > 0 {
		result = strconv.Itoa(int(days)) + " days, " + strconv.Itoa(int(hours)) + " hours, " + strconv.Itoa(int(minutes)) + " minutes, " + strconv.Itoa(int(seconds)) + " seconds"
	} else if hours > 0 {
		result = strconv.Itoa(int(hours)) + " hours, " + strconv.Itoa(int(minutes)) + " minutes, " + strconv.Itoa(int(seconds)) + " seconds"
	} else if minutes > 0 {
		result = strconv.Itoa(int(minutes)) + " minutes, " + strconv.Itoa(int(seconds)) + " seconds"
	} else {
		result = strconv.Itoa(int(seconds)) + " seconds"
	}
	return result
}
