"""プロットに関する操作モジュール"""

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

from ...operations.registry import operation
from ...core.collection import ColumnCollection
from ..abstraction import extract_axis_data
from ...functional import plot as functional_plot


@operation(domain="core")
def plot(
    collection: ColumnCollection,
    y_column: str,
    x_column: Optional[str] = None,
    ax: Optional[plt.Axes] = None,
    **kwargs
) -> plt.Axes:
    """基本的なプロットを行います"""
    x_values, x_name, x_unit = extract_axis_data(collection, x_column)
    y_values, y_name, y_unit = extract_axis_data(collection, y_column)
    
    x_label = f"{x_name} [{x_unit}]" if x_unit else x_name
    y_label = f"{y_name} [{y_unit}]" if y_unit else y_name
    title = f"{y_name} vs {x_name}"
    
    return functional_plot.plot(
        x_values=np.array(x_values),
        y_values=np.array(y_values),
        x_label=x_label,
        y_label=y_label,
        title=title,
        ax=ax,
        **kwargs
    )


@operation(domain="core")
def visualize_outliers(
    collection: ColumnCollection,
    column: str,
    x_column: Optional[str] = None,
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
    """異常値を検出し可視化します"""
    x_values, x_name, x_unit = extract_axis_data(collection, x_column)
    y_values, y_name, y_unit = extract_axis_data(collection, column)
    
    x_label = f"{x_name} [{x_unit}]" if x_unit else x_name
    y_label = f"{y_name} [{y_unit}]" if y_unit else y_name
    title = f"Outlier Detection: {y_name}"
    
    return functional_plot.visualize_outliers(
        x_values=np.array(x_values),
        y_values=np.array(y_values),
        x_label=x_label,
        y_label=y_label,
        title=title,
        window_size=window_size,
        threshold=threshold,
        highlight_color=highlight_color,
        plot_type=plot_type,
        show_normal=show_normal,
        normal_color=normal_color,
        normal_alpha=normal_alpha,
        outlier_marker=outlier_marker,
        outlier_size=outlier_size,
        ax=ax,
        edge_handling=edge_handling,
        min_abs_value=min_abs_value,
        scale_factor=scale_factor,
        **kwargs
    )


@operation(domain="core")
def plot_const_x(
    collection: ColumnCollection,
    x_values: List[float],
    y_columns: List[str],
    ax: Optional[plt.Axes] = None,
    **kwargs
) -> plt.Axes:
    """共通のX軸に対して複数のY列をプロットします"""
    if x_values is None:
        x_values = collection.step.values
        
    y_data = {}
    for col_name in y_columns:
        if col_name in collection.columns:
            y_data[col_name] = np.array(collection.columns[col_name].values)
            
    return functional_plot.plot_const_x(
        y_data=y_data,
        x_values=np.array(x_values),
        ax=ax,
        **kwargs
    )


@operation(domain="core")
def iplot(
    collection: ColumnCollection,
    y_column: str,
    x_column: Optional[str] = None,
    **kwargs
) -> Any:
    """インタラクティブなプロットを行います（Jupyter用）"""
    x_values, x_name, x_unit = extract_axis_data(collection, x_column)
    y_values, y_name, y_unit = extract_axis_data(collection, y_column)
    
    x_label = f"{x_name} [{x_unit}]" if x_unit else x_name
    y_label = f"{y_name} [{y_unit}]" if y_unit else y_name
    title = f"{y_name} vs {x_name}"
    
    return functional_plot.iplot(
        x_values=np.array(x_values),
        y_values=np.array(y_values),
        x_label=x_label,
        y_label=y_label,
        title=title,
        **kwargs
    )
