from __future__ import annotations

import tomllib

import numpy as np


def _addr(value: str | int) -> int:
    return int(value, 16) if isinstance(value, str) else int(value)


class TinyRom:
    def __init__(self, bin_path: str, toml_path: str):
        with open(bin_path, "rb") as f:
            self.rom = bytearray(f.read())
        with open(toml_path, "rb") as f:
            self.definition = tomllib.load(f)
        self.tables = self.definition.get("tables", {})

    def raw(self, name: str) -> np.ndarray:
        table = self.tables[name]
        shape = tuple(table["shape"])
        dtype = np.dtype(table.get("datatype", "u1"))
        count = shape[0] * shape[1]
        return np.frombuffer(self.rom, dtype=dtype, count=count, offset=_addr(table["address"])).reshape(shape)

    def get_map(self, name: str) -> np.ndarray:
        table = self.tables[name]
        return (self.raw(name) * table.get("factor", 1.0)) + table.get("offset", 0.0)

    def patch_map(self, name: str, matrix: np.ndarray) -> None:
        table = self.tables[name]
        target = self.raw(name)
        values = np.asarray(matrix)
        if values.shape != target.shape:
            raise ValueError(f"{name} expects shape {target.shape}, got {values.shape}")
        raw = np.rint((values - table.get("offset", 0.0)) / table.get("factor", 1.0))
        target[:] = raw.astype(target.dtype)

    def save(self, out_path: str) -> None:
        with open(out_path, "wb") as f:
            f.write(self.rom)
