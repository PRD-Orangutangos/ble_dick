import asyncio
import logging
from bleak import BleakScanner
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

# Настройка логгера
_LOGGER = logging.getLogger(__name__)

# Устанавливаем уровень логирования
_LOGGER.setLevel(logging.DEBUG)

# Настройка логирования для вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
_LOGGER.addHandler(console_handler)

DOMAIN = "ble_dick"
devs = []  # Глобальный список для хранения найденных BLE устройств


async def discover_devices():
    """Функция для поиска всех доступных Bluetooth устройств."""
    global devs
    _LOGGER.info("Поиск BLE-устройств...")  # Логируем начало сканирования
    try:
        # Запуск сканирования устройств с ограничением времени (например, 5 секунд)
        devices = await BleakScanner.discover(timeout=5.0)
        _LOGGER.info(f"Найдено {len(devices)} устройств.")  # Логируем количество найденных устройств
        devs.clear()
        if devices:
            # Сохраняем имена устройств (или их адреса, если имя отсутствует)
            devs.extend([device.name or f"Unknown ({device.address})" for device in devices])
        else:
            devs.append("No devices found")
        _LOGGER.info(f"Устройства: {devs}")  # Логируем найденные устройства
    except Exception as e:
        _LOGGER.error(f"Ошибка при сканировании BLE: {e}")  # Логируем ошибку
        devs.append("Scan error")


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: HubConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Добавление сенсоров в Home Assistant."""
    hub = config_entry.runtime_data
    new_devices = []

    # Добавление сенсора BLE-устройств
    for roller in hub.rollers:
        new_devices.append(BLEDeviceSensor(roller))

    if new_devices:
        async_add_entities(new_devices)


class SensorBase(Entity):
    """Базовый класс для сенсоров."""

    should_poll = False

    def __init__(self, roller):
        """Инициализация сенсора."""
        self._roller = roller

    @property
    def device_info(self):
        """Информация о связанной сущности."""
        return {"identifiers": {(DOMAIN, self._roller.roller_id)}}

    @property
    def available(self) -> bool:
        """Состояние доступности сенсора."""
        return self._roller.online and self._roller.hub.online

    async def async_added_to_hass(self):
        """Действие при добавлении в Home Assistant."""
        self._roller.register_callback(self.async_write_ha_state)
        self._update_task = asyncio.create_task(self._periodic_update())

    async def async_will_remove_from_hass(self):
        """Действие при удалении из Home Assistant."""
        self._roller.remove_callback(self.async_write_ha_state)
        if hasattr(self, "_update_task"):
            self._update_task.cancel()

    async def _periodic_update(self):
        """Периодическая задача для обновления состояния."""
        while True:
            await asyncio.sleep(10)  # Сканируем BLE каждые 10 секунд
            await discover_devices()
            self.async_write_ha_state()  # Обновление состояния после сканирования


class BLEDeviceSensor(SensorEntity):
    """Сенсор для отображения BLE-устройств."""

    def __init__(self, roller):
        """Инициализация сенсора."""
        super().__init__()
        self._roller = roller
        self._attr_unique_id = f"{self._roller.roller_id}_ble_devices"
        self._attr_name = f"{self._roller.name} BLE Devices"
        self._state = "No devices found"
        _LOGGER.debug(f"Создан сенсор для {self._roller.name}")  # Логируем создание сенсора

    @property
    def state(self):
        """Возвращает текущее состояние сенсора."""
        global devs
        if not devs:
            _LOGGER.debug("Нет доступных BLE устройств.")  # Логируем, если нет устройств
        _LOGGER.debug(f"Текущее состояние сенсора: {', '.join(devs)}")  # Логируем состояние сенсора
        return ", ".join(devs) if devs else "No devices found"

    @property
    def icon(self):
        """Иконка сенсора."""
        return "mdi:bluetooth"