"""Parser tests: python3 -m unittest discover tests (no Home Assistant needed)."""

import importlib.util
import pathlib
import sys
import unittest

_path = pathlib.Path(__file__).parents[1] / "custom_components/rt_t_logger/parser.py"
_spec = importlib.util.spec_from_file_location("rtt_parser", _path)
parser = importlib.util.module_from_spec(_spec)
sys.modules["rtt_parser"] = parser
_spec.loader.exec_module(parser)


def frame(temp: int, hum: int, battery: int = 100) -> bytes:
    return (
        bytes(8)
        + bytes([battery, 0])
        + temp.to_bytes(2, "big", signed=True)
        + hum.to_bytes(2, "big")
        + bytes(3)
    )


class ParserTest(unittest.TestCase):
    def test_reading_matching_display(self):
        r = parser.parse_service_data(frame(0x094C, 0x1194))
        self.assertEqual((r.temperature, r.humidity, r.battery), (23.8, 45.0, 100))

    def test_second_sample(self):
        r = parser.parse_service_data(frame(0x0910, 0x11F8))
        self.assertEqual((r.temperature, r.humidity), (23.2, 46.0))

    def test_negative_temperature(self):
        self.assertEqual(parser.parse_service_data(frame(-550, 8000)).temperature, -5.5)

    def test_short_or_bogus(self):
        self.assertIsNone(parser.parse_service_data(bytes(13)))
        self.assertIsNone(parser.parse_service_data(frame(0x094C, 0xFFFF)))
        self.assertIsNone(parser.parse_service_data(frame(0x094C, 0x1194, battery=200)))


if __name__ == "__main__":
    unittest.main()
