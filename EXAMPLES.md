# Example Automations for myPV AC THOR

Here are some useful automation examples for your myPV AC THOR integration.

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
            Total Energy: {{ states('sensor.mypv_ac_thor_xxxxx_total_energy') }} kWh
            Solar Forecast Tomorrow: {{ states('sensor.mypv_ac_thor_xxxxx_solar_forecast_tomorrow') }} kWh
          title: "Daily myPV Report"
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
title: myPV AC THOR
entities:
  - entity: sensor.mypv_ac_thor_xxxxx_total_power
    name: Current Power
  - entity: sensor.mypv_ac_thor_xxxxx_total_energy
    name: Total Energy
  - entity: sensor.mypv_ac_thor_xxxxx_soc
    name: Battery SOC
  - entity: sensor.mypv_ac_thor_xxxxx_temperature_channel_1
    name: Temperature Ch1
  - entity: sensor.mypv_ac_thor_xxxxx_solar_forecast_today
    name: Solar Forecast Today
```

## Energy Dashboard Integration

The sensors automatically work with Home Assistant's Energy Dashboard. To add them:

1. Go to **Settings** → **Dashboards** → **Energy**
2. Add your energy sensors under the appropriate sections:
   - Solar Production: Use solar forecast sensors
   - Grid Consumption: Use total energy sensors
   - Battery: Use SOC sensor

Replace `xxxxx` with your actual device serial number in all examples.
