"""Core ドメインの可視化モジュール

副作用（Matplotlib, Plotlyによる描画）を伴う関数群です。
コレクションの `plot` プロキシから呼び出されることを想定しています。
"""

from typing import Optional, Union, List, Dict, Any
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

# 日本語フォントサポート
try:
    import japanize_matplotlib
    # マイナス記号を正しく表示するための設定
    mpl.rcParams["axes.unicode_minus"] = False
except ImportError:
    print(
        "警告: japanize_matplotlib をインポートできません。日本語が正しく表示されない可能性があります。"
    )

from tascpy.analytics.functional.core import plot_utils as functional_plot
from tascpy.visualization import backend_mpl
from tascpy.visualization import backend_plotly
from tascpy.analytics.functional import stats as functional_stats


def plot(
    x_values: np.ndarray,
    y_values: np.ndarray,
    x_label: str = "",
    y_label: str = "",
    title: Optional[str] = None,
    ax: Optional[plt.Axes] = None,
    **kwargs
) -> plt.Axes:
    """基本的なプロットを行います。

    Matplotlibを使用して散布図や折れ線グラフなどを描画します。

    Args:
        x_values (np.ndarray): X軸データの配列。
        y_values (np.ndarray): Y軸データの配列。
        x_label (str, optional): X軸のラベル。デフォルトは空文字列。
        y_label (str, optional): Y軸のラベル。デフォルトは空文字列。
        title (Optional[str], optional): グラフのタイトル。Noneの場合は自動生成されます。
        ax (Optional[plt.Axes], optional): 描画先のAxes。Noneの場合は新しく作成されます。
        **kwargs: Matplotlibのplot関数に渡される追加引数（color, marker, linestyleなど）。

    Returns:
        plt.Axes: 描画されたAxesオブジェクト。
        
    Examples:
        >>> from tascpy.visualization.functional.core.plot import plot
        >>> import numpy as np
        >>> x = np.array([0, 1, 2])
        >>> y = np.array([0, 10, 20])
        >>> ax = plot(x, y, x_label="Time (s)", y_label="Speed (m/s)")
    """
    if title is None:
        title = f"{y_label.split(' [')[0]} vs {x_label.split(' [')[0]}"
        
    return backend_mpl.plot(
        x_values=x_values,
        y_values=y_values,
        x_label=x_label,
        y_label=y_label,
        title=title,
        ax=ax,
        **kwargs
    )


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
    ax: Optional[plt.Axes] = None,
    edge_handling: str = "asymmetric",
    min_abs_value: float = 1e-10,
    scale_factor: float = 1.0,
    **kwargs
) -> plt.Axes:
    """異常値を検出し可視化します。

    移動平均を用いた外れ値検出を行い、正常値と異常値を色分けしてプロットします。

    Args:
        x_values (np.ndarray): X軸データの配列。
        y_values (np.ndarray): Y軸データの配列（異常値検出の対象）。
        x_label (str, optional): X軸のラベル。デフォルトは空文字列。
        y_label (str, optional): Y軸のラベル。デフォルトは空文字列。
        window_size (int, optional): 異常値検出用の移動平均ウィンドウサイズ。デフォルトは 3。
        threshold (float, optional): 異常値判定の閾値。デフォルトは 0.5。
        highlight_color (str, optional): 異常値のプロット色。デフォルトは "red"。
        plot_type (str, optional): 正常値のプロットタイプ("line" または "scatter")。デフォルトは "scatter"。
        show_normal (bool, optional): 正常値をプロットするかどうか。デフォルトは True。
        normal_color (str, optional): 正常値のプロット色。デフォルトは "blue"。
        normal_alpha (float, optional): 正常値の透明度。デフォルトは 0.5。
        outlier_marker (str, optional): 異常値のマーカー形状。デフォルトは "o"。
        outlier_size (int, optional): 異常値のマーカーサイズ。デフォルトは 50。
        ax (Optional[plt.Axes], optional): 描画先のAxes。Noneの場合は新しく作成されます。
        edge_handling (str, optional): 境界データの処理方法。デフォルトは "asymmetric"。
        min_abs_value (float, optional): ゼロ除算防止の最小絶対値。デフォルトは 1e-10。
        scale_factor (float, optional): スケールファクタ。デフォルトは 1.0。
        **kwargs: Matplotlibに渡される追加引数。

    Returns:
        plt.Axes: 描画されたAxesオブジェクト。
    """
    
    # 計算ロジック（純粋関数）の呼び出し
    flags = functional_stats.detect_outliers(
        y_values,
        window_size=window_size,
        threshold=threshold,
        edge_handling=edge_handling,
        min_abs_value=min_abs_value,
        scale_factor=scale_factor,
    )
    
    x_normal, y_normal, x_out, y_out, outlier_count = functional_plot.prepare_outlier_data(
        x_values, y_values, flags
    )
    
    # 副作用（描画）ロジック
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    if show_normal:
        plot_kwargs = kwargs.copy()
        plot_kwargs["color"] = normal_color
        plot_kwargs["alpha"] = normal_alpha
        plot_kwargs["plot_type"] = plot_type
        
        backend_mpl.plot(
            x_values=x_normal,
            y_values=y_normal,
            x_label=x_label,
            y_label=y_label,
            title="", 
            ax=ax,
            **plot_kwargs
        )

    if outlier_count > 0:
        print(f"visualize_outliers: {outlier_count}個の異常値をプロットします")
        outlier_kwargs = {
            "color": highlight_color,
            "plot_type": "scatter",
            "s": outlier_size,
            "marker": outlier_marker,
            "label": "異常値",
            "zorder": 10,
        }
        
        backend_mpl.plot(
            x_values=x_out,
            y_values=y_out,
            x_label=x_label, 
            y_label=y_label,
            title="",
            ax=ax,
            **outlier_kwargs
        )
    else:
        print("visualize_outliers: 異常値は検出されませんでした")
        
    y_name_for_title = y_label.split(" [")[0]
    ax.set_title(f"異常値検出: {y_name_for_title} (検出数: {outlier_count}個)")

    if show_normal or outlier_count > 0:
        ax.legend()
    ax.grid(True, alpha=0.3)
    
    return ax


def plot_const_x(
    y_data: Dict[str, np.ndarray],
    x_values: np.ndarray,
    ax: Optional[plt.Axes] = None,
    **kwargs
) -> plt.Axes:
    """共通のX軸に対して複数のY列をプロットします。

    Args:
        y_data (Dict[str, np.ndarray]): 各Y軸の名前をキー、データ配列を値とする辞書。
        x_values (np.ndarray): 共通のX軸データの配列。
        ax (Optional[plt.Axes], optional): 描画先のAxes。Noneの場合は新しく作成されます。
        **kwargs: グラフタイトル(title)やラベル(x_label, y_label)、Matplotlib引数。

    Returns:
        plt.Axes: 描画されたAxesオブジェクト。
        
    Examples:
        >>> from tascpy.visualization.functional.core.plot import plot_const_x
        >>> import numpy as np
        >>> x = np.array([0, 1, 2])
        >>> y_dict = {"Sensor 1": np.array([1, 2, 3]), "Sensor 2": np.array([3, 2, 1])}
        >>> ax = plot_const_x(y_dict, x, x_label="Position (m)", y_label="Temperature (C)")
    """
            
    # 計算ロジック（純粋関数）
    x_arr, y_arr = functional_plot.prepare_const_x_data(y_data, x_values)

    x_label = kwargs.pop("x_label", "X Parameters")
    y_label = kwargs.pop("y_label", "Y Values")
    title = kwargs.pop("title", f"Plot of {len(y_data)} columns vs X")
    
    return backend_mpl.plot(
        x_values=x_arr,
        y_values=y_arr,
        x_label=x_label,
        y_label=y_label,
        title=title,
        ax=ax,
        **kwargs
    )


def iplot(
    x_values: np.ndarray,
    y_values: np.ndarray,
    x_label: str = "",
    y_label: str = "",
    title: Optional[str] = None,
    fig: Optional[Any] = None,
    **kwargs
) -> Any:
    """インタラクティブなプロットを行います（Jupyter/Plotly環境用）。

    Plotlyを使用して、ホバーで値が確認できるインタラクティブなグラフを描画します。

    Args:
        x_values (np.ndarray): X軸データの配列。
        y_values (np.ndarray): Y軸データの配列。
        x_label (str, optional): X軸のラベル。デフォルトは空文字列。
        y_label (str, optional): Y軸のラベル。デフォルトは空文字列。
        title (Optional[str], optional): グラフのタイトル。Noneの場合は自動生成されます。
        fig (Optional[Any], optional): 描画先のPlotly Figure。Noneの場合は新しく作成されます。
        **kwargs: Plotly関数に渡される追加引数。

    Returns:
        Any: 描画されたPlotly Figureオブジェクト。
        
    Examples:
        >>> from tascpy.visualization.functional.core.plot import iplot
        >>> import numpy as np
        >>> x = np.array([0, 1, 2])
        >>> y = np.array([0, 10, 20])
        >>> fig = iplot(x, y, x_label="Time (s)", y_label="Speed (m/s)")
    """
    if title is None:
        title = f"{y_label.split(' [')[0]} vs {x_label.split(' [')[0]}"
    
    plot_name = kwargs.pop("name", y_label.split(" [")[0])

    return backend_plotly.plot(
        x_values=x_values,
        y_values=y_values,
        x_label=x_label,
        y_label=y_label,
        title=title,
        fig=fig,
        name=plot_name,
        **kwargs
    )
