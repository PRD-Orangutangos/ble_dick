import asyncio
import random
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from . import HubConfigEntry

DOMAIN = "fruit_sensor"

# Глобальный список фруктов
fruits = ["Apple", "Banana", "Orange", "Grapes", "Pineapple", "Mango", "Peach", "Strawberry"]

async def discover_fruits():
    """Функция для генерации случайного списка фруктов."""
    global fruits_list
    fruits_list = random.sample(fruits, 3)  # Список из 3 случайных фруктов


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: HubConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Добавление сенсоров в Home Assistant."""
    hub = config_entry.runtime_data
    new_devices = []

    # Добавление сенсора для отображения случайных фруктов
    new_devices.append(FruitSensor())

    if new_devices:
        async_add_entities(new_devices)


class FruitSensor(SensorEntity):
    """Сенсор для отображения случайных фруктов."""

    def __init__(self):
        """Инициализация сенсора."""
        super().__init__()
        self._attr_unique_id = "fruit_sensor"
        self._attr_name = "Random Fruit"
        self._state = "No fruits found"

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
            await discover_fruits()  # Генерация случайных фруктов
            self.async_write_ha_state()  # Обновление состояния сенсора

    @property
    def state(self):
        """Возвращает текущее состояние сенсора."""
        global fruits_list
        return ", ".join(fruits_list) if fruits_list else "No fruits found"

    @property
    def icon(self):
        """Иконка сенсора."""
        return "mdi:fruit-pineapple"