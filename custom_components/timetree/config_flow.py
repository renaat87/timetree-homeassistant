"""Config flow for TimeTree Calendar integration."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    CONF_CALENDAR_ID,
    CONF_CALENDAR_NAME,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    UPDATE_INTERVAL_OPTIONS,
    ERROR_AUTH_FAILED,
    ERROR_CANNOT_CONNECT,
    ERROR_UNKNOWN,
)
from .timetree_api import (
    TimeTreeAPIClient,
    TimeTreeAuthError,
    TimeTreeConnectionError,
)

_LOGGER = logging.getLogger(__name__)


async def validate_auth(hass: HomeAssistant, email: str, password: str) -> dict[str, Any]:
    """Validate the user credentials and return calendar list."""
    client = TimeTreeAPIClient(email, password)
    
    try:
        await hass.async_add_executor_job(client.authenticate)
        calendars = await hass.async_add_executor_job(client.get_calendars)
        
        if not calendars:
            raise NoCalendarsError("No active calendars found")
        
        return {"calendars": calendars}
    
    except TimeTreeAuthError as err:
        raise InvalidAuth from err
    except TimeTreeConnectionError as err:
        raise CannotConnect from err


class TimeTreeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TimeTree Calendar."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.email = None
        self.password = None
        self.calendars = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - get credentials."""
        errors = {}

        if user_input is not None:
            try:
                info = await validate_auth(
                    self.hass, user_input[CONF_EMAIL], user_input[CONF_PASSWORD]
                )
                
                # Store credentials and calendars for next step
                self.email = user_input[CONF_EMAIL]
                self.password = user_input[CONF_PASSWORD]
                self.calendars = info["calendars"]
                
                # Move to calendar selection step
                return await self.async_step_calendar()

            except CannotConnect:
                errors["base"] = ERROR_CANNOT_CONNECT
            except InvalidAuth:
                errors["base"] = ERROR_AUTH_FAILED
            except NoCalendarsError:
                errors["base"] = "no_calendars"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = ERROR_UNKNOWN

        # Show credentials form
        data_schema = vol.Schema(
            {
                vol.Required(CONF_EMAIL): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_calendar(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle calendar selection step."""
        errors = {}

        if user_input is not None:
            # Find selected calendar
            calendar_id = user_input[CONF_CALENDAR_ID]
            selected_calendar = next(
                (cal for cal in self.calendars if str(cal["id"]) == calendar_id),
                None,
            )

            if selected_calendar:
                calendar_name = selected_calendar.get("name", "Unnamed Calendar")
                
                # Check if this calendar is already configured
                await self.async_set_unique_id(f"{self.email}_{calendar_id}")
                self._abort_if_unique_id_configured()

                # Create the config entry
                return self.async_create_entry(
                    title=f"TimeTree: {calendar_name}",
                    data={
                        CONF_EMAIL: self.email,
                        CONF_PASSWORD: self.password,
                        CONF_CALENDAR_ID: int(calendar_id),
                        CONF_CALENDAR_NAME: calendar_name,
                        CONF_UPDATE_INTERVAL: user_input.get(
                            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                        ),
                    },
                )
            else:
                errors["base"] = "calendar_not_found"

        # Build calendar selection options
        calendar_options = {
            str(cal["id"]): cal.get("name", "Unnamed Calendar")
            for cal in self.calendars
        }

        # Build update interval options
        interval_options = {
            str(minutes): label for minutes, label in UPDATE_INTERVAL_OPTIONS.items()
        }

        data_schema = vol.Schema(
            {
                vol.Required(CONF_CALENDAR_ID): vol.In(calendar_options),
                vol.Required(
                    CONF_UPDATE_INTERVAL, default=str(DEFAULT_UPDATE_INTERVAL)
                ): vol.In(interval_options),
            }
        )

        return self.async_show_form(
            step_id="calendar",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "calendar_count": str(len(self.calendars)),
            },
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class NoCalendarsError(HomeAssistantError):
    """Error to indicate no calendars were found."""
