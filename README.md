# Raspberry Pi Air Quality Monitor

[![Crafted by Human](https://madebyhuman.iamjarl.com/badges/crafted-black.svg)](https://madebyhuman.iamjarl.com)

A simple air quality monitoring service for the Raspberry Pi running Raspberry Pi OS, connected to an SDS011 particulate matter sensor. Optionally (if the user provides a free WeatherAPI key and a location, or an OpemWeather key and coordinates), outdoor particulate matter data can be fetched from the internet and tracked.

## Installation
Clone the repository and run the following to install docker from its upstream repository:
```bash
make install
```

## Building
To build:
```bash
make build
```

To rebuild an existing container on-the-fly after making changes to `Dockerfile`, `docker-compose.yaml` or files in `/src`:
```bash
make rebuild && make run
```

## Running
To run, use the run command:
```bash
make run
```

## Architecture
This project uses python, flask, docker compose and redis to create a simple web server to display the latest historical values from the sensor.

## Example Data
Some example data you can get from the sensor includes the following:

```json
{
    "device_id": 13358,
    "pm10": 10.8,
    "pm2.5": 4.8,
    "timestamp": "2021-06-16 22:12:13.887717"
}
```

The sensor reads two particulate matter (PM) values.

PM10 is a measure of particles less than 10 micrometers, whereas PM 2.5 is a measurement of finer particles, less than 2.5 micrometers. AQI (air quality index) is a composite value calculated based on these two direct measurements.

Different particles are from different sources, and can be hazardous to different parts of the respiratory system.

## Prior Arts
Thank you to @whirledsol, specifically for the implementation of a "measure now" button in [their fork](https://github.com/whirledsol/pi-air-quality-monitor)
