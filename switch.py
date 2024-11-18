from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

# Константы для компонента
DOMAIN = "ble_dick"


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Настройка платформы Switch."""
    # Добавляем один виртуальный переключатель
    async_add_entities([ExampleSwitch()])


class ExampleSwitch(SwitchEntity):
    """Пример кастомного переключателя."""

    def __init__(self):
        """Инициализация переключателя."""
        self._attr_is_on = False  # Текущее состояние (выключен)
        self._attr_name = "Example Switch"  # Имя переключателя

    @property
    def is_on(self) -> bool:
        """Возвращает текущее состояние переключателя."""
        return self._attr_is_on

    async def async_turn_on(self, **kwargs):
        """Включение переключателя."""
        self._attr_is_on = True
        self.async_write_ha_state()  # Уведомляем Home Assistant об изменении состояния

    async def async_turn_off(self, **kwargs):
        """Выключение переключателя."""
        self._attr_is_on = False
        self.async_write_ha_state()
