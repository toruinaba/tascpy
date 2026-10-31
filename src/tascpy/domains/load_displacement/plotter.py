import warnings
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Optional, Sequence

import numpy as np
from matplotlib.axes import Axes

from tascpy.core.plot.plotter import CorePlotter, axis_label
from tascpy.core.result import PointResult

from . import draw as ld_plot

if TYPE_CHECKING:
    from .collection import LoadDisplacementCollection


@dataclass
class _Axes:
    """荷重-変位の元データと軸ラベル・単位"""

    x: np.ndarray
    y: np.ndarray
    x_label: str
    y_label: str
    x_unit: Optional[str]
    y_unit: Optional[str]


class LoadDisplacementPlotter(CorePlotter):
    """荷重-変位コレクションのプロッター

    X 軸・Y 軸の列を省略すると変位列・荷重列を使い、軸ラベルは "列名 [単位]" にします。
    降伏点は `ops.yield_point()` の結果 (PointResult) を渡します。
    """

    _collection: "LoadDisplacementCollection"

    def _ld_axes(self, x_column: Optional[str], y_column: Optional[str],
                 x_label: Optional[str], y_label: Optional[str]) -> _Axes:
        x_col = self._collection[x_column or self._collection.displacement_column]
        y_col = self._collection[y_column or self._collection.load_column]
        return _Axes(
            x=x_col.values, y=y_col.values,
            x_label=axis_label(x_col.name, x_col.unit) if x_label is None else x_label,
            y_label=axis_label(y_col.name, y_col.unit) if y_label is None else y_label,
            x_unit=x_col.unit, y_unit=y_col.unit,
        )

    def plot_load_displacement(self, x_column: Optional[str] = None, y_column: Optional[str] = None,
                               ax: Optional[Axes] = None, x_label: Optional[str] = None,
                               y_label: Optional[str] = None, **kwargs: Any) -> Axes:
        """荷重-変位曲線を描画します（列の省略時は変位列・荷重列）"""
        a = self._ld_axes(x_column, y_column, x_label, y_label)
        return ld_plot.plot_load_displacement(a.x, a.y, x_label=a.x_label, y_label=a.y_label, ax=ax, **kwargs)

    @staticmethod
    def _yield_args(point: PointResult) -> tuple:
        info = point.metadata
        return (float(point.x), float(point.y), info.get("method", "unknown"), info.get("initial_slope", 1.0),
                info.get("parameters", {}))

    def plot_yield_point(self, point: PointResult, *, x_column: Optional[str] = None,
                         y_column: Optional[str] = None, x_label: Optional[str] = None,
                         y_label: Optional[str] = None, ax: Optional[Axes] = None,
                         plot_original_data: bool = True, plot_initial_slope: bool = True,
                         plot_offset_line: bool = True, **kwargs: Any) -> Axes:
        """降伏点 (`ops.yield_point()` の結果) を、このコレクションの荷重-変位曲線と重ねて描画します

        Examples:
            >>> ax = ld.plot.plot_yield_point(ld.ops.yield_point(offset_value=0.5, range_start=0.1, range_end=0.8))
        """
        a = self._ld_axes(x_column, y_column, x_label, y_label)
        return ld_plot.plot_yield_point(
            *self._yield_args(point), x_values=a.x, y_values=a.y,
            x_label=a.x_label, y_label=a.y_label, ax=ax, plot_original_data=plot_original_data,
            plot_initial_slope=plot_initial_slope, plot_offset_line=plot_offset_line, **kwargs,
        )

    def plot_yield_analysis_details(self, point: PointResult, *, x_column: Optional[str] = None,
                                    y_column: Optional[str] = None, x_label: Optional[str] = None,
                                    y_label: Optional[str] = None, ax: Optional[Axes] = None,
                                    plot_original: bool = True, **kwargs: Any) -> Axes:
        """降伏点の図に、初期勾配の計算範囲と降伏点の数値（単位付き）を加えて描画します"""
        a = self._ld_axes(x_column, y_column, x_label, y_label)
        return ld_plot.plot_yield_analysis_details(
            *self._yield_args(point), x_values=a.x, y_values=a.y,
            x_label=a.x_label, y_label=a.y_label, ax=ax, x_unit=a.x_unit, y_unit=a.y_unit,
            plot_original_data=plot_original, **kwargs,
        )

    def compare_yield_points(self, points: Sequence[PointResult], *, x_column: Optional[str] = None,
                             y_column: Optional[str] = None, x_label: Optional[str] = None,
                             y_label: Optional[str] = None, ax: Optional[Axes] = None, **kwargs: Any) -> Axes:
        """複数の降伏点（`ops.yield_point()` の結果）を、このコレクションの荷重-変位曲線と重ねて描画します

        求まらなかった点（metadata の is_valid が False）は警告を出して描画しません。

        Examples:
            >>> points = [ld.ops.yield_point(method="offset", offset_value=0.5, range_start=0.1, range_end=0.8),
            ...           ld.ops.yield_point(method="general", range_start=0.1, range_end=0.8)]
            >>> ax = ld.plot.compare_yield_points(points)
        """
        results = []
        for point in points:
            md = point.metadata
            if not md.get("is_valid", True):
                warnings.warn(f"求まらなかった降伏点は描画しません（{md.get('method', 'unknown')}）", stacklevel=2)
                continue
            results.append({
                "yield_disp": point.x, "yield_load": point.y, "method": md.get("method"),
                "initial_slope": md.get("initial_slope"), "parameters": md.get("parameters", {}),
            })
        a = self._ld_axes(x_column, y_column, x_label, y_label)
        return ld_plot.compare_yield_points(results, x_values=a.x, y_values=a.y, x_label=a.x_label,
                                            y_label=a.y_label, ax=ax, **kwargs)

    def plot_multiple_curves(self, curves: Sequence[Dict[str, Any]], *, plot_original: bool = False,
                             original_kwargs: Optional[Dict[str, Any]] = None, x_label: Optional[str] = None,
                             y_label: Optional[str] = None, ax: Optional[Axes] = None,
                             x_column: Optional[str] = None, y_column: Optional[str] = None) -> Axes:
        """複数の曲線 {"x": 配列, "y": 配列, "kwargs": {...}} を重ねて描画します

        plot_original=True のときは、このコレクションの荷重-変位曲線も描画します（original_kwargs は core の plot に渡すため、
        plot_type="scatter" なども指定できます）。別のコレクションの曲線は、同じ ax にそのコレクションの plot で描画することもできます。
        """
        a = self._ld_axes(x_column, y_column, x_label, y_label)
        original = (a.x, a.y, original_kwargs or {}) if plot_original else None
        return ld_plot.plot_multiple_curves(list(curves), x_label=a.x_label, y_label=a.y_label, ax=ax, original=original)
