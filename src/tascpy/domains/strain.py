from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Mapping, Optional, Self

from ..core.collection import ColumnCollection
from .coordinate import Coordinates, CoordinateCollection

if TYPE_CHECKING:
    from ..analytics.ops import StrainOps
    from ..visualization.plotters.strain.plotter import StrainPlotter

Rosette = Dict[str, Any]
"""ロゼット定義 {"columns": [e1, e2, e3], "type": "rectangular" | "delta", "orientation": 度}"""


def _checked_rosette(name: str, info: Mapping[str, Any]) -> Rosette:
    if "columns" not in info:
        raise ValueError(f"ロゼット情報には 'columns' リストが必要です: {name}")
    return dict(info)


class StrainCollection(CoordinateCollection):
    """ひずみゲージの座標とロゼット定義を持つコレクション

    Examples:
        >>> ros = {"R1": {"columns": ["CH1", "CH2", "CH3"], "type": "rectangular", "orientation": 0.0}}
        >>> col = StrainCollection({"CH1": [100.0], "CH2": [50.0], "CH3": [20.0]}, rosettes=ros)
        >>> col.get_rosette("R1")["type"]
        'rectangular'
    """

    domain = "strain"

    def __init__(self, columns: Optional[Mapping[str, Any]] = None, *,
                 rosettes: Optional[Mapping[str, Rosette]] = None,
                 coordinates: Optional[Coordinates] = None, **kwargs: Any) -> None:
        self._rosettes: Dict[str, Rosette] = {}
        super().__init__(columns, coordinates=coordinates, **kwargs)
        self._rosettes = {name: _checked_rosette(name, info) for name, info in (rosettes or {}).items()}

    @classmethod
    def from_collection(cls, collection: ColumnCollection, *, rosettes: Optional[Mapping[str, Rosette]] = None,
                        coordinates: Optional[Coordinates] = None) -> Self:
        new = super().from_collection(collection, coordinates=coordinates)
        new._rosettes = {name: _checked_rosette(name, info) for name, info in (rosettes or {}).items()}
        return new

    @property
    def ops(self) -> "StrainOps":
        """ひずみドメインの操作オブジェクト"""
        from ..analytics.ops import StrainOps

        return StrainOps(self)

    @property
    def plot(self) -> "StrainPlotter":
        """ひずみデータのプロッター"""
        from ..visualization.plotters.strain.plotter import StrainPlotter

        return StrainPlotter(self)

    @property
    def rosettes(self) -> Dict[str, Rosette]:
        return dict(self._rosettes)

    def get_rosette(self, name: str) -> Optional[Rosette]:
        return self._rosettes.get(name)

    def with_rosette(self, name: str, info: Mapping[str, Any]) -> Self:
        """ロゼット定義を追加・上書きした新しいコレクション"""
        new = self._replace()
        new._rosettes = {**self._rosettes, name: _checked_rosette(name, info)}
        return new
