from homeassistant import config_entries
from homeassistant.const import CONF_NAME
import voluptuous as vol


class BleDickConfigFlow(config_entries.ConfigFlow):
    """Handle a config flow for BLE Dick integration."""

    def __init__(self):
        """Initialize the flow."""
        self._name = None

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_NAME, default="BLE Dick Device"): str,
                    }
                ),
            )

        # После ввода данных создаем запись конфигурации
        return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)
