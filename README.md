# myPV AC THOR - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Custom integration for Home Assistant to monitor myPV AC-THOR, AC ELWA-E, and AC ELWA 2 devices using the official myPV API.

## Features

- Monitor device data (power, temperature, voltage, current, frequency)
- Track state of charge (SOC) for connected battery storage and charging stations
- View solar forecast data
- Automatic entity creation for all available data points from the API
- Comprehensive sensor definitions with proper units and device classes
- Support for multiple device types (AC THOR, AC ELWA-E, AC ELWA 2)
- Support for photovoltaic, battery storage, heat pump, and charging station monitoring
- Configurable update intervals for different data types
- Human-readable status values for device states

## Installation

### HACS (Recommended)

1. Add this repository as a custom repository in HACS
2. Search for "myPV AC THOR" in HACS
3. Install the integration
4. Restart Home Assistant

### Manual

1. Copy the `custom_components/mypv` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services
2. Click "+ ADD INTEGRATION"
3. Search for "myPV AC THOR"
4. Enter your device serial number and API key
5. Submit the form

### Getting Your API Key

Visit the [myPV API documentation](https://api.my-pv.com/api-docs/) to obtain your API key.

## Supported Endpoints

This integration implements the following myPV API endpoints:

- `/api/v1/device/{serial}/data` - Device data (updated every 30 seconds)
- `/api/v1/device/{serial}/data/soc` - State of charge (updated every 5 minutes)
- `/api/v1/device/{serial}/solarForecast` - Solar forecast (updated every hour)
  - Returns PV energy forecast for today and up to 2 additional days (3 days total)
  - Includes hourly intervals in local timezone
  - Daily totals provided as separate values

## Sensors

The integration automatically creates sensors for all available data from your device based on the myPV API schema. All sensors have proper names, units, and device classes for seamless Home Assistant integration.

### Sensor Categories

**Power Sensors (W)**
- Total system power and individual phase power (L1, L2, L3)
- Photovoltaic production per phase
- Battery storage power per phase
- Heat pump power per phase
- Charging station power per phase
- Grid and solar power contributions

**Temperature Sensors (°C)**
- Power unit temperature
- Up to 4 temperature channels
- Automatic conversion from 0.1°C units

**Current Sensors (A)**
- Grid current per phase (L1, L2, L3)
- Automatic conversion from 0.1A units

**Voltage Sensors (V)**
- Input voltage per phase
- Output voltage
- AUX relay voltage

**Battery & Charging**
- Battery storage State of Charge (%)
- Charging station State of Charge (%)

**Status & Configuration**
- Device status (Standby, Heating, Error, etc.)
- Cloud connection status
- Firmware versions
- Network configuration
- Communication status for connected devices

**Other Sensors**
- Grid frequency (Hz)
- Uptime (hours)
- Boost timers
- And many more...

**Solar Forecast**
- Solar Forecast Today (Wh) - Total expected production for today
- Solar Forecast Tomorrow (Wh) - Total expected production for tomorrow
- Solar Forecast Day After Tomorrow (Wh) - Total expected production for day after tomorrow
- Each forecast sensor includes hourly breakdown in attributes

**Time-Based Solar Forecast (Today Only)**
- Solar Forecast Night (Wh) - Expected production from 00:00 to 06:00
- Solar Forecast Morning (Wh) - Expected production from 06:01 to 09:00
- Solar Forecast Late Morning (Wh) - Expected production from 09:01 to 12:00
- Solar Forecast Mid Day (Wh) - Expected production from 12:01 to 15:00
- Solar Forecast Afternoon (Wh) - Expected production from 15:01 to 18:00
- Solar Forecast Evening (Wh) - Expected production from 18:01 to 23:59
- Each time-based sensor includes hourly breakdown in attributes

Each sensor is properly configured with appropriate device classes, state classes, and units of measurement.

## Support

For issues, feature requests, or contributions, please visit the [GitHub repository](https://github.com/techmhe/myPV-API-HA/issues).

## Examples

See [EXAMPLES.md](EXAMPLES.md) for automation examples and dashboard configurations.
