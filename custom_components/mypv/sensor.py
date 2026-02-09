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
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
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
SENSOR_TYPES = {
    # Power sensors
    "power_1": {
        "name": "Power Channel 1",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "power_2": {
        "name": "Power Channel 2",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "power_3": {
        "name": "Power Channel 3",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "power": {
        "name": "Total Power",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # Temperature sensors
    "temp_1": {
        "name": "Temperature Channel 1",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "temp_2": {
        "name": "Temperature Channel 2",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "temp_3": {
        "name": "Temperature Channel 3",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # Energy sensors
    "energy_1": {
        "name": "Energy Channel 1",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "energy_2": {
        "name": "Energy Channel 2",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "energy_3": {
        "name": "Energy Channel 3",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    "energy": {
        "name": "Total Energy",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    # SOC sensors
    "soc": {
        "name": "State of Charge",
        "unit": PERCENTAGE,
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    # Solar forecast sensors
    "solar_forecast_today": {
        "name": "Solar Forecast Today",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "solar_forecast_tomorrow": {
        "name": "Solar Forecast Tomorrow",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
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
            _create_sensors_from_data(
                forecast_coordinator, serial, entry.entry_id, "forecast"
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
    items = []
    for key, value in data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(_flatten_dict(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)


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

        # Device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            name=f"{NAME} {serial}",
            manufacturer="myPV",
            model="AC THOR",
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
        return flat_data.get(self._sensor_key)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        return {
            "serial": self._serial,
            "data_type": self._data_type,
        }
