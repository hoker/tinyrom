from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from tinyrom import TinyRom


ROOT = Path(__file__).resolve().parents[1]
ROM = str(ROOT / "examples" / "factory_rom.bin")
TOML = str(ROOT / "examples" / "definitions.toml")


def ecu() -> TinyRom:
    return TinyRom(ROM, TOML)


class ReadTests(unittest.TestCase):
    def test_primary_fuel_shape_and_values(self) -> None:
        fuel = ecu().get_map("primary_fuel")
        self.assertEqual(fuel.shape, (16, 16))
        self.assertTrue(np.isclose(fuel[0, 0], 0.625))
        self.assertTrue(np.isclose(fuel[-1, -1], 1.796875))

    def test_base_ignition_applies_offset(self) -> None:
        # factor 0.25, offset -20.0; raw 140 -> 140*0.25 - 20 == 15.0
        e = ecu()
        self.assertEqual(e.raw("base_ignition")[0, 0], 140)
        ign = e.get_map("base_ignition")
        self.assertEqual(ign.shape, (16, 16))
        self.assertTrue(np.isclose(ign[0, 0], 15.0))
        self.assertTrue(np.isclose(ign[-1, -1], 11.25))

    def test_rpm_axis_is_row_vector_u2(self) -> None:
        e = ecu()
        axis = e.get_map("rpm_axis")
        self.assertEqual(axis.shape, (1, 16))
        self.assertEqual(e.raw("rpm_axis").dtype, np.dtype("u2"))

    def test_rev_limiter_is_scalar(self) -> None:
        e = ecu()
        rev = e.get_map("rev_limiter")
        self.assertEqual(rev.shape, (1, 1))
        self.assertEqual(e.raw("rev_limiter").dtype, np.dtype("u2"))

    def test_unknown_map_raises_keyerror(self) -> None:
        e = ecu()
        with self.assertRaises(KeyError):
            e.get_map("does_not_exist")
        with self.assertRaises(KeyError):
            e.raw("does_not_exist")
        with self.assertRaises(KeyError):
            e.patch_map("does_not_exist", np.zeros((1, 1)))


class PatchTests(unittest.TestCase):
    def _round_trip(self, name: str, edited: np.ndarray) -> np.ndarray:
        with tempfile.TemporaryDirectory() as tmp:
            out = str(Path(tmp) / "patched.bin")
            e = ecu()
            e.patch_map(name, edited)
            e.save(out)
            return TinyRom(out, TOML).get_map(name)

    def test_round_trip_full_array_u1(self) -> None:
        # shift every cell by one factor step -> stays on grid, exact reload
        e = ecu()
        fuel = e.get_map("primary_fuel")
        step = 0.0078125
        edited = fuel + step
        reloaded = self._round_trip("primary_fuel", edited)
        self.assertTrue(np.allclose(reloaded, edited))

    def test_round_trip_offset_map(self) -> None:
        e = ecu()
        edited = e.get_map("base_ignition") + 0.25  # one factor step
        reloaded = self._round_trip("base_ignition", edited)
        self.assertTrue(np.allclose(reloaded, edited))

    def test_round_trip_multibyte_u2(self) -> None:
        edited = (np.arange(16) * 100.0).reshape(1, 16)
        reloaded = self._round_trip("rpm_axis", edited)
        self.assertTrue(np.allclose(reloaded, edited))

    def test_round_trip_scalar_u2(self) -> None:
        reloaded = self._round_trip("rev_limiter", np.array([[7000.0]]))
        self.assertTrue(np.isclose(reloaded[0, 0], 7000.0))

    def test_patch_quantizes_off_grid_values(self) -> None:
        # 0.01 is not a multiple of factor 0.0078125; rint -> 1 raw -> 0.0078125
        e = ecu()
        fuel = e.get_map("primary_fuel")
        fuel[0, 0] = 0.01
        reloaded = self._round_trip("primary_fuel", fuel)
        self.assertFalse(np.isclose(reloaded[0, 0], 0.01))
        self.assertTrue(np.isclose(reloaded[0, 0], 0.0078125))

    def test_patch_does_not_touch_other_maps(self) -> None:
        before = ecu().get_map("base_ignition")
        with tempfile.TemporaryDirectory() as tmp:
            out = str(Path(tmp) / "patched.bin")
            e = ecu()
            fuel = e.get_map("primary_fuel")
            fuel[:] = fuel + 0.0078125
            e.patch_map("primary_fuel", fuel)
            e.save(out)
            after = TinyRom(out, TOML).get_map("base_ignition")
        self.assertTrue(np.array_equal(before, after))

    def test_patch_mutates_in_memory_before_save(self) -> None:
        e = ecu()
        edited = e.get_map("primary_fuel") + 0.0078125
        e.patch_map("primary_fuel", edited)
        self.assertTrue(np.allclose(e.get_map("primary_fuel"), edited))

    def test_patch_rejects_wrong_shape(self) -> None:
        with self.assertRaisesRegex(
            ValueError, r"primary_fuel expects shape \(16, 16\), got \(1, 1\)"
        ):
            ecu().patch_map("primary_fuel", np.array([[1.0]]))


if __name__ == "__main__":
    unittest.main()
