import asyncio
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from bleak import BleakScanner

DOMAIN = "ble_dick"  # Укажите ваш домен


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Добавление сенсоров BLE-устройств в Home Assistant."""
    async_add_entities([BLEDeviceSensor()])


class BLEDeviceSensor(SensorEntity):
    """Сенсор для отображения BLE-устройств."""

    _attr_icon = "mdi:bluetooth"
    _attr_name = "BLE Devices"
    _attr_should_poll = False

    def __init__(self):
        """Инициализация сенсора."""
        self._state = "No devices found"
        self._devices = []

    @property
    def state(self):
        """Возвращает текущее состояние сенсора."""
        return ", ".join(self._devices) if self._devices else self._state

    async def async_added_to_hass(self):
        """Действие при добавлении сенсора в Home Assistant."""
        # Запускаем периодическое обновление BLE-сканирования
        self._update_task = asyncio.create_task(self._periodic_update())

    async def async_will_remove_from_hass(self):
        """Действие при удалении сенсора из Home Assistant."""
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
            except Exception as e:
                self._devices = [f"Error: {e}"]

            self.async_write_ha_state()
            await asyncio.sleep(10)  # Сканируем каждые 10 секунд