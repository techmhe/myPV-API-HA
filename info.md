# myPV AC THOR Integration

This integration connects your myPV AC THOR device to Home Assistant using the official myPV API.

## What you need

- A myPV AC THOR device
- The device serial number
- An API key from [myPV API portal](https://api.my-pv.com)

## Features

### Real-time Monitoring
- Power consumption per channel
- Temperature readings
- Energy consumption tracking

### State of Charge
- Battery SOC monitoring
- Updated every 5 minutes

### Solar Forecast
- Daily and future solar production forecasts
- Updated hourly

## Configuration

After installing the integration through HACS:

1. Go to **Settings** → **Devices & Services**
2. Click **+ ADD INTEGRATION**
3. Search for **myPV AC THOR**
4. Enter your:
   - Device serial number
   - API key

## Sensors

The integration automatically creates sensors for all available data from your device. Common sensors include:

- `sensor.mypv_ac_thor_xxxxx_power_*` - Power readings
- `sensor.mypv_ac_thor_xxxxx_temperature_*` - Temperature readings
- `sensor.mypv_ac_thor_xxxxx_energy_*` - Energy consumption
- `sensor.mypv_ac_thor_xxxxx_soc` - Battery state of charge
- `sensor.mypv_ac_thor_xxxxx_solar_forecast_*` - Solar production forecasts

All sensors include proper units and device classes for use in the Energy Dashboard and other automations.

## Support

For issues or feature requests, please visit the [GitHub repository](https://github.com/techmhe/myPV-API-HA/issues).
