# RT_T Bluetooth Logger for Home Assistant

Reads the cheap **RT_T** Bluetooth temperature/humidity logger (phone app "RT_T BT04")
in Home Assistant. The logger broadcasts its readings openly, so no pairing or
connection is needed: any Home Assistant Bluetooth adapter or ESPHome Bluetooth proxy
within range picks them up.

Entities per logger: temperature, humidity, battery, and signal strength (disabled by default).

## Install (HACS)

1. HACS → ⋮ → Custom repositories → `https://github.com/tjlech/ha-rt-t-logger`, type **Integration**.
2. Download **RT_T Bluetooth Logger**, restart Home Assistant.
3. The logger is discovered automatically (Settings → Devices & services). You can also
   add it by hand: Add integration → RT_T Bluetooth Logger.

## Broadcast format

Service data UUID `0xCBFF`, 17 bytes:

| Bytes | Meaning |
|-------|---------|
| 0-7   | unknown (device id or date) |
| 8     | battery, % |
| 10-11 | temperature, signed big-endian, ÷100 → °C |
| 12-13 | relative humidity, big-endian, ÷100 → % |

Decoded against the logger's display. Negative temperatures are assumed to be
two's complement; this hasn't been checked on a real device below 0 °C.

## Tests

`python3 -m unittest discover -s tests` (parser only, no Home Assistant needed).
