# Example Automations for myPV AC THOR

Here are some useful automation examples for your myPV AC THOR integration.

**Note**: Sensor entity IDs follow the pattern `sensor.<sensor_name>`. For example:
- `sensor.solar_forecast_today`
- `sensor.photovoltaic_total`
- `sensor.device_status`
- `sensor.battery_storage_soc`

## Monitor High Power Consumption

```yaml
automation:
  - alias: "Alert on High Power Consumption"
    trigger:
      - platform: numeric_state
        entity_id: sensor.mypv_ac_thor_xxxxx_total_power
        above: 3000
    action:
      - service: notify.mobile_app
        data:
          message: "myPV AC THOR power consumption is above 3kW"
          title: "High Power Alert"
```

## Monitor Low Battery SOC

```yaml
automation:
  - alias: "Alert on Low Battery"
    trigger:
      - platform: numeric_state
        entity_id: sensor.mypv_ac_thor_xxxxx_soc
        below: 20
    action:
      - service: notify.mobile_app
        data:
          message: "Battery SOC is low ({{ states('sensor.mypv_ac_thor_xxxxx_soc') }}%)"
          title: "Low Battery Alert"
```

## Daily Energy Report

```yaml
automation:
  - alias: "Daily myPV Energy Report"
    trigger:
      - platform: time
        at: "20:00:00"
    action:
      - service: notify.mobile_app
        data:
          message: >
            Today's myPV stats:
            Solar Forecast Tomorrow: {{ states('sensor.solar_forecast_tomorrow') }} Wh
          title: "Daily myPV Report"
```

## Solar Forecast Alert

```yaml
automation:
  - alias: "High Solar Production Expected"
    trigger:
      - platform: numeric_state
        entity_id: sensor.solar_forecast_tomorrow
        above: 5000
    action:
      - service: notify.mobile_app
        data:
          message: "High solar production expected tomorrow: {{ states('sensor.solar_forecast_tomorrow') }} Wh"
          title: "Solar Forecast Alert"
```

## Temperature Monitoring

```yaml
automation:
  - alias: "Alert on High Temperature"
    trigger:
      - platform: numeric_state
        entity_id: sensor.mypv_ac_thor_xxxxx_temperature_channel_1
        above: 80
    action:
      - service: notify.mobile_app
        data:
          message: "myPV temperature is high ({{ states('sensor.mypv_ac_thor_xxxxx_temperature_channel_1') }}°C)"
          title: "High Temperature Alert"
```

## Dashboard Card Example

```yaml
type: entities
title: myPV Device
entities:
  - entity: sensor.device_status
    name: Status
  - entity: sensor.photovoltaic_total
    name: PV Power
  - entity: sensor.battery_storage_soc
    name: Battery SOC
  - entity: sensor.temperature_1
    name: Temperature
  - entity: sensor.solar_forecast_today
    name: Solar Forecast Today
  - entity: sensor.solar_forecast_tomorrow
    name: Solar Forecast Tomorrow
```

## Solar Forecast Card with Hourly Data

**Note**: This example requires the [multiple-entity-row](https://github.com/benct/lovelace-multiple-entity-row) custom card from HACS.

```yaml
type: custom:multiple-entity-row
entity: sensor.solar_forecast_today
name: Solar Forecast Today
secondary_info:
  attribute: hourly_forecast
  format: yaml
```

Alternatively, use the standard template card to display hourly data:

```yaml
type: markdown
content: >
  ## Solar Forecast Today

  Total: {{ states('sensor.solar_forecast_today') }} Wh

  ### Hourly Breakdown
  {% for time, value in state_attr('sensor.solar_forecast_today', 'hourly_forecast').items() %}
  - {{ time }}: {{ value }} Wh
  {% endfor %}
```

## Energy Dashboard Integration

The sensors automatically work with Home Assistant's Energy Dashboard. To add them:

1. Go to **Settings** → **Dashboards** → **Energy**
2. Add your energy sensors under the appropriate sections:
   - Solar Production: Use solar forecast sensors
   - Grid Consumption: Use total energy sensors
   - Battery: Use SOC sensor

Replace `xxxxx` with your actual device serial number in all examples.
