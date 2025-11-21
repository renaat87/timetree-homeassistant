"""The TimeTree Calendar integration."""
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN, CONF_CALENDAR_ID, CONF_UPDATE_INTERVAL
from .timetree_api import (
    TimeTreeAPIClient,
    TimeTreeAuthError,
    TimeTreeConnectionError,
    convert_timetree_event,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.CALENDAR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up TimeTree Calendar from a config entry."""
    email = entry.data[CONF_EMAIL]
    password = entry.data[CONF_PASSWORD]
    calendar_id = entry.data[CONF_CALENDAR_ID]
    update_interval = entry.data.get(CONF_UPDATE_INTERVAL, 30)

    # Create API client
    client = TimeTreeAPIClient(email, password)

    # Authenticate
    try:
        await hass.async_add_executor_job(client.authenticate)
    except TimeTreeAuthError as err:
        raise ConfigEntryAuthFailed("Invalid credentials") from err
    except TimeTreeConnectionError as err:
        _LOGGER.error("Cannot connect to TimeTree: %s", err)
        return False

    # Create data update coordinator
    async def async_update_data():
        """Fetch data from TimeTree API."""
        try:
            events_data = await hass.async_add_executor_job(
                client.get_events, calendar_id
            )
            
            # Convert TimeTree events to Home Assistant format
            events = [convert_timetree_event(event) for event in events_data]
            
            _LOGGER.debug("Updated %d events from TimeTree", len(events))
            return events

        except TimeTreeAuthError as err:
            raise ConfigEntryAuthFailed("Authentication failed") from err
        except TimeTreeConnectionError as err:
            raise UpdateFailed(f"Error communicating with TimeTree: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"TimeTree Calendar {calendar_id}",
        update_method=async_update_data,
        update_interval=timedelta(minutes=update_interval),
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "client": client,
    }

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
