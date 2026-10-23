from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, Optional, Sequence, Tuple

import numpy as np

from ..core.collection import ColumnCollection
from ..core.column import Column

if TYPE_CHECKING:
    from ..analytics.ops import LoadDisplacementOps
    from ..visualization.plotters.load_displacement.plotter import LoadDisplacementPlotter

LOAD_KEYWORDS = ("load", "force", "荷重", "力")
DISPLACEMENT_KEYWORDS = ("disp", "displacement", "変位", "変形")


def _guess_column(collection: ColumnCollection, keywords: Sequence[str]) -> Optional[str]:
    for keyword in keywords:
        for name in collection.columns:
            if keyword.lower() in name.lower():
                return name
    return None


class LoadDisplacementCollection(ColumnCollection):
    """荷重と変位の列を指定したコレクション

    Examples:
        >>> col = LoadDisplacementCollection(
        ...     {"P": [0.0, 10.0], "d": [0.0, 1.0]}, units={"P": "kN", "d": "mm"},
        ...     load_column="P", displacement_column="d",
        ... )
        >>> col.load.unit
        'kN'
    """

    domain = "load_displacement"

    def __init__(self, columns: Optional[Mapping[str, Any]] = None, *, load_column: str,
                 displacement_column: str, **kwargs: Any) -> None:
        super().__init__(columns, **kwargs)
        self._load_column = load_column
        self._displacement_column = displacement_column
        self._validate()

    @classmethod
    def from_collection(cls, collection: ColumnCollection, load_column: Optional[str] = None,
                        displacement_column: Optional[str] = None) -> "LoadDisplacementCollection":
        """既存のコレクションから作成する（列名省略時は列名のキーワードから推測）

        Raises:
            ValueError: 列を推測できない、または列が数値でない場合
        """
        load_column = load_column or _guess_column(collection, LOAD_KEYWORDS)
        displacement_column = displacement_column or _guess_column(collection, DISPLACEMENT_KEYWORDS)
        if not load_column or not displacement_column:
            raise ValueError("荷重列・変位列を指定してください（列名から推測できませんでした）")
        new = collection._as_class(cls)
        new._load_column = load_column
        new._displacement_column = displacement_column
        new._validate()
        return new

    def _validate(self) -> None:
        for role, name in (("load_column", self._load_column), ("displacement_column", self._displacement_column)):
            if name not in self:
                raise ValueError(f"{role} に指定した列 '{name}' が存在しません")
            if not self[name].is_numeric:
                raise ValueError(f"{role} に指定した列 '{name}' は数値列ではありません")

    def _apply_rename(self, mapping: Mapping[str, str]) -> None:
        self._load_column = mapping.get(self._load_column, self._load_column)
        self._displacement_column = mapping.get(self._displacement_column, self._displacement_column)

    @property
    def ops(self) -> "LoadDisplacementOps":
        """荷重-変位ドメインの操作オブジェクト"""
        from ..analytics.ops import LoadDisplacementOps

        return LoadDisplacementOps(self)

    @property
    def plot(self) -> "LoadDisplacementPlotter":
        """荷重-変位データのプロッター"""
        from ..visualization.plotters.load_displacement.plotter import LoadDisplacementPlotter

        return LoadDisplacementPlotter(self)

    @property
    def load_column(self) -> str:
        return self._load_column

    @property
    def displacement_column(self) -> str:
        return self._displacement_column

    @property
    def load(self) -> Column:
        return self[self._load_column]

    @property
    def displacement(self) -> Column:
        return self[self._displacement_column]

    @property
    def load_data(self) -> np.ndarray:
        """荷重の配列（欠損は NaN）"""
        return self.load.values

    @property
    def displacement_data(self) -> np.ndarray:
        """変位の配列（欠損は NaN）"""
        return self.displacement.values

    @property
    def valid_data_mask(self) -> np.ndarray:
        """荷重・変位がともに欠損でない行のマスク"""
        return ~(np.isnan(self.load_data) | np.isnan(self.displacement_data))

    @property
    def valid_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """有効な行の (変位, 荷重)"""
        mask = self.valid_data_mask
        return self.displacement_data[mask], self.load_data[mask]

    def __repr__(self) -> str:
        return (super().__repr__()[:-1]
                + f" load={self._load_column!r} displacement={self._displacement_column!r}>")
