"""荷重-変位データの描画関数

配列を受け取って描画し、Axes を返します。図の表示（plt.show）は呼び出し側で行います。
"""

import warnings
from typing import Any, Dict, List, Optional

import numpy as np
from matplotlib.axes import Axes

from tascpy.core.plot.draw import new_axes, plot as core_plot

DEFAULT_ORIGINAL_KWARGS = {"alpha": 0.5, "label": "Original Data", "color": "gray"}


def _with_unit(value: float, unit: Optional[str]) -> str:
    return f"{value:.4f} {unit}" if unit else f"{value:.4f}"


def _valid_loads(x_values: Optional[np.ndarray], y_values: Optional[np.ndarray]) -> Optional[np.ndarray]:
    """荷重・変位がともに有効な行のマスク（compute_stiffness と同じ行を使うため）"""
    if x_values is None or y_values is None:
        return None
    valid = ~(np.isnan(np.asarray(x_values, dtype=float)) | np.isnan(np.asarray(y_values, dtype=float)))
    return valid if valid.any() else None


def _peak_load(x_values: Optional[np.ndarray], y_values: Optional[np.ndarray]) -> Optional[float]:
    """荷重・変位がともに有効な行のうち、絶対値が最大の荷重（なければ None）"""
    valid = _valid_loads(x_values, y_values)
    if valid is None:
        return None
    loads = np.asarray(y_values, dtype=float)[valid]
    return float(loads[np.argmax(np.abs(loads))])


def _peak_sign(x_values: Optional[np.ndarray], y_values: Optional[np.ndarray], fallback: float) -> float:
    """最大荷重の符号（データがなければ fallback の符号、0 なら正）"""
    peak = _peak_load(x_values, y_values)
    return -1.0 if (fallback if peak is None else peak) < 0 else 1.0


def _plot_original(ax: Axes, x_values: Optional[np.ndarray], y_values: Optional[np.ndarray],
                   x_label: str, y_label: str, kwargs: Dict[str, Any]) -> None:
    if x_values is not None and y_values is not None:
        core_plot(x_values, y_values, ax=ax, **{"x_label": x_label, "y_label": y_label, "title": "", **kwargs})
    else:
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)


def plot_load_displacement(
    x_values: np.ndarray,
    y_values: np.ndarray,
    x_label: str = "Displacement",
    y_label: str = "Load",
    title: Optional[str] = None,
    ax: Optional[Axes] = None,
    **kwargs: Any
) -> Axes:
    """荷重-変位曲線を描画します

    Args:
        x_values: 変位データ配列
        y_values: 荷重データ配列
        x_label: X 軸ラベル
        y_label: Y 軸ラベル
        title: タイトル（None の場合は "Load-Displacement Curve"）
        ax: 描画先の Axes（None の場合は新しい図を作成）
        **kwargs: matplotlib の plot に渡す追加引数

    Returns:
        Axes: 描画した Axes

    Examples:
        >>> import numpy as np
        >>> from tascpy.domains.load_displacement.draw import plot_load_displacement
        >>> ax = plot_load_displacement(np.array([0, 1, 2]), np.array([0, 5, 8]), x_label="Disp [mm]", y_label="Load [kN]")
    """
    return core_plot(x_values, y_values, x_label=x_label, y_label=y_label,
                     title="Load-Displacement Curve" if title is None else title, ax=ax, **kwargs)


def _plot_curve(curve_x: np.ndarray, curve_y: np.ndarray, x_values: Optional[np.ndarray],
                y_values: Optional[np.ndarray], x_label: str, y_label: str, ax: Optional[Axes],
                original_kwargs: Optional[Dict[str, Any]], curve_kwargs: Dict[str, Any], title: str) -> Axes:
    ax = new_axes(ax)
    _plot_original(ax, x_values, y_values, x_label, y_label, original_kwargs or DEFAULT_ORIGINAL_KWARGS)
    ax.plot(curve_x, curve_y, **curve_kwargs)
    ax.set_title(title)
    ax.grid(True, linestyle="--", alpha=0.7)
    ax.legend()
    return ax


def plot_skeleton_curve(
    skeleton_x: np.ndarray,
    skeleton_y: np.ndarray,
    x_values: Optional[np.ndarray] = None,
    y_values: Optional[np.ndarray] = None,
    x_label: str = "Displacement",
    y_label: str = "Load",
    ax: Optional[Axes] = None,
    original_kwargs: Optional[Dict[str, Any]] = None,
    skeleton_kwargs: Optional[Dict[str, Any]] = None,
) -> Axes:
    """スケルトン曲線を、元の荷重-変位データ（任意）と重ねて描画します

    Args:
        skeleton_x: スケルトン曲線の変位配列
        skeleton_y: スケルトン曲線の荷重配列
        x_values: 元データの変位配列（None の場合は描画しない）
        y_values: 元データの荷重配列（None の場合は描画しない）
        x_label: X 軸ラベル
        y_label: Y 軸ラベル
        ax: 描画先の Axes（None の場合は新しい図を作成）
        original_kwargs: 元データの描画に渡す引数
        skeleton_kwargs: スケルトン曲線の描画に渡す引数

    Examples:
        >>> import numpy as np
        >>> from tascpy.domains.load_displacement.draw import plot_skeleton_curve
        >>> ax = plot_skeleton_curve(np.array([0, 2, 4]), np.array([0, 10, 12]))
    """
    return _plot_curve(skeleton_x, skeleton_y, x_values, y_values, x_label, y_label, ax, original_kwargs,
                       skeleton_kwargs or {"label": "Skeleton Curve", "color": "red", "linewidth": 2},
                       "Skeleton Curve Analysis")


def plot_cumulative_curve(
    cumulative_x: np.ndarray,
    cumulative_y: np.ndarray,
    x_values: Optional[np.ndarray] = None,
    y_values: Optional[np.ndarray] = None,
    x_label: str = "Displacement",
    y_label: str = "Load",
    ax: Optional[Axes] = None,
    original_kwargs: Optional[Dict[str, Any]] = None,
    cumulative_kwargs: Optional[Dict[str, Any]] = None,
) -> Axes:
    """累積曲線を、元の荷重-変位データ（任意）と重ねて描画します

    引数は plot_skeleton_curve と同じです（cumulative_kwargs は累積曲線の描画に渡す引数）。

    Examples:
        >>> import numpy as np
        >>> from tascpy.domains.load_displacement.draw import plot_cumulative_curve
        >>> ax = plot_cumulative_curve(np.array([0, 1, 2]), np.array([0, 5, 10]))
    """
    return _plot_curve(cumulative_x, cumulative_y, x_values, y_values, x_label, y_label, ax, original_kwargs,
                       cumulative_kwargs or {"label": "Cumulative Curve", "color": "blue", "linewidth": 2},
                       "Cumulative Curve Analysis")


def plot_yield_point(
    yield_disp: float,
    yield_load: float,
    yield_method: str = "unknown",
    initial_slope: float = 1.0,
    yield_parameters: Optional[Dict[str, Any]] = None,
    x_values: Optional[np.ndarray] = None,
    y_values: Optional[np.ndarray] = None,
    x_label: str = "Displacement",
    y_label: str = "Load",
    ax: Optional[Axes] = None,
    plot_original_data: bool = True,
    plot_initial_slope: bool = True,
    plot_offset_line: bool = True,
    **kwargs: Any
) -> Axes:
    """降伏点と、初期勾配線・オフセット線（オフセット法）・接線（一般降伏法）を描画します

    オフセット線は最大荷重（絶対値が最大の荷重）の符号の向きにずらします（圧縮側にも対応）。

    Args:
        yield_disp: 降伏点の変位
        yield_load: 降伏点の荷重
        yield_method: 降伏点の求め方 ("offset", "general" など)
        initial_slope: 初期勾配
        yield_parameters: 解析のパラメータ（offset_value / factor など）
        x_values: 元の変位データ配列（None なら描画しない）
        y_values: 元の荷重データ配列（None なら描画しない）
        x_label: X 軸ラベル
        y_label: Y 軸ラベル
        ax: 描画先の Axes（None の場合は新しい図を作成）
        plot_original_data: 元の荷重-変位データも描画するかどうか
        plot_initial_slope: 初期勾配線を描画するかどうか
        plot_offset_line: オフセット線を描画するかどうか（オフセット法の場合）
        **kwargs: 元データの描画に渡す追加引数

    Examples:
        >>> import numpy as np
        >>> from tascpy.domains.load_displacement.draw import plot_yield_point
        >>> disp = np.array([0, 0.5, 1.0, 1.5, 2.0])
        >>> load = np.array([0, 2.5, 5.0, 6.5, 7.0])
        >>> ax = plot_yield_point(1.5, 6.5, "offset", 5.0, {"offset_value": 0.2}, x_values=disp, y_values=load)
    """
    params = yield_parameters or {}
    ax = new_axes(ax)
    _plot_original(ax, x_values if plot_original_data else None, y_values if plot_original_data else None,
                   x_label, y_label, kwargs)

    ax.scatter([yield_disp], [yield_load], color="red", s=80, marker="o",
               label=f"Yield Point ({yield_method})", zorder=5)
    if plot_initial_slope:
        ax.axline(xy1=(0, 0), slope=initial_slope, color="orange", linestyle="--", label="Initial Slope")
    if yield_method == "offset" and plot_offset_line and "offset_value" in params:
        offset = params["offset_value"] * _peak_sign(x_values, y_values, yield_load)
        ax.axline(xy1=(offset, 0), slope=initial_slope, color="blue", linestyle="--", label="Offset Line")
    if yield_method == "general" and "factor" in params:
        factor = params["factor"]
        half = abs(yield_disp) * 0.5
        xs = np.array([yield_disp - half, yield_disp + half])
        ax.plot(xs, initial_slope * factor * (xs - yield_disp) + yield_load, color="m", linestyle="--",
                label=f"Tangent ({factor:.2f}×Initial)", zorder=4)

    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.7)
    return ax


def plot_yield_analysis_details(
    yield_disp: float,
    yield_load: float,
    yield_method: str = "unknown",
    initial_slope: float = 1.0,
    yield_parameters: Optional[Dict[str, Any]] = None,
    x_values: Optional[np.ndarray] = None,
    y_values: Optional[np.ndarray] = None,
    x_label: str = "Displacement",
    y_label: str = "Load",
    ax: Optional[Axes] = None,
    x_unit: Optional[str] = None,
    y_unit: Optional[str] = None,
    **kwargs: Any
) -> Axes:
    """降伏点の図に、初期勾配の計算範囲と降伏点の数値を加えて描画します

    初期勾配の計算範囲は、剛性の計算と同じく最大荷重（絶対値が最大の荷重）の range_start〜range_end です。
    x_unit / y_unit 以外の引数は plot_yield_point と同じです。

    Args:
        x_unit: 情報欄に表示する変位の単位
        y_unit: 情報欄に表示する荷重の単位

    Examples:
        >>> import numpy as np
        >>> from tascpy.domains.load_displacement.draw import plot_yield_analysis_details
        >>> disp = np.array([0, 0.5, 1.0, 1.5, 2.0])
        >>> load = np.array([0, 2.5, 5.0, 6.5, 7.0])
        >>> ax = plot_yield_analysis_details(1.5, 6.5, initial_slope=5.0,
        ...                                  yield_parameters={"range_start": 0.1, "range_end": 0.4},
        ...                                  x_values=disp, y_values=load, x_unit="mm", y_unit="kN")
    """
    params = yield_parameters or {}
    ax = plot_yield_point(yield_disp, yield_load, yield_method, initial_slope, params, x_values, y_values,
                          x_label, y_label, ax, **kwargs)

    valid = _valid_loads(x_values, y_values)
    peak = _peak_load(x_values, y_values)
    if valid is not None and peak is not None and "range_start" in params and "range_end" in params:
        disps, loads = np.asarray(x_values, dtype=float), np.asarray(y_values, dtype=float)
        lower, upper = sorted((peak * params["range_start"], peak * params["range_end"]))
        in_range = valid & (loads >= lower) & (loads <= upper)
        ax.scatter(disps[in_range], loads[in_range], color="cyan", s=40, alpha=0.7, zorder=4,
                   label=f"Initial Slope Range ({params['range_start']:.2f}-{params['range_end']:.2f})")
        ax.legend()

    ax.set_title(f"Yield Point Analysis ({yield_method.capitalize()} Method)")
    slope_unit = f"{y_unit}/{x_unit}" if x_unit and y_unit else None
    info_text = (
        "Yield Point:\n"
        f"  Displacement: {_with_unit(yield_disp, x_unit)}\n"
        f"  Load: {_with_unit(yield_load, y_unit)}\n"
        f"  Initial Slope: {_with_unit(initial_slope, slope_unit)}"
    )
    ax.text(0.05, 0.95, info_text, transform=ax.transAxes, fontsize=10, verticalalignment="top",
            bbox={"boxstyle": "round", "facecolor": "wheat", "alpha": 0.5})
    return ax


def compare_yield_methods(
    yield_results: List[Dict[str, Any]],
    x_values: Optional[np.ndarray] = None,
    y_values: Optional[np.ndarray] = None,
    x_label: str = "Displacement",
    y_label: str = "Load",
    ax: Optional[Axes] = None,
    **kwargs: Any
) -> Axes:
    """複数の手法で求めた降伏点を1つのグラフに重ねて描画します

    Args:
        yield_results: [{"method", "yield_disp", "yield_load", "initial_slope", "parameters"}, ...]
        x_values: 元の変位データ配列（None なら描画しない）
        y_values: 元の荷重データ配列（None なら描画しない）
        x_label: X 軸ラベル
        y_label: Y 軸ラベル
        ax: 描画先の Axes（None の場合は新しい図を作成）
        **kwargs: 元データの描画に渡す追加引数

    Examples:
        >>> import numpy as np
        >>> from tascpy.domains.load_displacement.draw import compare_yield_methods
        >>> results = [{"method": "offset", "yield_disp": 1.2, "yield_load": 5.5, "initial_slope": 5.0,
        ...             "parameters": {"offset_value": 0.2}}]
        >>> ax = compare_yield_methods(results)
    """
    ax = new_axes(ax, figsize=(10, 6))
    _plot_original(ax, x_values, y_values, x_label, y_label,
                   {"label": "Load-Displacement Data", "color": "black", "alpha": 0.7, **kwargs})
    colors = ["red", "blue", "green", "purple", "orange"]

    for i, result in enumerate(yield_results):
        yield_disp, yield_load = result.get("yield_disp"), result.get("yield_load")
        if yield_disp is None or yield_load is None:
            continue
        color = colors[i % len(colors)]
        method = result.get("method", "unknown")
        params = result.get("parameters", {})
        if method == "offset":
            label = f"Offset ({params.get('offset_value', 0.002)})"
        else:
            label = f"{method.capitalize()} (factor={params.get('factor', 0.33)})"
        ax.scatter([yield_disp], [yield_load], color=color, s=80, marker="o", label=label, zorder=5 + i)

        if method == "offset":
            offset = params.get("offset_value", 0.002) * _peak_sign(x_values, y_values, yield_load)
            ax.axline(xy1=(offset, 0), slope=result.get("initial_slope", 1.0), linestyle="--", color=color,
                      alpha=0.6, label=f"Offset Line ({params.get('offset_value', 0.002)})", zorder=2 + i)

    if ax.get_legend_handles_labels()[0]:
        ax.legend()
    ax.grid(True, linestyle="--", alpha=0.7)
    ax.set_title("Comparison of Yield Point Methods")
    return ax


def plot_multiple_curves(
    curves_data: List[Dict[str, Any]],
    x_label: str = "Displacement",
    y_label: str = "Load",
    ax: Optional[Axes] = None,
) -> Axes:
    """複数の曲線を重ねて描画します

    Args:
        curves_data: [{"type": "original" | 任意, "x": 配列, "y": 配列, "kwargs": {...}}, ...]
            "original" は core の plot で描画するため、kwargs に plot_type="scatter" なども指定できます
        x_label: X 軸ラベル
        y_label: Y 軸ラベル
        ax: 描画先の Axes（None の場合は新しい図を作成）

    Returns:
        Axes: 描画した Axes（x / y がない曲線は警告を出して飛ばす）
    """
    ax = new_axes(ax, figsize=(10, 8))
    for curve in curves_data:
        x_arr, y_arr = curve.get("x"), curve.get("y")
        if x_arr is None or y_arr is None:
            warnings.warn(f"曲線 '{curve.get('type', 'unknown')}' の x / y がないため描画しません", stacklevel=2)
            continue
        if curve.get("type") == "original":
            core_plot(x_arr, y_arr, ax=ax, **{"title": "", **curve.get("kwargs", {})})
        else:
            ax.plot(x_arr, y_arr, **curve.get("kwargs", {}))
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    if ax.get_legend_handles_labels()[0]:
        ax.legend()
    ax.grid(True, linestyle="--", alpha=0.7)
    return ax
