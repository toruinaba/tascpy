from __future__ import annotations

from typing import Any, Dict, Iterator, Mapping, Optional

from .column import ColumnMeta


class Row(Mapping[str, Any]):
    """ColumnCollection の1行（値は素のスカラー、欠損は None）

    Examples:
        >>> row = col[1]
        >>> row["荷重"], row.unit("荷重"), row.step
        (40.0, 'kN', 2)
    """

    __slots__ = ("_values", "_meta")

    def __init__(self, values: Dict[str, Any], meta: Mapping[str, ColumnMeta]) -> None:
        self._values = values
        self._meta = meta

    def __getitem__(self, key: str) -> Any:
        if key not in self._values:
            raise KeyError(f"列 '{key}' が存在しません")
        return self._values[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)

    @property
    def step(self) -> Any:
        return self._values["step"]

    def unit(self, key: str) -> Optional[str]:
        return self._meta[key].unit

    @property
    def units(self) -> Dict[str, Optional[str]]:
        return {name: meta.unit for name, meta in self._meta.items()}

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._values)

    def __repr__(self) -> str:
        items = [f"step={self.step}"]
        for name in list(self._meta)[:4]:
            unit = self._meta[name].unit
            items.append(f"{name}={self._values[name]}{' ' + unit if unit else ''}")
        if len(self._meta) > 4:
            items.append("...")
        return f"<Row {', '.join(items)}>"
