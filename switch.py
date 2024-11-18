from homeassistant.helpers.entity import ToggleEntity
from .const import DOMAIN


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
        from bleak import BleakClient

        async with BleakClient(self._mac_address) as client:
            await client.write_gatt_char(
                "UUID_CHARACTERISTIC", b"\x01"
            )  # Пример команды
        self._is_on = True

    async def async_turn_off(self, **kwargs):
        from bleak import BleakClient

        async with BleakClient(self._mac_address) as client:
            await client.write_gatt_char(
                "UUID_CHARACTERISTIC", b"\x00"
            )  # Пример команды
        self._is_on = False
