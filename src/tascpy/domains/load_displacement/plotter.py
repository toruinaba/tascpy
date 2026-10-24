import warnings
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, TypeVar

import numpy as np
from matplotlib.axes import Axes

from tascpy.core.plot.plotter import CorePlotter, axis_label
from tascpy.core.result import AnalysisResult, PointResult, XYSeriesResult

from . import draw as ld_plot

if TYPE_CHECKING:
    from .collection import LoadDisplacementCollection

R = TypeVar("R", bound=AnalysisResult)


def _typed_result(result: Optional[AnalysisResult], name: str, cls: Type[R], missing: str) -> R:
    """解析結果が存在し、期待した型であることを確かめて返します"""
    if result is None:
        raise ValueError(missing)
    if not isinstance(result, cls):
        raise TypeError(f"解析結果 '{name}' は {cls.__name__} ではありません ({type(result).__name__})")
    return result


@dataclass
class _Axes:
    """荷重-変位の元データと軸ラベル・単位"""

    x: np.ndarray
    y: np.ndarray
    x_label: str
    y_label: str
    x_unit: Optional[str]
    y_unit: Optional[str]


@dataclass
class _Yield:
    disp: float
    load: float
    method: str
    initial_slope: float
    parameters: Dict[str, Any]


class LoadDisplacementPlotter(CorePlotter):
    """荷重-変位コレクションのプロッター

    X 軸・Y 軸の列を省略すると変位列・荷重列を使い、軸ラベルは "列名 [単位]" にします。
    曲線や降伏点は解析結果（results）から取得します。
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

    def _curve(self, name: str) -> tuple[np.ndarray, np.ndarray]:
        """解析結果 (XYSeriesResult) から曲線の (x, y) を取得します"""
        curve = _typed_result(self._collection.results.get(name), name, XYSeriesResult,
                              f"コレクションに解析結果 '{name}' がありません")
        return curve.x.values, curve.y.values

    def _yield_point(self, result_prefix: str, yield_disp: Optional[float], yield_load: Optional[float],
                     yield_method: Optional[str], initial_slope: Optional[float],
                     yield_parameters: Optional[Dict[str, Any]]) -> _Yield:
        """引数で指定された値を優先し、指定がなければ解析結果 "{result_prefix}_point" から取得します"""
        info: Dict[str, Any] = {}
        if yield_disp is None or yield_load is None:
            name = f"{result_prefix}_point"
            point = _typed_result(self._collection.results.get(name), name, PointResult,
                                  "コレクションに降伏点の解析結果が含まれていません")
            yield_disp, yield_load = point.x, point.y
            info = point.metadata or {}
        return _Yield(
            disp=float(yield_disp), load=float(yield_load),
            method=yield_method or info.get("method", "unknown"),
            initial_slope=initial_slope if initial_slope is not None else info.get("initial_slope", 1.0),
            parameters=yield_parameters if yield_parameters is not None else info.get("parameters", {}),
        )

    def plot_load_displacement(self, x_column: Optional[str] = None, y_column: Optional[str] = None,
                               ax: Optional[Axes] = None, x_label: Optional[str] = None,
                               y_label: Optional[str] = None, **kwargs: Any) -> Axes:
        """荷重-変位曲線を描画します（列の省略時は変位列・荷重列）"""
        a = self._ld_axes(x_column, y_column, x_label, y_label)
        return ld_plot.plot_load_displacement(a.x, a.y, x_label=a.x_label, y_label=a.y_label, ax=ax, **kwargs)

    def plot_skeleton_curve(self, skeleton_x: Optional[np.ndarray] = None, skeleton_y: Optional[np.ndarray] = None,
                            x_column: Optional[str] = None, y_column: Optional[str] = None,
                            x_label: Optional[str] = None, y_label: Optional[str] = None,
                            ax: Optional[Axes] = None, plot_original: bool = True,
                            original_kwargs: Optional[Dict[str, Any]] = None,
                            skeleton_kwargs: Optional[Dict[str, Any]] = None) -> Axes:
        """スケルトン曲線を描画します（省略時は解析結果 "skeleton_curve" を使う）"""
        if skeleton_x is None or skeleton_y is None:
            skeleton_x, skeleton_y = self._curve("skeleton_curve")
        a = self._ld_axes(x_column, y_column, x_label, y_label)
        return ld_plot.plot_skeleton_curve(
            skeleton_x, skeleton_y, x_values=a.x if plot_original else None, y_values=a.y if plot_original else None,
            x_label=a.x_label, y_label=a.y_label, ax=ax, original_kwargs=original_kwargs,
            skeleton_kwargs=skeleton_kwargs,
        )

    def plot_cumulative_curve(self, cumulative_x: Optional[np.ndarray] = None,
                              cumulative_y: Optional[np.ndarray] = None, x_column: Optional[str] = None,
                              y_column: Optional[str] = None, x_label: Optional[str] = None,
                              y_label: Optional[str] = None, ax: Optional[Axes] = None,
                              plot_original: bool = True, original_kwargs: Optional[Dict[str, Any]] = None,
                              cumulative_kwargs: Optional[Dict[str, Any]] = None) -> Axes:
        """累積曲線を描画します（省略時は解析結果 "cumulative_curve" を使う）"""
        if cumulative_x is None or cumulative_y is None:
            cumulative_x, cumulative_y = self._curve("cumulative_curve")
        a = self._ld_axes(x_column, y_column, x_label, y_label)
        return ld_plot.plot_cumulative_curve(
            cumulative_x, cumulative_y, x_values=a.x if plot_original else None,
            y_values=a.y if plot_original else None, x_label=a.x_label, y_label=a.y_label, ax=ax,
            original_kwargs=original_kwargs, cumulative_kwargs=cumulative_kwargs,
        )

    def plot_yield_point(self, yield_disp: Optional[float] = None, yield_load: Optional[float] = None,
                         yield_method: Optional[str] = None, initial_slope: Optional[float] = None,
                         yield_parameters: Optional[Dict[str, Any]] = None, x_column: Optional[str] = None,
                         y_column: Optional[str] = None, x_label: Optional[str] = None,
                         y_label: Optional[str] = None, ax: Optional[Axes] = None,
                         plot_original_data: bool = True, plot_initial_slope: bool = True,
                         plot_offset_line: bool = True, result_prefix: str = "yield", **kwargs: Any) -> Axes:
        """降伏点の解析結果を描画します（値の省略時は解析結果 "{result_prefix}_point" を使う）"""
        yp = self._yield_point(result_prefix, yield_disp, yield_load, yield_method, initial_slope, yield_parameters)
        a = self._ld_axes(x_column, y_column, x_label, y_label)
        return ld_plot.plot_yield_point(
            yp.disp, yp.load, yp.method, yp.initial_slope, yp.parameters, x_values=a.x, y_values=a.y,
            x_label=a.x_label, y_label=a.y_label, ax=ax, plot_original_data=plot_original_data,
            plot_initial_slope=plot_initial_slope, plot_offset_line=plot_offset_line, **kwargs,
        )

    def plot_yield_analysis_details(self, yield_disp: Optional[float] = None, yield_load: Optional[float] = None,
                                    yield_method: Optional[str] = None, initial_slope: Optional[float] = None,
                                    yield_parameters: Optional[Dict[str, Any]] = None,
                                    x_column: Optional[str] = None, y_column: Optional[str] = None,
                                    x_label: Optional[str] = None, y_label: Optional[str] = None,
                                    ax: Optional[Axes] = None, plot_original: bool = True,
                                    result_prefix: str = "yield", **kwargs: Any) -> Axes:
        """降伏点の図に、初期勾配の計算範囲と降伏点の数値（単位付き）を加えて描画します"""
        yp = self._yield_point(result_prefix, yield_disp, yield_load, yield_method, initial_slope, yield_parameters)
        a = self._ld_axes(x_column, y_column, x_label, y_label)
        return ld_plot.plot_yield_analysis_details(
            yp.disp, yp.load, yp.method, yp.initial_slope, yp.parameters, x_values=a.x, y_values=a.y,
            x_label=a.x_label, y_label=a.y_label, ax=ax, x_unit=a.x_unit, y_unit=a.y_unit,
            plot_original_data=plot_original, **kwargs,
        )

    def compare_yield_methods(self, methods: Optional[List[Dict[str, Any]]] = None,
                              x_column: Optional[str] = None, y_column: Optional[str] = None,
                              x_label: Optional[str] = None, y_label: Optional[str] = None,
                              ax: Optional[Axes] = None, **kwargs: Any) -> Axes:
        """複数の手法で降伏点を求めて重ねて描画します（求められなかった手法は警告を出して飛ばす）

        Args:
            methods: find_yield_point に渡す引数のリスト（省略時は offset と general）
        """
        defaults: List[Dict[str, Any]] = [{"method": "offset"}, {"method": "general"}]
        results = []
        for params in defaults if methods is None else methods:
            params = {k: v for k, v in params.items() if k != "result_prefix"}
            try:
                found = self._collection.ops.find_yield_point(**params).end().results.get("yield_point")
            except ValueError as e:
                warnings.warn(f"降伏点を求められませんでした {params}: {e}", stacklevel=2)
                continue
            point = _typed_result(found, "yield_point", PointResult, "find_yield_point が結果を返しませんでした")
            md = point.metadata
            results.append({
                "yield_disp": point.x, "yield_load": point.y, "method": md.get("method"),
                "initial_slope": md.get("initial_slope"), "parameters": md.get("parameters", {}),
            })
        a = self._ld_axes(x_column, y_column, x_label, y_label)
        return ld_plot.compare_yield_methods(results, x_values=a.x, y_values=a.y, x_label=a.x_label,
                                             y_label=a.y_label, ax=ax, **kwargs)

    def plot_multiple_curves(self, curves: List[Dict[str, Any]], x_label: Optional[str] = None,
                             y_label: Optional[str] = None, ax: Optional[Axes] = None,
                             x_column: Optional[str] = None, y_column: Optional[str] = None) -> Axes:
        """複数の曲線を重ねて描画します

        curves の各要素は {"type": "original" | "skeleton" | "cumulative", "kwargs": {...}}、
        または {"x": 配列, "y": 配列, "kwargs": {...}} です。解析結果がない曲線は警告を出して飛ばします。
        """
        a = self._ld_axes(x_column, y_column, x_label, y_label)
        curves_data = []
        for curve in curves:
            if "x" in curve and "y" in curve:
                curves_data.append(curve)
                continue
            kind = curve.get("type")
            item: Dict[str, Any] = {"type": kind, "kwargs": curve.get("kwargs", {})}
            if kind == "original":
                item["x"], item["y"] = a.x, a.y
            elif kind in ("skeleton", "cumulative"):
                try:
                    item["x"], item["y"] = self._curve(f"{kind}_curve")
                except ValueError as e:
                    warnings.warn(str(e), stacklevel=2)
                    continue
            else:
                warnings.warn(f"未知の曲線の種類です: {kind}", stacklevel=2)
                continue
            curves_data.append(item)
        return ld_plot.plot_multiple_curves(curves_data, x_label=a.x_label, y_label=a.y_label, ax=ax)
