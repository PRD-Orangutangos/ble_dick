import asyncio
from bleak import BleakScanner
from homeassistant.components.sensor import SensorEntity

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

    @property
    def state(self):
        """Возвращает текущее состояние сенсора."""
        return ", ".join(devs) if devs else "No devices found"

    @property
    def icon(self):
        """Иконка сенсора."""
        return "mdi:bluetooth"