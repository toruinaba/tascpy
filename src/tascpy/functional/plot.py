from typing import Tuple, Dict, Any, List, Optional
import numpy as np
import matplotlib.pyplot as plt
from ..visualization import backend_mpl
from . import stats as functional_stats

def plot(
    x_values: np.ndarray,
    y_values: np.ndarray,
    x_label: str,
    y_label: str,
    title: str,
    ax: Optional[plt.Axes] = None,
    **kwargs,
) -> plt.Axes:
    """基本プロットを行います (Functional wrapper)。

    Args:
        x_values (np.ndarray): x軸のデータ配列。
        y_values (np.ndarray): y軸のデータ配列。
        x_label (str): x軸のラベル。
        y_label (str): y軸のラベル。
        title (str): グラフのタイトル。
        ax (Optional[plt.Axes], optional): 描画先のMatplotlib Axesオブジェクト。Noneの場合は新規作成されます。デフォルトは None。
        **kwargs: その他のプロットオプション（color, marker, linestyleなど）。

    Returns:
        plt.Axes: 描画に使用されたAxesオブジェクト。
    """
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
    x_values: Any,
    y_values: Any,
    x_label: str,
    y_label: str,
    title: str,
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
    """異常値を検出し可視化します (Functional implementation)。

    Args:
        x_values (Any): x軸のデータ配列。
        y_values (Any): y軸のデータ配列。
        x_label (str): x軸のラベル。
        y_label (str): y軸のラベル。
        title (str): グラフのタイトル。
        window_size (int, optional): 外れ値検出のウィンドウサイズ。デフォルトは 3。
        threshold (float, optional): 外れ値検出の閾値。デフォルトは 0.5。
        highlight_color (str, optional): 異常値のハイライト色。デフォルトは "red"。
        plot_type (str, optional): プロットタイプ ('scatter', 'line' など)。デフォルトは "scatter"。
        show_normal (bool, optional): 正常値を描画するかどうか。デフォルトは True。
        normal_color (str, optional): 正常値の色。デフォルトは "blue"。
        normal_alpha (float, optional): 正常値の透明度。デフォルトは 0.5。
        outlier_marker (str, optional): 異常値のマーカー形状。デフォルトは "o"。
        outlier_size (int, optional): 異常値のマーカーサイズ。デフォルトは 50。
        ax (Optional[plt.Axes], optional): 描画先のAxesオブジェクト。デフォルトは None。
        edge_handling (str, optional): 境界処理の方法。デフォルトは "asymmetric"。
        min_abs_value (float, optional): 最小絶対値（ゼロ除算防止）。デフォルトは 1e-10。
        scale_factor (float, optional): 閾値のスケーリング係数。デフォルトは 1.0。
        **kwargs: その他のプロットオプション。

    Returns:
        plt.Axes: 描画に使用されたAxesオブジェクト。
    """
    # 1. Detect Outliers
    flags = functional_stats.detect_outliers(
        y_values,
        window_size=window_size,
        threshold=threshold,
        edge_handling=edge_handling,
        min_abs_value=min_abs_value,
        scale_factor=scale_factor,
    )
    
    # 2. Prepare Data
    x_normal, y_normal, x_out, y_out, outlier_count = prepare_outlier_data(
        x_values, y_values, flags
    )
    
    # 3. Draw
    # Create new figure if needed (handled in backend if ax is None? backend_mpl.plot handles it)
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    # Determine Title
    # Logic from original: if title starts with "Outlier", pass. Else use incoming title?
    # Actually, inject_plot_data provides a title. 
    # Original logic:
    # y_name_for_title = y_label.split(" [")[0]
    # ax.set_title(f"異常値検出: {y_name_for_title} (検出数: {outlier_count}個)")
    # We should preserve this behavior.
    
    # Draw Normal
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
            title="", # Don't set title yet
            ax=ax,
            **plot_kwargs
        )

    # Draw Outliers
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
        
        # Debug print
        if len(x_out) > 0:
            debug_count = min(3, len(x_out))
            print(f"最初の{debug_count}個の異常値データ: {list(zip(x_out[:debug_count], y_out[:debug_count]))}")

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
        
    # Set Final Title
    y_name_for_title = y_label.split(" [")[0]
    ax.set_title(f"異常値検出: {y_name_for_title} (検出数: {outlier_count}個)")

    # Legend & Grid
    if show_normal or outlier_count > 0:
        ax.legend()
    ax.grid(True, alpha=0.3)
    
    return ax


def iplot(
    x_values: np.ndarray,
    y_values: np.ndarray,
    x_label: str,
    y_label: str,
    title: str,
    fig: Optional[Any] = None,
    **kwargs,
) -> Any:
    """インタラクティブなグラフを描画します (Functional wrapper)。

    Plotlyを使用してインタラクティブなプロットを作成します。

    Args:
        x_values (np.ndarray): x軸のデータ配列。
        y_values (np.ndarray): y軸のデータ配列。
        x_label (str): x軸のラベル。
        y_label (str): y軸のラベル。
        title (str): グラフのタイトル。
        fig (Optional[Any], optional): 既存のPlotly Figureオブジェクト。Noneの場合は新規作成されます。デフォルトは None。
        **kwargs: その他のプロットオプション (name, color, symbol, sizeなど)。

    Returns:
        Any: PlotlyのFigureオブジェクト。
    """
    from ..visualization import backend_plotly
    
    # y_label format is "Name [Unit]" or "Name".
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

def plot_const_x(
    y_data: Dict[str, Any],
    x_values: List[float],
    show_legend: bool = True,
    ax: Optional[plt.Axes] = None,
    **kwargs
) -> plt.Axes:
    """特定のx値に対して複数のy列の値をプロットします。

    Args:
        y_data (Dict[str, Any]): プロットするyデータの辞書（キー: 名前, 値: データ列またはスカラー）。
        x_values (List[float]): x軸の値のリスト（y_dataと同じ長さが必要）。
        show_legend (bool, optional): 凡例を表示するかどうか。デフォルトは True。
        ax (Optional[plt.Axes], optional): 描画先のAxesオブジェクト。デフォルトは None。
        **kwargs: その他のプロットオプション (x_label, y_label, titleなど)。

    Returns:
        plt.Axes: 描画に使用されたAxesオブジェクト。
    """
    x_arr, y_arr = prepare_const_x_data(y_data, x_values)

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

def prepare_outlier_data(
    x_values: np.ndarray,
    y_values: np.ndarray,
    flags: List[int],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, int]:
    """異常値フラグに基づいてデータを正常値と異常値に分割します。

    Args:
        x_values (np.ndarray): x軸のデータ配列。
        y_values (np.ndarray): y軸のデータ配列。
        flags (List[int]): 異常値フラグのリスト（0: 正常, 1: 異常）。

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, int]: 
            (正常値x, 正常値y, 異常値x, 異常値y, 異常値カウント) のタプル。
    """
    flags_arr = np.array(flags)
    x_arr = np.array(x_values)
    y_arr = np.array(y_values)
    
    normal_mask = (flags_arr == 0)
    outlier_mask = (flags_arr == 1)
    
    outlier_count = np.sum(outlier_mask)
    
    x_normal = x_arr[normal_mask]
    y_normal = y_arr[normal_mask]
    x_outlier = x_arr[outlier_mask]
    y_outlier = y_arr[outlier_mask]
    
    return x_normal, y_normal, x_outlier, y_outlier, outlier_count

def prepare_const_x_data(
    y_data: Dict[str, Any],
    x_values: List[float],
) -> Tuple[np.ndarray, np.ndarray]:
    """yデータ列から最初の値を抽出し、x値とペアにします。

    Args:
        y_data (Dict[str, Any]): yデータの辞書。
        x_values (List[float]): x値のリスト。

    Returns:
        Tuple[np.ndarray, np.ndarray]: (x配列, y配列) のタプル。

    Raises:
        ValueError: x_valuesの長さとy_dataの長さが一致しない場合。
    """
    if len(x_values) != len(y_data):
        raise ValueError(f"x_valuesの長さ({len(x_values)})とy_columnsの長さ({len(y_data)})が一致しません")

    y_vals_list = []
    
    for col_vals in y_data.values():
        val_to_append = float('nan')
        # Check if array-like
        if hasattr(col_vals, '__len__'):
             if len(col_vals) > 0:
                 try:
                     val = col_vals[0]
                     val_to_append = float(val) if val is not None else float('nan')
                 except:
                     pass
        elif np.isscalar(col_vals):
             try:
                 val_to_append = float(col_vals)
             except:
                 pass
             
        y_vals_list.append(val_to_append)

    x_arr = np.array(x_values)
    y_arr = np.array(y_vals_list)
    
    return x_arr, y_arr
