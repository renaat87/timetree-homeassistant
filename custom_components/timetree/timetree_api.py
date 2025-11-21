"""TimeTree API client wrapper for Home Assistant integration."""
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import requests
from requests.exceptions import HTTPError, RequestException

from .const import API_BASEURI, API_USER_AGENT

_LOGGER = logging.getLogger(__name__)


class TimeTreeAuthError(Exception):
    """Exception raised when authentication fails."""


class TimeTreeConnectionError(Exception):
    """Exception raised when connection to TimeTree fails."""


class TimeTreeAPIClient:
    """TimeTree API client."""

    def __init__(self, email: str, password: str) -> None:
        """Initialize the TimeTree API client."""
        self.email = email
        self.password = password
        self.session_id = None
        self.session = requests.Session()

    def authenticate(self) -> bool:
        """Authenticate with TimeTree and get session ID."""
        url = f"{API_BASEURI}/auth/email/signin"
        payload = {
            "uid": self.email,
            "password": self.password,
            "uuid": str(uuid.uuid4()).replace("-", ""),
        }
        headers = {
            "Content-Type": "application/json",
            "X-Timetreea": API_USER_AGENT,
        }

        try:
            response = requests.put(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code != 200:
                _LOGGER.error("Authentication failed: %s", response.text)
                raise TimeTreeAuthError("Invalid credentials")

            self.session_id = response.cookies.get("_session_id")
            if not self.session_id:
                raise TimeTreeAuthError("No session ID received")

            self.session.cookies.set("_session_id", self.session_id)
            _LOGGER.info("Successfully authenticated with TimeTree")
            return True

        except RequestException as err:
            _LOGGER.error("Connection error during authentication: %s", err)
            raise TimeTreeConnectionError("Cannot connect to TimeTree") from err

    def get_calendars(self) -> list[dict[str, Any]]:
        """Get list of available calendars."""
        if not self.session_id:
            raise TimeTreeAuthError("Not authenticated")

        url = f"{API_BASEURI}/calendars?since=0"
        headers = {
            "Content-Type": "application/json",
            "X-Timetreea": API_USER_AGENT,
        }

        try:
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                _LOGGER.error("Failed to get calendars: %s", response.text)
                raise HTTPError("Failed to fetch calendars")

            calendars = response.json().get("calendars", [])
            
            # Filter out deactivated calendars
            active_calendars = [
                cal for cal in calendars if cal.get("deactivated_at") is None
            ]
            
            _LOGGER.info("Found %d active calendars", len(active_calendars))
            return active_calendars

        except RequestException as err:
            _LOGGER.error("Connection error while fetching calendars: %s", err)
            raise TimeTreeConnectionError("Cannot connect to TimeTree") from err

    def get_events(self, calendar_id: int) -> list[dict[str, Any]]:
        """Get events from a specific calendar."""
        if not self.session_id:
            raise TimeTreeAuthError("Not authenticated")

        url = f"{API_BASEURI}/calendar/{calendar_id}/events/sync"
        headers = {
            "Content-Type": "application/json",
            "X-Timetreea": API_USER_AGENT,
        }

        try:
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                _LOGGER.error("Failed to get events: %s", response.text)
                raise HTTPError("Failed to fetch events")

            r_json = response.json()
            events = r_json.get("events", [])
            
            # Handle chunked responses
            if r_json.get("chunk") is True:
                events.extend(self._get_events_recursive(calendar_id, r_json.get("since")))
            
            _LOGGER.info("Fetched %d events from calendar %s", len(events), calendar_id)
            return events

        except RequestException as err:
            _LOGGER.error("Connection error while fetching events: %s", err)
            raise TimeTreeConnectionError("Cannot connect to TimeTree") from err

    def _get_events_recursive(self, calendar_id: int, since: int) -> list[dict[str, Any]]:
        """Recursively fetch events when response is chunked."""
        url = f"{API_BASEURI}/calendar/{calendar_id}/events/sync?since={since}"
        headers = {
            "Content-Type": "application/json",
            "X-Timetreea": API_USER_AGENT,
        }

        try:
            response = self.session.get(url, headers=headers, timeout=10)
            r_json = response.json()
            events = r_json.get("events", [])
            
            if r_json.get("chunk") is True:
                events.extend(self._get_events_recursive(calendar_id, r_json.get("since")))
            
            return events

        except RequestException as err:
            _LOGGER.error("Error fetching chunked events: %s", err)
            return []


def convert_timestamp_to_datetime(timestamp: int, tzinfo: ZoneInfo = ZoneInfo("UTC")) -> datetime:
    """Convert timestamp to datetime for both positive and negative timestamps."""
    if timestamp >= 0:
        return datetime.fromtimestamp(timestamp, tzinfo)
    return datetime.fromtimestamp(0, tzinfo) + timedelta(seconds=int(timestamp))


def convert_timetree_event(event_data: dict[str, Any]) -> dict[str, Any]:
    """Convert TimeTree event to Home Assistant calendar event format."""
    # Extract timezone info
    start_tz = ZoneInfo(event_data.get("start_timezone", "UTC"))
    end_tz = ZoneInfo(event_data.get("end_timezone", "UTC"))
    
    # Convert timestamps (TimeTree uses milliseconds)
    start_dt = convert_timestamp_to_datetime(
        event_data.get("start_at") / 1000, start_tz
    )
    end_dt = convert_timestamp_to_datetime(
        event_data.get("end_at") / 1000, end_tz
    )
    
    # Build Home Assistant calendar event
    ha_event = {
        "uid": event_data.get("uuid"),
        "summary": event_data.get("title", ""),
        "start": start_dt,
        "end": end_dt,
        "description": event_data.get("note", ""),
        "location": event_data.get("location", ""),
    }
    
    # Add all-day flag if applicable
    if event_data.get("all_day"):
        ha_event["start"] = start_dt.date()
        ha_event["end"] = end_dt.date()
    
    # Add URL if present
    if event_data.get("url"):
        ha_event["url"] = event_data.get("url")
    
    return ha_event
