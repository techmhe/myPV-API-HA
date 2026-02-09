"""Sensor platform for myPV AC THOR integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import MyPVApiClient
from .const import DOMAIN, NAME, SCAN_INTERVAL_DATA, SCAN_INTERVAL_FORECAST, SCAN_INTERVAL_SOC

_LOGGER = logging.getLogger(__name__)


# Sensor definitions based on myPV API documentation
# These will be mapped from API responses to sensor entities
# Units are based on the API schema: W (Watt), 0.1A (Ampere), 0.1°C (Celsius), mHz (milliHertz), etc.
SENSOR_TYPES = {
    # Status and state sensors
    "9s_state": {
        "name": "Power Unit 9s Status",
    },
    "act_night_flag": {
        "name": "Day/Night (RH)",
    },
    "acthor9s": {
        "name": "Acthor Device Type",
    },
    "blockactive": {
        "name": "Block Status",
    },
    "boostactive": {
        "name": "Hot Water Boost Status",
    },
    "bststrt": {
        "name": "Hot Water Boost Active",
    },
    "cloudstate": {
        "name": "Cloud Status",
    },
    "co_upd_state": {
        "name": "Co-controller Update Status",
    },
    "coversion": {
        "name": "Co-controller Version",
    },
    "coversionlatest": {
        "name": "Latest Co-controller Firmware",
    },
    "ctrl_errors": {
        "name": "Control Error Bits",
    },
    "ctrlstate": {
        "name": "Control State",
    },
    "device": {
        "name": "Device Type",
    },
    "ecarboostctr": {
        "name": "E-Car Boost Time",
        "unit": UnitOfTime.MINUTES,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "ecarstate": {
        "name": "E-Car Status",
    },
    "error_state": {
        "name": "Error Bits",
    },
    "fan_speed": {
        "name": "Fan Level",
    },
    "fsetup": {
        "name": "First Setup Status",
    },
    "fwversion": {
        "name": "Firmware Version",
    },
    "fwversionlatest": {
        "name": "Latest Firmware",
    },
    "legboostnext": {
        "name": "Next Legionella Boost",
        "unit": UnitOfTime.DAYS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "load_state": {
        "name": "Load State",
    },
    "m1devstate": {
        "name": "Photovoltaic Communication Status",
    },
    "m2devstate": {
        "name": "Battery Storage Communication Status",
    },
    "m2state": {
        "name": "Battery Status",
    },
    "m3devstate": {
        "name": "Charging Station Communication Status",
    },
    "m4devstate": {
        "name": "Heat Pump Communication Status",
    },
    "mss2": {
        "name": "Secondary Controller 2 Status",
    },
    "mss3": {
        "name": "Secondary Controller 3 Status",
    },
    "mss4": {
        "name": "Secondary Controller 4 Status",
    },
    "mss5": {
        "name": "Secondary Controller 5 Status",
    },
    "mss6": {
        "name": "Secondary Controller 6 Status",
    },
    "mss7": {
        "name": "Secondary Controller 7 Status",
    },
    "mss8": {
        "name": "Secondary Controller 8 Status",
    },
    "mss9": {
        "name": "Secondary Controller 9 Status",
    },
    "mss10": {
        "name": "Secondary Controller 10 Status",
    },
    "mss11": {
        "name": "Secondary Controller 11 Status",
    },
    "p_co_s": {
        "name": "Partition Co-controller Status",
    },
    "p_co_v": {
        "name": "Partition Co-controller Version",
    },
    "p_ps_s": {
        "name": "Partition Power Unit Status",
    },
    "p_ps_v": {
        "name": "Partition Power Unit Version",
    },
    "p1_s": {
        "name": "Partition 1 Status",
    },
    "p1_v": {
        "name": "Partition 1 Version",
    },
    "p2_s": {
        "name": "Partition 2 Status",
    },
    "p2_v": {
        "name": "Partition 2 Version",
    },
    "p9s_upd_state": {
        "name": "Power Unit 9s Update Status",
    },
    "p9sversion": {
        "name": "Power Unit 9s Version",
    },
    "p9sversionlatest": {
        "name": "Latest Power Unit 9s Firmware",
    },
    "ps_state": {
        "name": "Power Unit Status",
    },
    "ps_upd_state": {
        "name": "Power Unit Update Status",
    },
    "psversion": {
        "name": "Power Unit Version",
    },
    "psversionlatest": {
        "name": "Latest Power Unit Firmware",
    },
    "pump_pwm": {
        "name": "Pump PWM",
    },
    "rel_selv": {
        "name": "SELV Relay Status",
    },
    "rel1_out": {
        "name": "Relay Status",
    },
    "schicht_flag": {
        "name": "Layer Charging Status",
    },
    "screen_mode_flag": {
        "name": "Device Status",
    },
    "upd_files_left": {
        "name": "Update Files Remaining",
    },
    "upd_state": {
        "name": "Update Status",
    },
    "warnings": {
        "name": "Warning Bits",
    },
    "wifi_signal": {
        "name": "WLAN Signal Strength",
    },
    "wp_flag": {
        "name": "Heat Pump Status",
    },
    "wp_time1_ctr": {
        "name": "Heat Pump Time1 Counter",
    },
    "wp_time2_ctr": {
        "name": "Heat Pump Time2 Counter",
    },
    "wp_time3_ctr": {
        "name": "Heat Pump Time3 Counter",
    },
    # Network configuration
    "cur_dns": {
        "name": "DNS Server",
    },
    "cur_eth_mode": {
        "name": "Ethernet Mode",
    },
    "cur_gw": {
        "name": "Gateway",
    },
    "cur_ip": {
        "name": "IP Address",
    },
    "cur_sn": {
        "name": "Subnet Mask",
    },
    "debug_ip": {
        "name": "Debug IP",
    },
    "meter_ss": {
        "name": "WiFi Meter Signal Strength",
        "unit": PERCENTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "meter_ssid": {
        "name": "WiFi Meter SSID",
    },
    "meter1_id": {
        "name": "my-PV Meter 1 ID",
    },
    "meter1_ip": {
        "name": "my-PV Meter 1 IP",
    },
    "meter2_id": {
        "name": "my-PV Meter 2 ID",
    },
    "meter2_ip": {
        "name": "my-PV Meter 2 IP",
    },
    "meter3_id": {
        "name": "my-PV Meter 3 ID",
    },
    "meter3_ip": {
        "name": "my-PV Meter 3 IP",
    },
    "meter4_id": {
        "name": "my-PV Meter 4 ID",
    },
    "meter4_ip": {
        "name": "my-PV Meter 4 IP",
    },
    "meter5_id": {
        "name": "my-PV Meter 5 ID",
    },
    "meter5_ip": {
        "name": "my-PV Meter 5 IP",
    },
    "meter6_id": {
        "name": "my-PV Meter 6 ID",
    },
    "meter6_ip": {
        "name": "my-PV Meter 6 IP",
    },
    # Date and time sensors
    "date": {
        "name": "Date",
    },
    "loctime": {
        "name": "Local Time",
    },
    "unixtime": {
        "name": "Unix Time",
        "device_class": SensorDeviceClass.TIMESTAMP,
    },
    "uptime": {
        "name": "Uptime",
        "unit": UnitOfTime.HOURS,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    # Current sensors (0.1A scale)
    "curr_L2": {
        "name": "Grid Current L2",
        "unit": UnitOfElectricCurrent.AMPERE,
        "device_class": SensorDeviceClass.CURRENT,
        "state_class": SensorStateClass.MEASUREMENT,
        "scale": 0.1,
    },
    "curr_L3": {
        "name": "Grid Current L3",
        "unit": UnitOfElectricCurrent.AMPERE,
        "device_class": SensorDeviceClass.CURRENT,
        "state_class": SensorStateClass.MEASUREMENT,
        "scale": 0.1,
    },
    "curr_mains": {
        "name": "Grid Current L1",
        "unit": UnitOfElectricCurrent.AMPERE,
        "device_class": SensorDeviceClass.CURRENT,
        "state_class": SensorStateClass.MEASUREMENT,
        "scale": 0.1,
    },
    # Frequency sensor (mH = millihertz)
    "freq": {
        "name": "Grid Frequency",
        "unit": UnitOfFrequency.HERTZ,
        "device_class": SensorDeviceClass.FREQUENCY,
        "state_class": SensorStateClass.MEASUREMENT,
        "scale": 0.001,
    },
    # Power sensors (W)
    "load_nom": {
        "name": "Nominal Power",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "m0bat": {
        "name": "Battery Storage Power",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "m0l1": {
        "name": "House Connection L1",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "m0l2": {
        "name": "House Connection L2",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "m0l3": {
        "name": "House Connection L3",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "m0sum": {
        "name": "House Connection Total",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "m1l1": {
        "name": "Photovoltaic L1",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "m1l2": {
        "name": "Photovoltaic L2",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "m1l3": {
        "name": "Photovoltaic L3",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "m1sum": {
        "name": "Photovoltaic Total",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "m2l1": {
        "name": "Battery Storage L1",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "m2l2": {
        "name": "Battery Storage L2",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "m2l3": {
        "name": "Battery Storage L3",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "m2sum": {
        "name": "Battery Storage Total",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "m3l1": {
        "name": "Charging Station L1",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "m3l2": {
        "name": "Charging Station L2",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "m3l3": {
        "name": "Charging Station L3",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "m3sum": {
        "name": "Charging Station Total",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "m4l1": {
        "name": "Heat Pump L1",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "m4l2": {
        "name": "Heat Pump L2",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "m4l3": {
        "name": "Heat Pump L3",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "m4sum": {
        "name": "Heat Pump Total",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "power_ac9": {
        "name": "AC THOR 9s Power",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "power_act": {
        "name": "AC THOR Power",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "power_elwa2": {
        "name": "ELWA 2 Power",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "power_grid": {
        "name": "Grid Power",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "power_grid_ac9": {
        "name": "Grid Power from Acthor 9s",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "power_grid_act": {
        "name": "Grid Power from Acthor",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "power_max": {
        "name": "Maximum Controllable Power",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "power_nominal": {
        "name": "Nominal Power (Nameplate)",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "power_solar": {
        "name": "Solar Power",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "power_solar_ac9": {
        "name": "Solar Power from Acthor 9s",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "power_solar_act": {
        "name": "Solar Power from Acthor",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "power_system": {
        "name": "Total System Power",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "power1_grid": {
        "name": "Output 1 Grid Power",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "power1_solar": {
        "name": "Output 1 Solar Power",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "power2_grid": {
        "name": "Output 2 Grid Power",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "power2_solar": {
        "name": "Output 2 Solar Power",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "power3_grid": {
        "name": "Output 3 Grid Power",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "power3_solar": {
        "name": "Output 3 Solar Power",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "surplus": {
        "name": "Surplus (Meter + Battery Charging)",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # Battery SOC (%)
    "m2soc": {
        "name": "Battery Storage SoC",
        "unit": PERCENTAGE,
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "m3soc": {
        "name": "Charging Station SoC",
        "unit": PERCENTAGE,
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # Temperature sensors (0.1°C scale)
    "temp_ps": {
        "name": "Power Unit Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "scale": 0.1,
    },
    "temp1": {
        "name": "Temperature 1",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "scale": 0.1,
    },
    "temp2": {
        "name": "Temperature 2",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "scale": 0.1,
    },
    "temp3": {
        "name": "Temperature 3",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "scale": 0.1,
    },
    "temp4": {
        "name": "Temperature 4",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "scale": 0.1,
    },
    # Voltage sensors (V)
    "volt_aux": {
        "name": "Voltage L2 at AUX Relay",
        "unit": UnitOfElectricPotential.VOLT,
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "volt_L2": {
        "name": "Power Unit Input Voltage L2",
        "unit": UnitOfElectricPotential.VOLT,
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "volt_L3": {
        "name": "Power Unit Input Voltage L3",
        "unit": UnitOfElectricPotential.VOLT,
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "volt_mains": {
        "name": "Power Unit Input Voltage L1",
        "unit": UnitOfElectricPotential.VOLT,
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "volt_out": {
        "name": "Power Unit Output Voltage",
        "unit": UnitOfElectricPotential.VOLT,
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up myPV sensor platform."""
    client: MyPVApiClient = hass.data[DOMAIN][entry.entry_id]["client"]
    serial: str = hass.data[DOMAIN][entry.entry_id]["serial"]

    # Create coordinators for different data types with different update intervals
    data_coordinator = MyPVDataUpdateCoordinator(
        hass, client, "data", SCAN_INTERVAL_DATA
    )
    soc_coordinator = MyPVDataUpdateCoordinator(
        hass, client, "soc", SCAN_INTERVAL_SOC
    )
    forecast_coordinator = MyPVDataUpdateCoordinator(
        hass, client, "forecast", SCAN_INTERVAL_FORECAST
    )

    # Fetch initial data
    await data_coordinator.async_config_entry_first_refresh()
    await soc_coordinator.async_config_entry_first_refresh()
    await forecast_coordinator.async_config_entry_first_refresh()

    entities = []

    # Create sensors from device data
    if data_coordinator.data:
        entities.extend(
            _create_sensors_from_data(
                data_coordinator, serial, entry.entry_id, "data"
            )
        )

    # Create sensors from SOC data
    if soc_coordinator.data:
        entities.extend(
            _create_sensors_from_data(
                soc_coordinator, serial, entry.entry_id, "soc"
            )
        )

    # Create sensors from forecast data
    if forecast_coordinator.data:
        entities.extend(
            _create_forecast_sensors(
                forecast_coordinator, serial, entry.entry_id
            )
        )

    async_add_entities(entities)


def _create_sensors_from_data(
    coordinator: MyPVDataUpdateCoordinator,
    serial: str,
    entry_id: str,
    data_type: str,
) -> list[MyPVSensor]:
    """Create sensor entities from API data."""
    entities = []
    
    if not coordinator.data:
        return entities

    # Flatten nested data structure
    flat_data = _flatten_dict(coordinator.data)

    for key, value in flat_data.items():
        # Skip empty values
        if value is None or value == "":
            continue

        # Create sensor entity
        entities.append(
            MyPVSensor(
                coordinator=coordinator,
                serial=serial,
                entry_id=entry_id,
                sensor_key=key,
                data_type=data_type,
            )
        )

    return entities


def _flatten_dict(data: dict, parent_key: str = "", sep: str = "_") -> dict:
    """Flatten nested dictionary."""
    # Handle non-dict inputs gracefully
    if not isinstance(data, dict):
        data_preview = str(data)[:50] if data else "None"
        _LOGGER.warning(
            "Expected dict but got %s. Data preview: %s...",
            type(data).__name__,
            data_preview
        )
        return {}
    
    items = []
    for key, value in data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(_flatten_dict(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)


def _create_forecast_sensors(
    coordinator: MyPVDataUpdateCoordinator,
    serial: str,
    entry_id: str,
) -> list[SensorEntity]:
    """Create sensor entities from solar forecast data."""
    entities = []
    
    if not coordinator.data:
        return entities
    
    # The forecast data has a structure like:
    # {
    #   "watt_hours": {"2026-01-14 08:00:00": 97, ...},
    #   "watt_hours_day": {"2026-01-14": 4312, ...}
    # }
    
    watt_hours_day = coordinator.data.get("watt_hours_day", {})
    
    if not watt_hours_day:
        _LOGGER.warning("No watt_hours_day data found in solar forecast")
        return entities
    
    # Sort dates to identify today, tomorrow, and day after tomorrow
    sorted_dates = sorted(watt_hours_day.keys())
    
    # Create sensors for each day
    for i, date in enumerate(sorted_dates[:3]):  # Maximum 3 days
        if i == 0:
            sensor_name = "Solar Forecast Today"
        elif i == 1:
            sensor_name = "Solar Forecast Tomorrow"
        elif i == 2:
            sensor_name = "Solar Forecast Day After Tomorrow"
        else:
            continue
        
        entities.append(
            MyPVForecastSensor(
                coordinator=coordinator,
                serial=serial,
                entry_id=entry_id,
                date=date,
                name=sensor_name,
            )
        )
    
    return entities


class MyPVDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching myPV data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: MyPVApiClient,
        data_type: str,
        scan_interval: int,
    ) -> None:
        """Initialize."""
        self.client = client
        self.data_type = data_type

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{data_type}",
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            if self.data_type == "data":
                return await self.client.async_get_data()
            elif self.data_type == "soc":
                return await self.client.async_get_soc()
            elif self.data_type == "forecast":
                return await self.client.async_get_solar_forecast()
            else:
                raise UpdateFailed(f"Unknown data type: {self.data_type}")
        except Exception as exception:
            raise UpdateFailed(f"Error communicating with API: {exception}") from exception


class MyPVSensor(CoordinatorEntity, SensorEntity):
    """Representation of a myPV sensor."""

    def __init__(
        self,
        coordinator: MyPVDataUpdateCoordinator,
        serial: str,
        entry_id: str,
        sensor_key: str,
        data_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        
        self._serial = serial
        self._sensor_key = sensor_key
        self._data_type = data_type
        self._attr_unique_id = f"{entry_id}_{data_type}_{sensor_key}"
        
        # Set name based on sensor key
        self._attr_name = self._format_sensor_name(sensor_key)
        
        # Try to get sensor configuration from SENSOR_TYPES
        sensor_config = SENSOR_TYPES.get(sensor_key, {})
        
        if "name" in sensor_config:
            self._attr_name = sensor_config["name"]
        
        if "unit" in sensor_config:
            self._attr_native_unit_of_measurement = sensor_config["unit"]
        
        if "device_class" in sensor_config:
            self._attr_device_class = sensor_config["device_class"]
        
        if "state_class" in sensor_config:
            self._attr_state_class = sensor_config["state_class"]

        # Device info - try to get device type from coordinator data
        device_model = "myPV Device"  # default fallback
        if coordinator.data:
            flat_data = _flatten_dict(coordinator.data)
            device_type = flat_data.get("device")
            if device_type:
                device_model = device_type
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            name=f"{NAME} {serial}",
            manufacturer="myPV",
            model=device_model,
        )

    def _format_sensor_name(self, key: str) -> str:
        """Format sensor key into readable name."""
        # Replace underscores with spaces and capitalize each word
        return key.replace("_", " ").title()

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        
        # Get value from flattened data structure
        flat_data = _flatten_dict(self.coordinator.data)
        value = flat_data.get(self._sensor_key)
        
        if value is None:
            return None
        
        # Apply human-readable mappings for specific sensors
        if self._sensor_key == "screen_mode_flag" and isinstance(value, int):
            status_map = {
                0: "Standby",
                1: "Heating",
                2: "Heating Boost",
                3: "Heating Complete",
                4: "No Connection / Disabled",
                5: "Error",
                6: "Blocking Time Active",
            }
            return status_map.get(value, f"Unknown ({value})")
        
        if self._sensor_key == "cur_eth_mode" and isinstance(value, int):
            mode_map = {0: "LAN", 1: "WLAN", 2: "AP"}
            return mode_map.get(value, f"Unknown ({value})")
        
        # Apply scaling if defined in sensor config
        sensor_config = SENSOR_TYPES.get(self._sensor_key, {})
        scale = sensor_config.get("scale")
        
        if scale is not None and isinstance(value, (int, float)):
            try:
                return round(value * scale, 2)
            except (ValueError, TypeError):
                _LOGGER.warning(
                    "Could not scale value %s for sensor %s with scale %s",
                    value,
                    self._sensor_key,
                    scale,
                )
                return value
        
        return value

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        return {
            "serial": self._serial,
            "data_type": self._data_type,
        }


class MyPVForecastSensor(CoordinatorEntity, SensorEntity):
    """Representation of a myPV solar forecast sensor."""

    def __init__(
        self,
        coordinator: MyPVDataUpdateCoordinator,
        serial: str,
        entry_id: str,
        date: str,
        name: str,
    ) -> None:
        """Initialize the forecast sensor."""
        super().__init__(coordinator)
        
        self._serial = serial
        self._date = date
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_forecast_{date}"
        
        # Set sensor properties for energy forecast
        self._attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL
        
        # Device info
        device_model = "myPV Device"
        if coordinator.data:
            flat_data = _flatten_dict(coordinator.data)
            device_type = flat_data.get("device")
            if device_type:
                device_model = device_type
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            name=f"{NAME} {serial}",
            manufacturer="myPV",
            model=device_model,
        )

    @property
    def native_value(self) -> Any:
        """Return the forecasted energy for the day."""
        if self.coordinator.data is None:
            return None
        
        watt_hours_day = self.coordinator.data.get("watt_hours_day", {})
        return watt_hours_day.get(self._date)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes including hourly forecast."""
        attributes = {
            "serial": self._serial,
            "date": self._date,
        }
        
        # Add hourly forecast data if available
        if self.coordinator.data:
            watt_hours = self.coordinator.data.get("watt_hours", {})
            
            # Filter hourly data for this specific date
            hourly_data = {}
            for timestamp, value in watt_hours.items():
                # Check if timestamp starts with our date
                if timestamp.startswith(self._date):
                    # Extract just the hour part for cleaner attributes
                    time_part = timestamp.split(" ")[1] if " " in timestamp else timestamp
                    hourly_data[time_part] = value
            
            if hourly_data:
                attributes["hourly_forecast"] = hourly_data
        
        return attributes
