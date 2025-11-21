"""Calendar platform for TimeTree Calendar integration."""
from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_CALENDAR_NAME, CONF_CALENDAR_ID

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up TimeTree calendar platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    calendar_name = entry.data[CONF_CALENDAR_NAME]
    calendar_id = entry.data[CONF_CALENDAR_ID]

    async_add_entities([TimeTreeCalendarEntity(coordinator, calendar_name, calendar_id, entry.entry_id)], True)


class TimeTreeCalendarEntity(CoordinatorEntity, CalendarEntity):
    """Representation of a TimeTree Calendar."""

    def __init__(self, coordinator, calendar_name: str, calendar_id: int, entry_id: str) -> None:
        """Initialize the TimeTree calendar entity."""
        super().__init__(coordinator)
        self._calendar_name = calendar_name
        self._calendar_id = calendar_id
        self._attr_name = f"TimeTree {calendar_name}"
        self._attr_unique_id = f"timetree_{calendar_id}"
        self._entry_id = entry_id

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        if not self.coordinator.data:
            return None

        now = datetime.now()
        upcoming_events = [
            event for event in self.coordinator.data
            if self._get_event_end(event) >= now
        ]

        if not upcoming_events:
            return None

        # Sort by start time and get the first one
        upcoming_events.sort(key=lambda x: self._get_event_start(x))
        next_event = upcoming_events[0]

        return CalendarEvent(
            start=self._get_event_start(next_event),
            end=self._get_event_end(next_event),
            summary=next_event.get("summary", ""),
            description=next_event.get("description"),
            location=next_event.get("location"),
            uid=next_event.get("uid"),
        )

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        if not self.coordinator.data:
            return []

        events = []
        for event_data in self.coordinator.data:
            event_start = self._get_event_start(event_data)
            event_end = self._get_event_end(event_data)

            # Check if event overlaps with requested range
            if event_end >= start_date and event_start <= end_date:
                events.append(
                    CalendarEvent(
                        start=event_start,
                        end=event_end,
                        summary=event_data.get("summary", ""),
                        description=event_data.get("description"),
                        location=event_data.get("location"),
                        uid=event_data.get("uid"),
                    )
                )

        # Sort events by start time
        events.sort(key=lambda x: x.start)
        return events

    def _get_event_start(self, event: dict[str, Any]) -> datetime:
        """Get event start as datetime."""
        start = event.get("start")
        if isinstance(start, datetime):
            return start
        # Handle date objects (all-day events)
        return datetime.combine(start, datetime.min.time())

    def _get_event_end(self, event: dict[str, Any]) -> datetime:
        """Get event end as datetime."""
        end = event.get("end")
        if isinstance(end, datetime):
            return end
        # Handle date objects (all-day events)
        return datetime.combine(end, datetime.max.time())

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return {
            "calendar_id": self._calendar_id,
            "calendar_name": self._calendar_name,
            "event_count": len(self.coordinator.data) if self.coordinator.data else 0,
        }
