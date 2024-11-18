from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
import voluptuous as vol


class BleDickConfigFlow(config_entries.ConfigFlow):
    """Handle a config flow for BLE Dick integration."""

    VERSION = 1

    def __init__(self):
        """Initialize the flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._discovered_devices: dict[str, BluetoothServiceInfoBleak] = {}

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> config_entries.ConfigFlowResult:
        """Handle the bluetooth discovery step."""
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        self._discovery_info = discovery_info
        self.context["title_placeholders"] = {"name": discovery_info.name}
        return await self.async_step_user()

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the user step to pick discovered device."""
        errors: dict[str, str] = {}

        if user_input is not None:
            address = user_input[CONF_NAME]
            discovery_info = self._discovered_devices[address]
            await self.async_set_unique_id(
                discovery_info.address, raise_on_progress=False
            )
            self._abort_if_unique_id_configured()

            # Дополнительная логика работы с устройством (например, подключение, обновление состояния)
            # Пример проверки соединения с устройством:
            try:
                # Здесь может быть ваш код для взаимодействия с устройством, например, проверка доступности
                pass
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                # Если устройство успешно настроено
                return self.async_create_entry(
                    title=discovery_info.name,
                    data={CONF_NAME: discovery_info.name},
                )

        if discovery := self._discovery_info:
            self._discovered_devices[discovery.address] = discovery
        else:
            current_addresses = self._async_current_ids()
            # Заполнение списка доступных устройств
            for discovery in async_discovered_service_info(self.hass):
                if discovery.address in current_addresses:
                    continue
                self._discovered_devices[discovery.address] = discovery

        if not self._discovered_devices:
            return self.async_abort(reason="no_devices_found")

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME): vol.In(
                    {
                        service_info.address: f"{service_info.name} ({service_info.address})"
                        for service_info in self._discovered_devices.values()
                    }
                ),
            }
        )
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
