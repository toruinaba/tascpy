"""Core ドメインの描画関数

配列を受け取って描画し、Axes（Plotly の場合は Figure）を返します。図の表示（plt.show）は呼び出し側で行います。
"""

from typing import Any, Dict, Optional

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes

from tascpy.analytics.functional.core import stats as functional_stats
from tascpy.visualization import backend_plotly
from tascpy.visualization.functional.core import plot_utils


def new_axes(ax: Optional[Axes] = None, figsize: tuple = (8, 6)) -> Axes:
    """ax が指定されていればそれを、なければ新しい図の Axes を返します"""
    if ax is not None:
        return ax
    _, new_ax = plt.subplots(figsize=figsize)
    return new_ax


def _label_name(label: str) -> str:
    return label.split(" [")[0]


def plot(
    x_values: np.ndarray,
    y_values: np.ndarray,
    x_label: str = "",
    y_label: str = "",
    title: Optional[str] = None,
    ax: Optional[Axes] = None,
    plot_type: str = "line",
    **kwargs: Any
) -> Axes:
    """折れ線グラフまたは散布図を描画します。

    Args:
        x_values: X 軸データの配列
        y_values: Y 軸データの配列
        x_label: X 軸のラベル
        y_label: Y 軸のラベル
        title: タイトル（None の場合は "Y vs X"）
        ax: 描画先の Axes（None の場合は新しい図を作成）
        plot_type: "line" または "scatter"
        **kwargs: matplotlib の plot / scatter に渡す追加引数

    Returns:
        Axes: 描画した Axes

    Examples:
        >>> import numpy as np
        >>> from tascpy.visualization.functional.core.plot import plot
        >>> ax = plot(np.array([0, 1, 2]), np.array([0, 10, 20]), x_label="Time [s]", y_label="Speed [m/s]")
    """
    if plot_type not in ("line", "scatter"):
        raise ValueError(f"plot_type は 'line' または 'scatter' で指定してください: {plot_type}")
    ax = new_axes(ax)
    if plot_type == "scatter":
        ax.scatter(x_values, y_values, **kwargs)
    else:
        ax.plot(x_values, y_values, **kwargs)
    if x_label:
        ax.set_xlabel(x_label)
    if y_label:
        ax.set_ylabel(y_label)
    if title is None and (x_label or y_label):
        title = f"{_label_name(y_label)} vs {_label_name(x_label)}"
    if title:
        ax.set_title(title)
    return ax


def visualize_outliers(
    x_values: np.ndarray,
    y_values: np.ndarray,
    x_label: str = "",
    y_label: str = "",
    window_size: int = 3,
    threshold: float = 0.5,
    highlight_color: str = "red",
    plot_type: str = "scatter",
    show_normal: bool = True,
    normal_color: str = "blue",
    normal_alpha: float = 0.5,
    outlier_marker: str = "o",
    outlier_size: int = 50,
    ax: Optional[Axes] = None,
    min_abs_value: float = 1e-10,
    scale_factor: float = 1.0,
    **kwargs: Any
) -> Axes:
    """移動平均に基づく外れ値を検出し、正常値と外れ値を色分けして描画します。

    Args:
        x_values: X 軸データの配列
        y_values: Y 軸データの配列（外れ値検出の対象）
        x_label: X 軸のラベル
        y_label: Y 軸のラベル
        window_size: 外れ値検出用の移動平均ウィンドウサイズ
        threshold: 外れ値判定の閾値
        highlight_color: 外れ値の色
        plot_type: 正常値の描画方法 ("line" または "scatter")
        show_normal: 正常値も描画するかどうか
        normal_color: 正常値の色
        normal_alpha: 正常値の透明度
        outlier_marker: 外れ値のマーカー形状
        outlier_size: 外れ値のマーカーサイズ
        ax: 描画先の Axes（None の場合は新しい図を作成）
        min_abs_value: ゼロ除算防止の最小絶対値
        scale_factor: スケールファクタ
        **kwargs: 正常値の描画に渡す追加引数

    Returns:
        Axes: 描画した Axes（タイトルに検出数を表示）
    """
    flags = functional_stats.detect_outliers(
        y_values, window_size=window_size, threshold=threshold,
        min_abs_value=min_abs_value, scale_factor=scale_factor,
    )
    x_normal, y_normal, x_out, y_out, outlier_count = plot_utils.prepare_outlier_data(x_values, y_values, flags)

    ax = new_axes(ax, figsize=(10, 6))
    if show_normal:
        plot(x_normal, y_normal, x_label=x_label, y_label=y_label, title="", ax=ax, plot_type=plot_type,
             **{"label": "正常値", **kwargs, "color": normal_color, "alpha": normal_alpha})
    if outlier_count > 0:
        ax.scatter(x_out, y_out, color=highlight_color, s=outlier_size, marker=outlier_marker,
                   label="異常値", zorder=10)
    if x_label:
        ax.set_xlabel(x_label)
    if y_label:
        ax.set_ylabel(y_label)
    ax.set_title(f"異常値検出: {_label_name(y_label)} (検出数: {outlier_count}個)")
    if show_normal or outlier_count > 0:
        ax.legend()
    ax.grid(True, alpha=0.3)
    return ax


def plot_const_x(
    y_data: Dict[str, Any],
    x_values: np.ndarray,
    x_label: str = "",
    y_label: str = "",
    title: Optional[str] = None,
    ax: Optional[Axes] = None,
    **kwargs: Any
) -> Axes:
    """列ごとの位置（共通の X 軸）に、各列の1つの値を並べて描画します（ひずみ分布など）。

    Args:
        y_data: {列のラベル: 値（スカラー）}
        x_values: 各列の位置（y_data と同じ数）
        x_label: X 軸のラベル
        y_label: Y 軸のラベル
        title: タイトル（None の場合は "Y vs X"）
        ax: 描画先の Axes（None の場合は新しい図を作成）
        **kwargs: matplotlib の plot に渡す追加引数

    Returns:
        Axes: 描画した Axes

    Examples:
        >>> import numpy as np
        >>> from tascpy.visualization.functional.core.plot import plot_const_x
        >>> ax = plot_const_x({"S1": 1.0, "S2": 3.0}, np.array([0.0, 1.0]), x_label="Position [m]", y_label="T [C]")
    """
    x_arr, y_arr = plot_utils.prepare_const_x_data(y_data, x_values)
    kwargs.setdefault("marker", "o")
    return plot(x_arr, y_arr, x_label=x_label, y_label=y_label, title=title, ax=ax, **kwargs)


def iplot(
    x_values: np.ndarray,
    y_values: np.ndarray,
    x_label: str = "",
    y_label: str = "",
    title: Optional[str] = None,
    fig: Optional[Any] = None,
    **kwargs: Any
) -> Any:
    """Plotly でインタラクティブなグラフを描画します。

    Args:
        x_values: X 軸データの配列
        y_values: Y 軸データの配列
        x_label: X 軸のラベル
        y_label: Y 軸のラベル
        title: タイトル（None の場合は "Y vs X"）
        fig: 描画先の Plotly Figure（None の場合は新規作成）
        **kwargs: Plotly の Scatter に渡す追加引数（name, color など）

    Returns:
        Any: Plotly Figure

    Examples:
        >>> import numpy as np
        >>> from tascpy.visualization.functional.core.plot import iplot
        >>> fig = iplot(np.array([0, 1, 2]), np.array([0, 10, 20]), x_label="Time [s]", y_label="Speed [m/s]")
    """
    if title is None:
        title = f"{_label_name(y_label)} vs {_label_name(x_label)}"
    name = kwargs.pop("name", _label_name(y_label))
    return backend_plotly.plot(x_values=x_values, y_values=y_values, x_label=x_label, y_label=y_label,
                               title=title, fig=fig, name=name, **kwargs)
