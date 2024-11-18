import asyncio
from bleak import BleakScanner
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from . import HubConfigEntry

DOMAIN = "ble_dick"
devs = []  # Глобальный список для хранения найденных устройств


async def discover_devices():
    """Функция для поиска всех доступных Bluetooth устройств."""
    global devs
    print("Поиск BLE-устройств...")
    try:
        devices = await BleakScanner.discover()
        print(f"Найдено {len(devices)} устройств.")  # Отладочное сообщение
        devs.clear()
        if devices:
            devs.extend([device.name or f"Unknown ({device.address})" for device in devices])
        else:
            devs.append("No devices found")
        print(f"Устройства: {devs}")  # Выводим устройства для отладки
    except Exception as e:
        print(f"Ошибка при сканировании BLE: {e}")
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
        print(f"Создан сенсор для {self._roller.name}")  # Отладочное сообщение

    @property
    def state(self):
        """Возвращает текущее состояние сенсора."""
        global devs
        print(f"Текущее состояние сенсора: {', '.join(devs)}")  # Отладочное сообщение
        return ", ".join(devs) if devs else "No devices found"

    @property
    def icon(self):
        """Иконка сенсора."""
        return "mdi:bluetooth"