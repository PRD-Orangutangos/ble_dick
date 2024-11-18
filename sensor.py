from homeassistant.helpers.entity import Entity
from .const import DOMAIN


class MyBLEDeviceSensor(Entity):
    """Representation of a BLE sensor."""

    def __init__(self, name, mac_address):
        self._name = name
        self._mac_address = mac_address
        self._state = None

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unique_id(self):
        return f"{self._mac_address}-sensor"

    async def async_update(self):
        """Fetch new state data from the BLE device."""
        from bleak import BleakClient

        async with BleakClient(self._mac_address) as client:
            data = await client.read_gatt_char("UUID_CHARACTERISTIC")  # Замените UUID
            self._state = int.from_bytes(data, "little")  # Пример обработки данных
