# myPV AC THOR - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Custom integration for Home Assistant to monitor myPV AC-THOR devices using the official myPV API.

## Features

- Monitor device data (power, temperature, energy)
- Track state of charge (SOC) for connected storage
- View solar forecast data
- Automatic entity creation for all available data points
- Configurable update intervals for different data types

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

- `/api/v1/device/{serial}/data` - Device data (updated every 60 seconds)
- `/api/v1/device/{serial}/data/soc` - State of charge (updated every 5 minutes)
- `/api/v1/device/{serial}/solarForecast` - Solar forecast (updated every hour)

## Sensors

The integration automatically creates sensor entities for all non-empty values returned by the API, including:

- Power sensors (W)
- Temperature sensors (°C)
- Energy sensors (kWh)
- State of charge (%)
- Solar forecast (kWh)

Each sensor is properly configured with appropriate device classes, state classes, and units of measurement.

## Support

For issues, feature requests, or contributions, please visit the [GitHub repository](https://github.com/techmhe/myPV-API-HA/issues).

## Examples

See [EXAMPLES.md](EXAMPLES.md) for automation examples and dashboard configurations.
