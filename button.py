"""Example Button Platform."""

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

DOMAIN = "ble_dick"


async def async_setup_entry(
    hass: HomeAssistant, entry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up button platform."""
    async_add_entities([ExampleButton()])


class ExampleButton(ButtonEntity):
    """Representation of an example button."""

    def __init__(self):
        """Initialize the button."""
        self._attr_name = "Example Button"
        self._attr_unique_id = "example_button_1"

    async def async_press(self) -> None:
        """Handle the button press."""
        # Replace this with the action you want the button to perform
        print("Example button was pressed!")
