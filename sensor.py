import asyncio
from bleak import BleakScanner, BleakClient
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ble_dick"
from . import HubConfigEntry

# Глобальная переменная для хранения информации об устройстве
device_info = None

async def discover_device_by_name(target_name):
    """Функция для поиска BLE устройства с нужным именем."""
    global device_info
    try:
        devices = await BleakScanner.discover(timeout=5.0)
        for device in devices:
            if device.name and target_name.lower() in device.name.lower():
                # Подключаемся к устройству, чтобы получить его сервисы
                device_info = {
                    "name": device.name,
                    "address": device.address,
                    "services": await get_device_services(device),
                }
                return device
        # Если устройство не найдено
        device_info = None
    except Exception as e:
        _LOGGER.error(f"Ошибка при сканировании устройства: {e}")

    return None

async def get_device_services(device):
    """Получение сервисов подключённого устройства."""
    try:
        # Подключаемся к устройству через BleakClient
        async with BleakClient(device.address) as client:
            if not client.is_connected:
                await client.connect()  # Подключаемся, если не подключены
            services = await client.get_services()  # Получаем сервисы после подключения
            return [str(service) for service in services]
    except Exception as e:
        _LOGGER.error(f"Не удалось получить сервисы для устройства {device.name}: {e}")
        return []

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


class BLEDeviceSensor(SensorEntity):
    """Сенсор для отображения информации о BLE устройстве."""

    def __init__(self):
        """Инициализация сенсора."""
        super().__init__()
        self._attr_unique_id = "ble_device_sensor"
        self._attr_name = "BLE Device Info"
        self._state = "No device found"
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
            await asyncio.sleep(10)  # Обновление состояния каждые 10 секунд
            device = await discover_device_by_name(self.target_device_name)  # Поиск устройства по имени
            if device_info:
                self._state = f"Device found: {device_info['name']}"
            else:
                self._state = "No device found"
            self.async_write_ha_state()  # Обновление состояния сенсора

    @property
    def state(self):
        """Возвращает текущее состояние сенсора (информация о BLE устройстве)."""
        return self._state

    @property
    def icon(self):
        """Иконка сенсора."""
        return "mdi:bluetooth"

    @property
    def device_state_attributes(self):
        """Возвращает атрибуты сенсора для отображения в интерфейсе Home Assistant."""
        if device_info:
            return {
                "address": device_info["address"],
                "services": ", ".join(device_info["services"]),  # Список сервисов
            }
        return {}