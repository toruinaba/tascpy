"""列（1次元データ）とその付随情報"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from numbers import Number
from typing import Any, Iterator, Mapping, Optional

import numpy as np
import polars as pl


class _Keep:
    def __repr__(self) -> str:
        return "KEEP"


KEEP: Any = _Keep()
"""`with_column` / `with_meta` で「既存の値を引き継ぐ」ことを表す既定値"""


@dataclass(frozen=True)
class ColumnMeta:
    """列に付随する情報

    Attributes:
        unit: 単位。None は不明、"" は単位なし（無次元）を明示
        ch: 計測チャンネル名
        attrs: その他の属性（座標など）
    """

    unit: Optional[str] = None
    ch: Optional[str] = None
    attrs: Mapping[str, Any] = field(default_factory=dict)

    def updated(self, unit: Any = KEEP, ch: Any = KEEP, attrs: Any = KEEP) -> "ColumnMeta":
        changes = {k: v for k, v in {"unit": unit, "ch": ch, "attrs": attrs}.items() if v is not KEEP}
        if "attrs" in changes:
            changes["attrs"] = dict(changes["attrs"] or {})
        return replace(self, **changes)


def _is_number(v: Any) -> bool:
    return isinstance(v, Number) and not isinstance(v, (bool, np.bool_))


def _is_missing(v: Any) -> bool:
    return v is None or (isinstance(v, (float, np.floating)) and np.isnan(v))


def to_series(name: str, values: Any) -> pl.Series:
    """値の並びをデータ列用の Series に正規化する（数値は Float64、欠損は null）"""
    if isinstance(values, Column):
        values = values.series
    if isinstance(values, pl.Series):
        series = values.alias(name)
    elif isinstance(values, np.ndarray) and values.dtype.kind in "iuf":
        series = pl.Series(name, values.astype(float), nan_to_null=True)
    elif isinstance(values, np.ndarray) and values.dtype.kind == "b":
        series = pl.Series(name, values)
    else:
        series = _series_from_items(name, list(values))

    if series.dtype == pl.Null or series.dtype.is_numeric():
        series = series.cast(pl.Float64).fill_nan(None)
    return series


def _series_from_items(name: str, items: list) -> pl.Series:
    items = [None if _is_missing(v) else v for v in items]
    present = [v for v in items if v is not None]
    if all(_is_number(v) for v in present):
        return pl.Series(name, [None if v is None else float(v) for v in items], dtype=pl.Float64)
    if all(isinstance(v, (bool, np.bool_)) for v in present):
        return pl.Series(name, [None if v is None else bool(v) for v in items], dtype=pl.Boolean)
    if all(isinstance(v, str) for v in present):
        return pl.Series(name, items, dtype=pl.String)
    try:
        return pl.Series(name, items, strict=True)
    except (TypeError, ValueError, pl.exceptions.PolarsError):
        return pl.Series(name, [None if v is None else str(v) for v in items], dtype=pl.String)


class Column:
    """データ列の読み取り専用ビュー

    Examples:
        >>> col = Column("load", [1.0, None, 3.0], unit="kN")
        >>> col.values
        array([ 1., nan,  3.])
        >>> col.max(), col.unit
        (3.0, 'kN')
    """

    __slots__ = ("_series", "_meta")

    def __init__(
        self,
        name: str,
        values: Any = (),
        *,
        unit: Optional[str] = None,
        ch: Optional[str] = None,
        attrs: Optional[Mapping[str, Any]] = None,
    ) -> None:
        self._series = to_series(name, values)
        self._meta = ColumnMeta(unit=unit, ch=ch, attrs=dict(attrs or {}))

    @classmethod
    def _wrap(cls, series: pl.Series, meta: ColumnMeta) -> "Column":
        column = cls.__new__(cls)
        column._series = series
        column._meta = meta
        return column

    # ── 属性 ──────────────────────────────────

    @property
    def name(self) -> str:
        return self._series.name

    @property
    def series(self) -> pl.Series:
        return self._series

    @property
    def meta(self) -> ColumnMeta:
        return self._meta

    @property
    def unit(self) -> Optional[str]:
        return self._meta.unit

    @property
    def ch(self) -> Optional[str]:
        return self._meta.ch

    @property
    def attrs(self) -> Mapping[str, Any]:
        return self._meta.attrs

    @property
    def dtype(self) -> pl.DataType:
        return self._series.dtype

    @property
    def is_numeric(self) -> bool:
        return self._series.dtype.is_numeric()

    @property
    def values(self) -> np.ndarray:
        """値の配列（数値列は float64 で欠損は NaN、それ以外は object 配列で欠損は None）"""
        return self._series.to_numpy()

    def to_list(self) -> list:
        """値のリスト（欠損は None）"""
        return self._series.to_list()

    def __len__(self) -> int:
        return len(self._series)

    def __getitem__(self, index: int) -> Any:
        return self._series[index]

    def __iter__(self) -> Iterator[Any]:
        return iter(self._series.to_list())

    def __repr__(self) -> str:
        unit = f" unit={self.unit!r}" if self.unit is not None else ""
        ch = f" ch={self.ch!r}" if self.ch else ""
        vals = self.to_list()
        preview = vals if len(vals) <= 6 else [*vals[:2], "...", *vals[-2:]]
        return f"<Column {self.name!r}{unit}{ch} dtype={self.dtype} len={len(self)} values={preview}>"

    # ── 集約（数値列以外は None） ───────────────────

    def _numeric_stat(self, func_name: str, *args: Any) -> Optional[float]:
        if not self.is_numeric:
            return None
        value = getattr(self._series, func_name)(*args)
        return None if value is None else float(value)

    def max(self) -> Any:
        return self._series.max() if self.is_numeric or self.dtype == pl.String else None

    def min(self) -> Any:
        return self._series.min() if self.is_numeric or self.dtype == pl.String else None

    def mean(self) -> Optional[float]:
        return self._numeric_stat("mean")

    def median(self) -> Optional[float]:
        return self._numeric_stat("median")

    def std(self) -> Optional[float]:
        return self._numeric_stat("std")

    def sum(self) -> Optional[float]:
        return self._numeric_stat("sum")

    def quantile(self, q: float) -> Optional[float]:
        if not 0 <= q <= 1:
            raise ValueError("q は 0 から 1 の間で指定してください")
        return self._numeric_stat("quantile", q)

    def ptp(self) -> Optional[float]:
        hi, lo = self._numeric_stat("max"), self._numeric_stat("min")
        return None if hi is None or lo is None else hi - lo

    def abs_max(self) -> Optional[float]:
        if not self.is_numeric:
            return None
        value = self._series.abs().max()
        return None if value is None else float(value)

    # ── 欠損 ──────────────────────────────────

    def null_count(self) -> int:
        return self._series.null_count()

    @property
    def n_valid(self) -> int:
        return len(self) - self.null_count()

    def is_valid(self) -> np.ndarray:
        return self._series.is_not_null().to_numpy()

    @property
    def first_valid_index(self) -> Optional[int]:
        valid = self.is_valid()
        return int(np.argmax(valid)) if valid.any() else None

    @property
    def first_invalid_index(self) -> Optional[int]:
        valid = self.is_valid()
        return None if valid.all() else int(np.argmin(valid))

    def nearest_index(self, value: float) -> Optional[int]:
        """値が value に最も近い要素のインデックス（数値列以外・全欠損なら None）"""
        if not self.is_numeric or self.n_valid == 0:
            return None
        return int(np.nanargmin(np.abs(self.values - value)))
