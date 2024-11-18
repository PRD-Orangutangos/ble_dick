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
    try:
        devices = await BleakScanner.discover(timeout=5.0)
        for device in devices:
            if device.name and target_name.lower() in device.name.lower():
                return device
        return None
    except Exception as e:
        _LOGGER.error(f"Ошибка при сканировании устройства: {e}")
        return None

async def get_device_services(device):
    """Получение сервисов подключённого устройства."""
    try:
        async with BleakClient(device.address) as client:
            if not client.is_connected:
                await client.connect()
            _LOGGER.info(f"Подключено к устройству {device.name} ({device.address})")

            services = client.services
            if services:
                services_list = [f"{service.uuid} ({service.handle}): {service.description}" for service in services]
                return services_list
            else:
                _LOGGER.warning(f"Устройство {device.name} не предоставляет сервисы.")
                return []
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
        self._connected = False
        self._device_info = None  # Атрибут для хранения информации об устройстве
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
            device = await discover_device_by_name(self.target_device_name)
            if device:
                self._state = f"Device found: {device.name}"
                self._connected = False
                self.async_write_ha_state()

                services = await get_device_services(device)
                if services:
                    self._device_info = {
                        "name": device.name,
                        "address": device.address,
                        "services": services,
                    }
                    self._state = f"Device connected: {device.name}"
                    self._connected = True
                else:
                    self._device_info = None
                    self._state = "No services found"
                    self._connected = False
                self.async_write_ha_state()
            else:
                self._state = "No device found"
                self._connected = False
                self._device_info = None
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
        if self._device_info:
            # Ограничение длины атрибута для сервисов
            services = ", ".join(self._device_info["services"]) if self._device_info["services"] else "No services"
            if len(services) > 255:
                services = services[:255]  # Обрезаем строку, если она слишком длинная

            # Разделим сервисы на несколько атрибутов, если они слишком длинные
            service_parts = [services[i:i+255] for i in range(0, len(services), 255)]

            # Возвращаем атрибуты с разделенными сервисами
            return {
                "address": self._device_info["address"],
                "connected": self._connected,
                "services_part_1": service_parts[0] if len(service_parts) > 0 else "",
                "services_part_2": service_parts[1] if len(service_parts) > 1 else "",
                "services_part_3": service_parts[2] if len(service_parts) > 2 else "",
            }
        return {}