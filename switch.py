from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import logging
from bleak import BleakClient, discover  # Используем BleakClient и discover для поиска устройств
import asyncio

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ble_dick"
RSC_MEASUREMENT_UUID = "00002a53-0000-1000-8000-00805f9b34fb"  # UUID RSC Measurement
from . import HubConfigEntry

async def async_setup_entry(hass: HomeAssistant, entry: HubConfigEntry, async_add_entities: AddEntitiesCallback):
    """Настройка компонента через конфигурацию Home Assistant."""
    switch = ExampleSwitch(hass)
    async_add_entities([switch])  # Добавляем сущность в Home Assistant

class ExampleSwitch(SwitchEntity):
    """Пример кастомного переключателя с поиском устройства и подключением."""

    def __init__(self, hass: HomeAssistant):
        """Инициализация переключателя."""
        self._attr_is_on = False  # Текущее состояние (выключен)
        self._attr_name = "Gomik button"  # Имя переключателя
        self._hass = hass  # Сохраняем ссылку на Home Assistant
        self._client = None  # BLE клиент
        self._device_address = ""  # Адрес устройства
        self.target_device_name = "QHM-12"  # Имя искомого устройства
        self._connected = False  # Флаг подключения
        self._device_name = ""
        self._reconnect_task = None  # Задача для переподключения

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
        if self._connected:
            self._attr_is_on = True
            if self._client:
                await self._client.start_notify(RSC_MEASUREMENT_UUID, lambda sender, data: None)
            self.async_write_ha_state()  # Уведомляем Home Assistant об изменении состояния
        else:
            _LOGGER.warning("Device is not connected. Cannot turn on the switch.")

    async def async_turn_off(self, **kwargs):
        """Выключение переключателя и остановка уведомлений."""
        if self._connected:
            self._attr_is_on = False
            if self._client:
                await self._client.stop_notify(RSC_MEASUREMENT_UUID)
            self.async_write_ha_state()  # Уведомляем Home Assistant об изменении состояния
        else:
            _LOGGER.warning("Device is not connected. Cannot turn off the switch.")

    async def async_added_to_hass(self):
        """Действия при добавлении переключателя в Home Assistant."""
        await self._connect_to_device()  # Попытка подключения к устройству
        self.async_write_ha_state()  # Обновляем состояние после инициализации

    async def async_will_remove_from_hass(self):
        """Действия при удалении переключателя из Home Assistant."""
        if self._client and self._connected:
            await self._client.disconnect()  # Отключаем клиента
        if self._reconnect_task:
            self._reconnect_task.cancel()  # Отменяем задачу переподключения, если она есть

    async def _connect_to_device(self):
        """Метод для поиска и подключения к BLE устройству."""
        devices = await discover()  # Используем bleak для поиска устройств
        target_device = None

        for device in devices:
            if device.name == self.target_device_name:
                target_device = device
                self._device_address = device.address
                self._device_name = device.name
                break

        if target_device:
            _LOGGER.debug(f"Found device: {self._device_name}, {self._device_address}")
            try:
                self._client = BleakClient(self._device_address)
                await self._client.connect()
                self._connected = True
                _LOGGER.info(f"Connected to device: {self._device_name}")
                self._reconnect_task = asyncio.create_task(self._monitor_connection())
            except Exception as e:
                _LOGGER.error(f"Failed to connect to device: {e}")
                self._connected = False
        else:
            _LOGGER.debug("No device found.")
            self._connected = False