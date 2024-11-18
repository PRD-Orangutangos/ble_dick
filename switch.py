import asyncio
import logging
import json
from homeassistant.components.sensor import SensorEntity

_LOGGER = logging.getLogger(__name__)

class BLEDeviceSensor(SensorEntity):
    """Сенсор для отображения информации о BLE устройстве."""

    def __init__(self):
        """Инициализация сенсора."""
        super().__init__()
        self._attr_unique_id = "ble_device_sensor"
        self._attr_name = "BLE Device Info"
        self._state = "No device found"
        self._connected = False
        self.target_device_name = "QHM-12"  # Имя искомого устройства
        self._services = []
        self._service_chunks = []

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
            device_info = await discover_device_by_name(self.target_device_name)  # Поиск устройства по имени
            if device_info and not self._connected:  # Если устройство найдено и не подключено
                self._state = f"Device found: {device_info['name']}"
                self._connected = True  # Устройство подключено
                self._services = device_info["services"]  # Получаем информацию о сервисах
                _LOGGER.info(f"Сервисы устройства {device_info['name']}: {self._services}")
                
                # Разбиение списка сервисов на несколько частей, если длина превышает 255 символов
                self._service_chunks = [self._services[i:i + 5] for i in range(0, len(self._services), 5)]
            elif not device_info and self._connected:
                self._state = "No device found"
                self._connected = False
                self._services = []
                self._service_chunks = []
            self.async_write_ha_state()

    @property
    def state(self):
        """Возвращает текущее состояние сенсора (информация о BLE устройстве)."""
        return self._state

    @property
    def icon(self):
        """Иконка сенсора."""
        if self._connected:
            return "mdi:bluetooth-connected"
        return "mdi:bluetooth"

    @property
    def device_state_attributes(self):
        """Возвращает атрибуты сенсора для отображения в интерфейсе Home Assistant."""
        attributes = {
            "address": device_info["address"] if device_info else "No device found",
            "connected": self._connected,
        }

        # Разделяем список сервисов на части и сохраняем их как отдельные атрибуты
        for idx, chunk in enumerate(self._service_chunks):
            chunk_data = ", ".join(chunk)
            # Убедимся, что атрибут не превышает 255 символов
            if len(chunk_data) <= 255:
                attributes[f"services_part_{idx + 1}"] = chunk_data
            else:
                attributes[f"services_part_{idx + 1}"] = "Data too long"
        
        return attributes