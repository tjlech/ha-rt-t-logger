"""Sensors for the RT_T logger."""

from __future__ import annotations

from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothDataProcessor,
    PassiveBluetoothDataUpdate,
    PassiveBluetoothEntityKey,
    PassiveBluetoothProcessorEntity,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    EntityCategory,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import RTTConfigEntry
from .const import MANUFACTURER, MODEL
from .parser import SERVICE_UUID, parse_service_data

DESCRIPTIONS: dict[str, SensorEntityDescription] = {
    "temperature": SensorEntityDescription(
        key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    "humidity": SensorEntityDescription(
        key="humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    "battery": SensorEntityDescription(
        key="battery",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "signal_strength": SensorEntityDescription(
        key="signal_strength",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
}

NAMES = {
    "temperature": "Temperature",
    "humidity": "Humidity",
    "battery": "Battery",
    "signal_strength": "Signal strength",
}


def _key(name: str) -> PassiveBluetoothEntityKey:
    return PassiveBluetoothEntityKey(name, None)


def service_info_to_update(
    service_info: BluetoothServiceInfoBleak,
) -> PassiveBluetoothDataUpdate[float | int | None]:
    """Turn one advertisement into entity values."""
    data = service_info.service_data.get(SERVICE_UUID)
    reading = parse_service_data(data) if data else None
    if reading is None:
        return PassiveBluetoothDataUpdate()
    values: dict[str, float | int] = {
        "temperature": reading.temperature,
        "humidity": reading.humidity,
        "battery": reading.battery,
        "signal_strength": service_info.rssi,
    }
    return PassiveBluetoothDataUpdate(
        devices={
            None: DeviceInfo(
                name=service_info.name or "RT_T",
                manufacturer=MANUFACTURER,
                model=MODEL,
            )
        },
        entity_descriptions={_key(k): DESCRIPTIONS[k] for k in values},
        entity_names={_key(k): NAMES[k] for k in values},
        entity_data={_key(k): v for k, v in values.items()},
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RTTConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the sensors."""
    coordinator = entry.runtime_data
    processor = PassiveBluetoothDataProcessor(service_info_to_update)
    entry.async_on_unload(
        processor.async_add_entities_listener(RTTSensor, async_add_entities)
    )
    entry.async_on_unload(
        coordinator.async_register_processor(processor, SensorEntityDescription)
    )


class RTTSensor(
    PassiveBluetoothProcessorEntity[
        PassiveBluetoothDataProcessor[float | int | None, BluetoothServiceInfoBleak]
    ],
    SensorEntity,
):
    """One RT_T reading."""

    @property
    def native_value(self) -> float | int | None:
        return self.processor.entity_data.get(self.entity_key)
