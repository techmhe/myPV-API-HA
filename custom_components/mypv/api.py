"""API client for myPV AC THOR."""
import asyncio
import logging
from typing import Any

import aiohttp

from .const import API_BASE_URL, API_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class MyPVApiClient:
    """API client for myPV AC THOR."""

    def __init__(self, serial: str, api_key: str, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self._serial = serial
        self._api_key = api_key
        self._session = session
        self._base_url = API_BASE_URL

    async def _async_get(self, endpoint: str) -> dict[str, Any]:
        """Make GET request to the API."""
        url = f"{self._base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Accept": "application/json",
        }

        try:
            async with asyncio.timeout(API_TIMEOUT):
                async with self._session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    return await response.json()
        except asyncio.TimeoutError as exception:
            _LOGGER.error("Timeout error fetching information from %s", url)
            raise Exception("Timeout error") from exception
        except aiohttp.ClientError as exception:
            _LOGGER.error("Error fetching information from %s: %s", url, exception)
            raise Exception(f"Error communicating with API: {exception}") from exception
        except Exception as exception:
            _LOGGER.error("Unexpected error fetching from %s: %s", url, exception)
            raise

    async def async_get_data(self) -> dict[str, Any]:
        """Get device data."""
        endpoint = f"/device/{self._serial}/data"
        return await self._async_get(endpoint)

    async def async_get_soc(self) -> dict[str, Any]:
        """Get state of charge data."""
        endpoint = f"/device/{self._serial}/data/soc"
        return await self._async_get(endpoint)

    async def async_get_solar_forecast(self) -> dict[str, Any]:
        """Get solar forecast data."""
        endpoint = f"/device/{self._serial}/solarForecast"
        return await self._async_get(endpoint)

    async def async_validate_connection(self) -> bool:
        """Test if we can communicate with the API."""
        try:
            await self.async_get_data()
            return True
        except Exception as exception:
            _LOGGER.error("Failed to validate connection: %s", exception)
            return False
