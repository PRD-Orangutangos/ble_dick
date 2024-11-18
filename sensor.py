import asyncio
from bleak import BleakScanner
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import Entity

devs = []  # Глобальный список для хранения найденных BLE устройств

async def discover_devices():
    """Функция для поиска всех доступных Bluetooth устройств."""
    global devs
    try:
        # Запуск сканирования устройств с ограничением времени (например, 5 секунд)
        devices = await BleakScanner.discover(timeout=5.0)
        devs.clear()
        if devices:
            # Сохраняем имена устройств (или их адреса, если имя отсутствует)
            devs.extend([device.name or f"Unknown ({device.address})" for device in devices])
        else:
            devs.append("No devices found")
    except Exception:
        devs.append("Scan error")

class BLEDeviceSensor(SensorEntity):
    """Сенсор для отображения BLE-устройств."""

    def __init__(self):
        """Инициализация сенсора."""
        self._state = "No devices found"
        self._attr_name = "BLE Devices"
        self._attr_unique_id = "ble_devices_sensor"

    @property
    def state(self):
        """Возвращает текущее состояние сенсора."""
        return ", ".join(devs) if devs else "No devices found"

    @property
    def icon(self):
        """Иконка сенсора."""
        return "mdi:bluetooth"

    async def async_update(self):
        """Метод для обновления состояния сенсора."""
        await discover_devices()  # Выполнение поиска BLE устройств
        self._attr_state = self.state  # Обновление состояния сенсора

    async def async_added_to_hass(self):
        """Действия при добавлении в Home Assistant."""
        self._update_task = asyncio.create_task(self._periodic_update())

    async def async_will_remove_from_hass(self):
        """Действия при удалении из Home Assistant."""
        if hasattr(self, "_update_task"):
            self._update_task.cancel()

    async def _periodic_update(self):
        """Периодическая задача для обновления состояния."""
        while True:
            await asyncio.sleep(10)  # Обновление данных каждые 10 секунд
            await self.async_update()  # Обновление данных
            self.async_write_ha_state()  # Обновление состояния сенсора в Home Assistant