# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-02-09

### Added
- Initial release of myPV AC THOR Home Assistant integration
- Support for myPV API v1
- Config flow for easy setup with device serial number and API key
- Dynamic sensor creation from API responses
- Three API endpoint implementations:
  - `/api/v1/device/{serial}/data` - Real-time device data (60 second update)
  - `/api/v1/device/{serial}/data/soc` - State of charge data (5 minute update)
  - `/api/v1/device/{serial}/solarForecast` - Solar forecast data (hourly update)
- Automatic entity creation for all non-empty API values
- Proper device classes, state classes, and units for all sensors
- Power sensors (W)
- Temperature sensors (°C)
- Energy sensors (kWh)
- Battery state of charge (%)
- Solar forecast sensors
- HACS compatibility
- Comprehensive documentation
- Example automations and dashboard configurations
- English translations
- Device info with manufacturer and model

### Features
- Multiple update coordinators for efficient data fetching
- Error handling and connection validation
- Flattened data structure for nested API responses
- Proper device grouping in Home Assistant UI
- Energy Dashboard integration support
