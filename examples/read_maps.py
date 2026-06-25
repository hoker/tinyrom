from __future__ import annotations

from pathlib import Path

from tinyrom import TinyRom


HERE = Path(__file__).resolve().parent


def describe_map(ecu: TinyRom, name: str) -> None:
    values = ecu.get_map(name)
    print(f"{name}")
    print(f"  shape: {values.shape}")
    print(f"  min:   {values.min():.6g}")
    print(f"  max:   {values.max():.6g}")
    print(f"  mean:  {values.mean():.6g}")
    print(f"  first: {values.flat[0]:.6g}")
    print()


def main() -> None:
    ecu = TinyRom(str(HERE / "factory_rom.bin"), str(HERE / "definitions.toml"))

    describe_map(ecu, "primary_fuel")
    describe_map(ecu, "base_ignition")
    describe_map(ecu, "rpm_axis")
    describe_map(ecu, "rev_limiter")


if __name__ == "__main__":
    main()
