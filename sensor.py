import asyncio
from bleak import BleakScanner
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ble_dick"
from . import HubConfigEntry


class BLEDeviceSensor(SensorEntity):
    """Сенсор для отображения информации о BLE устройстве."""

    def __init__(self):
        """Инициализация сенсора."""
        super().__init__()
        self._attr_unique_id = "ble_device_sensor"
        self._attr_name = "BLE Device Info"
        self._state = "No device found"
        self._connected = False  # Флаг подключения
        self._device_name = ""
        self._device_address = ""
        self.target_device_name = "QHM-12"  # Имя искомого устройства

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
            await asyncio.sleep(2)  # Обновление состояния каждые 2 секунды
            device = await discover_device_by_name(self.target_device_name)  # Поиск устройства по имени
            if device:
                self._state = f"Device found: {device.name}"  # Устройство найдено
                self._connected = False  # Устройство ещё не подключено
                self._device_name = device.name
                self._device_address = device.address
                # Логируем атрибуты перед обновлением состояния
                _LOGGER.debug(f"Updating sensor state: {self._device_name}, {self._device_address}, connected: {self._connected}")
                self.async_write_ha_state()  # Обновление состояния сенсора

            else:
                self._state = "No device found"
                self._connected = False  # Устройство не подключено
                # Логируем, что устройство не найдено
                _LOGGER.debug("No device found, resetting state.")
                self.async_write_ha_state()  # Обновление состояния сенсора

    @property
    def state(self):
        """Возвращает текущее состояние сенсора (информация о BLE устройстве)."""
        return self._state

    @property
    def icon(self):
        """Иконка сенсора."""
        if self._connected:
            return "mdi:bluetooth-connected"  # Иконка для подключенного устройства
        return "mdi:bluetooth"  # Иконка для устройства, к которому не подключены

    @property
    def device_state_attributes(self):
        """Возвращает атрибуты состояния устройства."""
        # Возвращаем атрибуты как словарь
        if self._device_name and self._device_address:
            _LOGGER.debug(f"Returning device attributes: {self._device_name}, {self._device_address}, {self._connected}")
            return {
                "device_name": self._device_name,
                "device_address": self._device_address,
                "connection_status": self._connected
            }
        return {}  # Если атрибуты не установлены, возвращаем пустой словарь

async def discover_device_by_name(target_name):
    """Функция для поиска BLE устройства с нужным именем."""
    try:
        devices = await BleakScanner.discover(timeout=2.0)
        for device in devices:
            if device.name and target_name.lower() in device.name.lower():
                # Сразу возвращаем устройство без получения информации о сервисах
                return device
    except Exception as e:
        _LOGGER.error(f"Ошибка при сканировании устройства: {e}")

    return None


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: HubConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Добавление сенсора в Home Assistant для отображения информации о BLE устройстве."""
    new_devices = []
    new_devices.append(BLEDeviceSensor())
    if new_devices:
        async_add_entities(new_devices)