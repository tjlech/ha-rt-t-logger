"""Decoder for the RT_T (BT04) temperature/humidity logger broadcast.

The logger sends its readings openly in BLE service data, UUID 0xCBFF,
17 bytes. Layout (checked against the logger's display):

    bytes 0-7   unknown (device id or date)
    byte  8     battery, percent
    byte  9     unknown
    bytes 10-11 temperature, signed big-endian, / 100 -> degrees C
    bytes 12-13 relative humidity, big-endian, / 100 -> percent
    bytes 14-16 unknown

This module has no Home Assistant imports so it can be tested on its own.
"""

from __future__ import annotations

from dataclasses import dataclass

SERVICE_UUID = "0000cbff-0000-1000-8000-00805f9b34fb"
MIN_LENGTH = 14


@dataclass(frozen=True, slots=True)
class RTTReading:
    """One decoded broadcast."""

    temperature: float
    humidity: float
    battery: int


def parse_service_data(data: bytes) -> RTTReading | None:
    """Decode the 0xCBFF service data; None if it doesn't look valid."""
    if len(data) < MIN_LENGTH:
        return None
    battery = data[8]
    temperature = int.from_bytes(data[10:12], "big", signed=True) / 100
    humidity = int.from_bytes(data[12:14], "big") / 100
    if not (-40 <= temperature <= 85 and 0 <= humidity <= 100 and battery <= 100):
        return None
    return RTTReading(temperature=temperature, humidity=humidity, battery=battery)
