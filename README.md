# TimeTree Calendar Integration for Home Assistant

A custom Home Assistant integration that syncs your TimeTree calendars with Home Assistant's calendar platform.

## Features

- 🔄 Automatic synchronization of TimeTree calendar events
- ⏱️ Configurable update intervals (5, 15, 30, or 60 minutes)
- 📅 Full calendar integration with Home Assistant
- 🔐 Secure credential storage
- 🌍 Support for all-day events and timezones
- 📍 Location and description support

## Quick Reference

**GitHub Repository**: `https://github.com/renaat87/timetree-homeassistant`  

**HACS Installation**: Add as custom repository → Download → Configure  
**Manual Installation**: Copy to `custom_components/timetree` → Restart → Configure

## Installation

### Method 1: HACS (Recommended)

[HACS](https://hacs.xyz/) (Home Assistant Community Store) makes it easy to install and update custom integrations.

#### Prerequisites
- HACS must be installed in your Home Assistant instance
- Your GitHub repository must be public

#### Steps

1. **Add Custom Repository to HACS**
   - Open Home Assistant
   - Go to **HACS** in the sidebar
   - Click on **Integrations**
   - Click the **three dots menu** (⋮) in the top right corner
   - Select **Custom repositories**
   - In the dialog:
     - **Repository**: Enter your GitHub repository URL (e.g., `https://github.com/renaat87/timetree-homeassistant`)
     - **Category**: Select **Integration**
   - Click **Add**

2. **Install the Integration**
   - In HACS, search for "TimeTree Calendar"
   - Click on the integration
   - Click **Download**
   - Restart Home Assistant

3. **Configure the Integration**
   - Go to **Settings** → **Devices & Services** → **Add Integration**
   - Search for "TimeTree Calendar" and click on it
   - Follow the configuration steps below

### Method 2: Manual Installation

1. Copy the `custom_components/timetree` directory to your Home Assistant `config/custom_components/` directory.

   Your directory structure should look like this:
   ```
   config/
   └── custom_components/
       └── timetree/
           ├── __init__.py
           ├── calendar.py
           ├── config_flow.py
           ├── const.py
           ├── manifest.json
           ├── strings.json
           ├── timetree_api.py
           └── translations/
               └── en.json
   ```

2. Restart Home Assistant

3. Go to **Settings** → **Devices & Services** → **Add Integration**

4. Search for "TimeTree Calendar" and click on it

## Configuration

### Step 1: Enter Credentials

1. Enter your TimeTree email address
2. Enter your TimeTree password
3. Click Submit

The integration will authenticate with TimeTree and fetch your available calendars.

### Step 2: Select Calendar and Update Interval

1. Select which calendar you want to sync from the dropdown
2. Choose your preferred update interval:
   - **5 minutes** - Most frequent updates (higher API usage)
   - **15 minutes** - Frequent updates
   - **30 minutes** - Default, balanced option
   - **1 hour** - Less frequent updates (lower API usage)
3. Click Submit

The integration will create a calendar entity in Home Assistant with your TimeTree events.

### Multiple Calendars

To sync multiple TimeTree calendars:
1. Add the integration again (repeat the setup process)
2. Select a different calendar during configuration

Each calendar will be a separate integration instance.

## Usage

### Viewing Events

Once configured, your TimeTree calendar will appear in:
- **Calendar Dashboard** - View all your calendars in one place
- **Calendar Card** - Add to your Lovelace dashboard
- **Automations** - Use calendar events as triggers

### Calendar Entity

The integration creates a calendar entity named `calendar.timetree_[calendar_name]`.

**Entity Attributes:**
- `calendar_id` - TimeTree calendar ID
- `calendar_name` - Calendar name
- `event_count` - Number of events currently synced

### Example Automation

Trigger an automation based on calendar events:

```yaml
automation:
  - alias: "Notify on Calendar Event"
    trigger:
      - platform: calendar
        entity_id: calendar.timetree_my_calendar
        event: start
    action:
      - service: notify.mobile_app
        data:
          message: "Event starting: {{ trigger.calendar_event.summary }}"
```

## Troubleshooting

### Authentication Failed

- Verify your TimeTree email and password are correct
- Make sure you're using the same credentials you use to log in to TimeTree

### Cannot Connect

- Check your internet connection
- Verify Home Assistant can reach `https://timetreeapp.com`
- Check Home Assistant logs for detailed error messages

### Events Not Updating

- Check the update interval setting
- Verify the integration is not disabled
- Check Home Assistant logs for errors
- Try reloading the integration

### Viewing Logs

To see detailed logs:
1. Go to **Settings** → **System** → **Logs**
2. Search for "timetree"

Or add this to your `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.timetree: debug
```

## Credits

This integration is built on top of the [TimeTree-Exporter](https://github.com/eoleedi/TimeTree-Exporter) project by eoleedi.

## License

This integration is provided as-is for personal use.
