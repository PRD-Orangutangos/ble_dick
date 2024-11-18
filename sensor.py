import asyncio
from bleak import BleakScanner
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

DOMAIN = "ble_dick"
from . import HubConfigEntry
# Глобальный список для хранения доступных устройств
devs = []

async def discover_devices():
    """Функция для поиска доступных BLE устройств."""
    global devs
    try:
        devices = await BleakScanner.discover(timeout=5.0)
        devs.clear()
        if devices:
            devs.extend([device.name or f"Unknown ({device.address})" for device in devices])
        else:
            devs.append("No devices found")
    except Exception as e:
        devs.append(f"Error: {e}")

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: HubConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Добавление сенсоров в Home Assistant."""
    new_devices = []

    # Добавление сенсора для отображения найденных BLE устройств
    new_devices.append(BLEDeviceSensor())

    if new_devices:
        async_add_entities(new_devices)


class BLEDeviceSensor(SensorEntity):
    """Сенсор для отображения списка BLE устройств."""

    def __init__(self):
        """Инициализация сенсора."""
        super().__init__()
        self._attr_unique_id = "ble_devices_sensor"
        self._attr_name = "BLE Devices"
        self._state = "No devices found"

    async def async_added_to_hass(self):
        """Действие при добавлении в Home Assistant."""
        self._update_task = asyncio.create_task(self._periodic_update())

    async def async_will_remove_from_hass(self):
        """Действие при удалении из Home Assistant."""
        if hasattr(self, "_update_task"):
            self._update_task.cancel()

    async def _periodic_update(self):
        """Периодическая задача для обновления состояния."""
        while True:
            await asyncio.sleep(10)  # Обновление состояния каждые 10 секунд
            await discover_devices()  # Поиск BLE устройств
            self.async_write_ha_state()  # Обновление состояния сенсора

    @property
    def state(self):
        """Возвращает текущее состояние сенсора (список BLE устройств)."""
        global devs
        return ", ".join(devs) if devs else "No devices found"

    @property
    def icon(self):
        """Иконка сенсора."""
        return "mdi:bluetooth"