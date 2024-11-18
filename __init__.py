import asyncio
from bleak import BleakScanner
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from .const import DOMAIN

SCAN_INTERVAL = 60  # Интервал сканирования в секундах


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration."""
    hass.data.setdefault(DOMAIN, {})

    async def scan_ble_devices():
        """Сканируем BLE-устройства."""
        while True:
            devices = await BleakScanner.discover()
            for device in devices:
                if is_target_device(device):
                    # Проверяем, зарегистрировано ли устройство
                    device_registry = dr.async_get(hass)
                    if not device_registry.async_get_device({(DOMAIN, device.address)}):
                        # Добавляем уведомление в Home Assistant
                        hass.bus.async_fire(
                            f"{DOMAIN}_device_found",
                            {"mac": device.address, "name": device.name},
                        )
            await asyncio.sleep(SCAN_INTERVAL)

    hass.loop.create_task(scan_ble_devices())
    return True


def is_target_device(device):
    """Проверить, является ли устройство целевым."""
    return "MyBLEDevice" in device.name  # Замените на условия для вашего устройства


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration."""
    hass.data.setdefault(DOMAIN, {})

    async def scan_ble_devices():
        """Сканируем BLE-устройства."""
        while True:
            devices = await BleakScanner.discover()
            for device in devices:
                if is_target_device(device):
                    hass.bus.async_fire(
                        f"{DOMAIN}_device_found",
                        {"mac": device.address, "name": device.name},
                    )
            await asyncio.sleep(SCAN_INTERVAL)

    hass.loop.create_task(scan_ble_devices())

    # Подписка на событие обнаружения
    async def handle_device_found_event(event):
        """Обработать найденное устройство."""
        discovery_info = event.data
        await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "ble"}, data=discovery_info
        )

    hass.bus.async_listen(f"{DOMAIN}_device_found", handle_device_found_event)

    return True
