from homeassistant.helpers.entity import ToggleEntity
from .const import DOMAIN
from bleak import BleakClient


class MyBLEDeviceSwitch(ToggleEntity):
    """Representation of a BLE switch."""

    def __init__(self, name, mac_address):
        self._name = name
        self._mac_address = mac_address
        self._is_on = False

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._is_on

    @property
    def unique_id(self):
        return f"{self._mac_address}-switch"

    async def async_turn_on(self, **kwargs):
        """Turn the BLE switch on."""
        from bleak import BleakClient

        # Замените на правильный UUID
        characteristic_uuid = "00002a19-0000-1000-8000-00805f9b34fb"  # Пример UUID

        try:
            async with BleakClient(self._mac_address) as client:
                await client.write_gatt_char(characteristic_uuid, b"\x01")  # Включить
            self._is_on = True
        except Exception as e:
            # Логируем ошибку, если не удалось включить устройство
            print(f"Failed to turn on the switch: {e}")

    async def async_turn_off(self, **kwargs):
        """Turn the BLE switch off."""
        from bleak import BleakClient

        # Замените на правильный UUID
        characteristic_uuid = "00002a19-0000-1000-8000-00805f9b34fb"  # Пример UUID

        try:
            async with BleakClient(self._mac_address) as client:
                await client.write_gatt_char(characteristic_uuid, b"\x00")  # Выключить
            self._is_on = False
        except Exception as e:
            # Логируем ошибку, если не удалось выключить устройство
            print(f"Failed to turn off the switch: {e}")
