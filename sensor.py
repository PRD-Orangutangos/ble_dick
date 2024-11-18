import asyncio
from homeassistant.components.sensor import SensorEntity
from bleak import BleakScanner

DOMAIN = "ble_dick"


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Добавление сенсора в Home Assistant."""
    async_add_entities([BLEDeviceSensor()])


class BLEDeviceSensor(SensorEntity):
    """Сенсор для отображения BLE-устройств."""

    _attr_icon = "mdi:bluetooth"
    _attr_name = "BLE Devices"
    _attr_should_poll = False

    def __init__(self):
        """Инициализация сенсора."""
        self._attr_state = "No devices found"  # Начальное состояние
        self._devices = []

    async def async_added_to_hass(self):
        """Действие при добавлении сенсора."""
        # Запускаем периодическое обновление
        self._update_task = asyncio.create_task(self._periodic_update())

    async def async_will_remove_from_hass(self):
        """Действие при удалении сенсора."""
        if hasattr(self, "_update_task"):
            self._update_task.cancel()

    async def _periodic_update(self):
        """Периодическое обновление списка BLE-устройств."""
        while True:
            try:
                devices = await BleakScanner.discover()
                self._devices = [
                    device.name or f"Unknown ({device.address})" for device in devices
                ]
                if self._devices:
                    self._attr_state = ", ".join(self._devices)
                else:
                    self._attr_state = "No devices found"
            except Exception as e:
                self._attr_state = f"Error: {e}"
                print(f"BLE Scan Error: {e}")

            self.async_write_ha_state()
            await asyncio.sleep(10)  # Сканируем каждые 10 секунд