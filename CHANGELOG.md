# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Changed
- **BREAKING**: Comprehensive sensor naming improvements based on official myPV API schema
- Updated all sensor names to be more descriptive and user-friendly
- Added proper unit conversions:
  - Temperature sensors now correctly convert from 0.1°C to °C
  - Current sensors now correctly convert from 0.1A to A
  - Frequency sensors now correctly convert from mHz (milliHertz) to Hz
- Added 146 sensor definitions with proper device classes and state classes
- Device status sensor now shows human-readable values (e.g., "Standby", "Heating", "Error")
- Ethernet mode sensor now shows human-readable values (e.g., "LAN", "WLAN", "AP")
- Device model now dynamically set based on API response (AC THOR, AC ELWA-E, or AC ELWA 2)
- **Device data polling interval reduced from 60s to 30s** for more responsive updates (API updates every 10s)

### Added
- Support for voltage sensors (V)
- Support for current sensors (A)
- Support for frequency sensor (Hz)
- Support for time-based sensors (minutes, hours, days)
- **Proper solar forecast implementation**:
  - Solar Forecast Today sensor with daily total in Wh
  - Solar Forecast Tomorrow sensor with daily total in Wh
  - Solar Forecast Day After Tomorrow sensor with daily total in Wh
  - Hourly forecast data included as sensor attributes
  - Automatic date detection from API response
- **Time-based solar forecast sensors for today**:
  - Solar Forecast Night (00:00 - 06:00)
  - Solar Forecast Morning (06:01 - 09:00)
  - Solar Forecast Late Morning (09:01 - 12:00)
  - Solar Forecast Mid Day (12:01 - 15:00)
  - Solar Forecast Afternoon (15:01 - 18:00)
  - Solar Forecast Evening (18:01 - 23:59)
  - Each time-based sensor sums hourly values within its period
  - Hourly breakdown available in sensor attributes
- Support for all myPV API sensor types including:
  - Power sensors for photovoltaic, battery storage, heat pump, and charging station
  - Communication status for connected devices
  - Firmware version information
  - Network configuration sensors
  - Secondary controller status sensors
  - And many more...

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
