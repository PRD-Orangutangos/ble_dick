from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from .const import DOMAIN


class MyBLEDeviceConfigFlow(config_entries.ConfigFlow):
    """Handle a config flow for My BLE Device."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Ручная настройка (если нужна)."""
        if user_input is not None:
            return self.async_create_entry(title="My BLE Device", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("mac_address"): str,
                }
            ),
        )

    @callback
    async def async_step_discovery(self, discovery_info):
        """Обработать автоматически найденное устройство через Bluetooth."""
        mac_address = discovery_info["mac"]
        name = discovery_info.get("name", "Unknown Device")
        return self.async_create_entry(title=name, data={"mac_address": mac_address})
