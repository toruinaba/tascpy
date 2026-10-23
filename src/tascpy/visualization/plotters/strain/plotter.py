from typing import TYPE_CHECKING, Any, Dict, Optional

from matplotlib.axes import Axes

from tascpy.visualization.functional.strain import plot as strain_plot
from tascpy.visualization.plotters.coordinate.plotter import CoordinatePlotter

if TYPE_CHECKING:
    from tascpy.domains.strain import StrainCollection


class StrainPlotter(CoordinatePlotter):
    """ひずみコレクションのプロッター（ロゼットの主ひずみベクトルなど）"""

    _collection: "StrainCollection"

    def _rosette_vector_args(self, rosette_name: str, step_index: int) -> Dict[str, Any]:
        """calculate_rosette_strains の結果列から、指定ステップの主ひずみ・主方向とロゼットの座標を取得します"""
        names = {key: f"{rosette_name}_{key}" for key in ("e1", "e2", "theta")}
        for name in names.values():
            if name not in self._collection:
                raise ValueError(f"計算済みカラム '{name}' が見つかりません。先に calculate_rosette_strains を実行してください。")
        n = len(self._collection)
        if not -n <= step_index < n:
            raise ValueError(f"Step index {step_index} is out of range.")

        x, y, _ = self._collection.get_column_coordinates(names["e1"])
        rosette = self._collection.get_rosette(rosette_name)
        if (x is None or y is None) and rosette and rosette.get("columns"):
            x, y, _ = self._collection.get_column_coordinates(rosette["columns"][0])
        if x is None or y is None:
            raise ValueError(f"ロゼット '{rosette_name}' の座標情報が取得できませんでした。")

        values = {key: float(self._collection[name].values[step_index]) for key, name in names.items()}
        return {"x": x, "y": y, **values, "rosette_name": rosette_name, "step_index": step_index}

    def plot_rosette_vectors(self, rosette_name: str, step_index: int = 0, scale: float = 1.0,
                             ax: Optional[Axes] = None) -> Axes:
        """ロゼットの位置に主ひずみベクトルを描画します"""
        return strain_plot.plot_rosette_vectors(**self._rosette_vector_args(rosette_name, step_index),
                                                scale=scale, ax=ax)

    def iplot_rosette_vectors(self, rosette_name: str, step_index: int = 0, scale: float = 1.0,
                              fig: Optional[Any] = None) -> Any:
        """ロゼットの位置に主ひずみベクトルを Plotly で描画します"""
        return strain_plot.iplot_rosette_vectors(**self._rosette_vector_args(rosette_name, step_index),
                                                 scale=scale, fig=fig)
