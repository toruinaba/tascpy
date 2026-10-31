from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Mapping, Optional, Self

from tascpy.core.collection import ColumnCollection
from tascpy.domains.coordinate.collection import CoordinateCollection, Coordinates

if TYPE_CHECKING:
    from .ops import StrainOps
    from .plotter import StrainPlotter

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
        >>> strain_col = StrainCollection({"CH1": [100.0], "CH2": [50.0], "CH3": [20.0]}, rosettes=ros)
        >>> strain_col.get_rosette("R1")["type"]
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
        # CoordinateCollection.from_collection と同じ処理。jedi（marimo の補完）は classmethod 内の
        # super() を解決できず戻り値の型を見失うため、super() を使わずに書く
        new = collection._as_class(cls)._with_coordinate_map(coordinates)
        new._rosettes = {name: _checked_rosette(name, info) for name, info in (rosettes or {}).items()}
        return new

    def _domain_config(self) -> Dict[str, Any]:
        return {"rosettes": self.rosettes}

    @classmethod
    def _from_config(cls, collection: ColumnCollection, config: Mapping[str, Any]) -> Self:
        return cls.from_collection(collection, **config)

    @property
    def ops(self) -> "StrainOps":
        """ひずみドメインの操作オブジェクト"""
        from .ops import StrainOps

        return StrainOps(self)

    @property
    def plot(self) -> "StrainPlotter":
        """ひずみデータのプロッター"""
        from .plotter import StrainPlotter

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


as_strain = StrainCollection.from_collection
"""`col.ops.as_domain(as_strain, ...)` でひずみドメインに変換する"""
