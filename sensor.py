import asyncio
import random
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from . import HubConfigEntry

DOMAIN = "ble_dick"
devs = []  # Глобальный список для хранения найденных фруктов


async def discover_devices():
    """Функция для генерации случайного списка фруктов."""
    global devs
    fruits = ["Apple", "Banana", "Orange", "Grapes", "Pineapple", "Mango", "Peach", "Strawberry"]
    # Генерация случайного списка из 3 фруктов
    devs = random.sample(fruits, 3)  # Обновляем devs новым списком


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: HubConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Добавление сенсоров в Home Assistant."""
    hub = config_entry.runtime_data
    new_devices = []

    # Добавление сенсора случайных фруктов
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
            await asyncio.sleep(10)  # Сканируем фрукты каждые 10 секунд
            await discover_devices()
            self.async_write_ha_state()  # Обновление состояния после "обнаружения" фруктов


class BLEDeviceSensor(SensorEntity):
    """Сенсор для отображения случайных фруктов."""

    def __init__(self, roller):
        """Инициализация сенсора."""
        super().__init__()
        self._roller = roller
        self._attr_unique_id = f"{self._roller.roller_id}_ble_devices"
        self._attr_name = f"{self._roller.name} Fruit Devices"
        self._state = "No fruits found"

    @property
    def state(self):
        """Возвращает текущее состояние сенсора."""
        global devs
        return ", ".join(devs) if devs else "No fruits found"

    @property
    def icon(self):
        """Иконка сенсора."""
        return "mdi:fruit-pineapple"