"""RT_T Bluetooth temperature/humidity logger."""

from __future__ import annotations

import logging

from homeassistant.components.bluetooth import (
    BluetoothScanningMode,
    BluetoothServiceInfoBleak,
)
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothProcessorCoordinator,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

PLATFORMS: list[Platform] = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)

type RTTConfigEntry = ConfigEntry[
    PassiveBluetoothProcessorCoordinator[BluetoothServiceInfoBleak]
]


def _passthrough(service_info: BluetoothServiceInfoBleak) -> BluetoothServiceInfoBleak:
    """Hand the advertisement to the sensor processor unchanged."""
    return service_info


async def async_setup_entry(hass: HomeAssistant, entry: RTTConfigEntry) -> bool:
    """Set up the logger from a config entry."""
    address = entry.unique_id
    assert address is not None
    coordinator = PassiveBluetoothProcessorCoordinator(
        hass,
        _LOGGER,
        address=address,
        mode=BluetoothScanningMode.PASSIVE,
        update_method=_passthrough,
    )
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    # Start only after the sensor platform has registered its processor.
    entry.async_on_unload(coordinator.async_start())
    return True


async def async_unload_entry(hass: HomeAssistant, entry: RTTConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
