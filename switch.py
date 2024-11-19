from bleak import BleakClient
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import logging
from . import BLEDeviceSensor  # Импортируем BLEDeviceSensor

_LOGGER = logging.getLogger(__name__)

# Константы для компонента
DOMAIN = "ble_dick"
RSC_MEASUREMENT_UUID = "00002a53-0000-1000-8000-00805f9b34fb"  # UUID RSC Measurement


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Настройка платформы Switch."""
    # Добавляем один виртуальный переключатель
    async_add_entities([ExampleSwitch(hass)])


class ExampleSwitch(SwitchEntity):
    """Пример кастомного переключателя."""

    def __init__(self, hass: HomeAssistant):
        """Инициализация переключателя."""
        self._attr_is_on = False  # Текущее состояние (выключен)
        self._attr_name = "Example Switch"  # Имя переключателя
        self._hass = hass  # Сохраняем ссылку на Home Assistant
        self._client = None  # BLE клиент
        self._device_address = "00:00:00:00:00:00"  # Адрес устройства, заменить на реальный
        self._connected = False  # Флаг подключения

    @property
    def is_on(self) -> bool:
        """Возвращает текущее состояние переключателя."""
        return self._attr_is_on

    @property
    def available(self) -> bool:
        """Возвращает доступность переключателя (кнопки)."""
        return self._connected  # Кнопка доступна только если устройство подключено

    async def async_turn_on(self, **kwargs):
        """Включение переключателя и запуск уведомлений."""
        if not self._connected:
            _LOGGER.warning("Cannot turn on, BLE device is not connected.")
            return

        self._attr_is_on = True
        # Запуск уведомлений для сервиса RSC_MEASUREMENT_UUID
        if self._client:
            await self._client.start_notify(RSC_MEASUREMENT_UUID, lambda sender, data: None)
        self.async_write_ha_state()  # Уведомляем Home Assistant об изменении состояния

    async def async_turn_off(self, **kwargs):
        """Выключение переключателя и остановка уведомлений."""
        if not self._connected:
            _LOGGER.warning("Cannot turn off, BLE device is not connected.")
            return

        self._attr_is_on = False
        # Остановка уведомлений для сервиса RSC_MEASUREMENT_UUID
        if self._client:
            await self._client.stop_notify(RSC_MEASUREMENT_UUID)
        self.async_write_ha_state()  # Уведомляем Home Assistant об изменении состояния

    async def async_added_to_hass(self):
        """Действия при добавлении переключателя в Home Assistant."""
        # Получаем BLE клиент из другого сенсора
        sensor = next(entity for entity in self._hass.data[DOMAIN].values() if isinstance(entity, BLEDeviceSensor))
        if sensor and sensor._client and sensor._client.is_connected:
            self._client = sensor._client  # Используем уже существующий клиент
            self._connected = True  # Устанавливаем флаг подключения
            _LOGGER.debug(f"Using existing client for device: {sensor._device_name}")
        else:
            _LOGGER.warning("No connected client found. Make sure the BLE device is connected.")
            self._connected = False  # Устройство не подключено

        self.async_write_ha_state()  # Обновляем состояние кнопки

    async def async_will_remove_from_hass(self):
        """Действия при удалении переключателя из Home Assistant."""
        if self._client and self._client.is_connected:
            await self._client.disconnect()  # Отключаем клиента
            self._connected = False  # Отключаем флаг подключения
            _LOGGER.debug("Disconnected from BLE device.")