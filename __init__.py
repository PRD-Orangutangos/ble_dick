"""The BLE Dick integration."""

import logging

# Логирование интеграции
_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    """Set up the BLE Dick integration."""
    _LOGGER.info("Setting up BLE Dick integration")
    return True
