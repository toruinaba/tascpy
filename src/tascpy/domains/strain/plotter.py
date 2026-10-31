from typing import TYPE_CHECKING, Any, Dict, Optional

from matplotlib.axes import Axes

from tascpy.core.plot.plotter import CorePlotter

from . import draw as strain_plot

if TYPE_CHECKING:
    from .collection import StrainCollection


class StrainPlotter(CorePlotter):
    """ひずみコレクションのプロッター（ロゼットの主ひずみベクトルなど）"""

    _collection: "StrainCollection"

    def _rosette_vector_args(self, prefix: str, step_index: int) -> Dict[str, Any]:
        """calculate_rosette_strains の結果列 "{prefix}_e1" などから、指定ステップの主ひずみ・主方向と座標を取得します"""
        names = {key: f"{prefix}_{key}" for key in ("e1", "e2", "theta")}
        for name in names.values():
            if name not in self._collection:
                raise ValueError(f"計算済みカラム '{name}' が見つかりません。先に calculate_rosette_strains(prefix=\"{prefix}\") を実行してください。")
        n = len(self._collection)
        if not -n <= step_index < n:
            raise ValueError(f"Step index {step_index} is out of range.")

        x, y, _ = self._collection.get_column_coordinates(names["e1"])
        if x is None or y is None:
            raise ValueError(f"結果列 '{names['e1']}' に座標がありません（ロゼットのゲージ列に座標を設定してください）")

        values = {key: float(self._collection[name].values[step_index]) for key, name in names.items()}
        return {"x": x, "y": y, **values, "rosette_name": prefix, "step_index": step_index}

    def plot_rosette_vectors(self, prefix: str, step_index: int = 0, scale: float = 1.0,
                             ax: Optional[Axes] = None) -> Axes:
        """`calculate_rosette_strains(prefix=...)` の結果から、ロゼットの位置に主ひずみベクトルを描画します"""
        return strain_plot.plot_rosette_vectors(**self._rosette_vector_args(prefix, step_index),
                                                scale=scale, ax=ax)

    def iplot_rosette_vectors(self, prefix: str, step_index: int = 0, scale: float = 1.0,
                              fig: Optional[Any] = None) -> Any:
        """`calculate_rosette_strains(prefix=...)` の結果から、ロゼットの位置に主ひずみベクトルを Plotly で描画します"""
        return strain_plot.iplot_rosette_vectors(**self._rosette_vector_args(prefix, step_index),
                                                 scale=scale, fig=fig)
