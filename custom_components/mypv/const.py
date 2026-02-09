"""Constants for the myPV AC THOR integration."""

DOMAIN = "mypv"
NAME = "myPV AC THOR"

# Configuration
CONF_SERIAL = "serial"
CONF_API_KEY = "api_key"

# API
API_BASE_URL = "https://api.my-pv.com/api/v1"
API_TIMEOUT = 30

# Update intervals
SCAN_INTERVAL_DATA = 30  # seconds (API updates every 10s)
SCAN_INTERVAL_SOC = 300  # seconds (5 minutes)
SCAN_INTERVAL_FORECAST = 3600  # seconds (1 hour)

# Platforms
PLATFORMS = ["sensor"]
