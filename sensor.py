from homeassistant.helpers.entity import Entity
from .const import DOMAIN

from homeassistant.components.image import ImageEntity


class YourIntegrationImageEntity(ImageEntity):
    def __init__(self, name, image_path):
        self._name = name
        self._image_path = image_path

    @property
    def name(self):
        return self._name

    @property
    def image(self):
        return self._image_path


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
