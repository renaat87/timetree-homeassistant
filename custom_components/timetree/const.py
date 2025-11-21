"""Constants for the TimeTree Calendar integration."""

DOMAIN = "timetree"

# Configuration keys
CONF_CALENDAR_ID = "calendar_id"
CONF_CALENDAR_NAME = "calendar_name"
CONF_UPDATE_INTERVAL = "update_interval"

# Default values
DEFAULT_UPDATE_INTERVAL = 30  # minutes

# Update interval options (in minutes)
UPDATE_INTERVAL_OPTIONS = {
    5: "5 minutes",
    15: "15 minutes",
    30: "30 minutes",
    60: "1 hour",
}

# API constants
API_BASEURI = "https://timetreeapp.com/api/v1"
API_USER_AGENT = "web/2.1.0/en"

# Error messages
ERROR_AUTH_FAILED = "authentication_failed"
ERROR_CANNOT_CONNECT = "cannot_connect"
ERROR_UNKNOWN = "unknown_error"
