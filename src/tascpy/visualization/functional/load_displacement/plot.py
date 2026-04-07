"""荷重-変位データのプロット関数"""

from typing import Optional, Dict, Any, Tuple, List, Union
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from matplotlib.figure import Figure
from matplotlib.axes import Axes

# Import japanize_matplotlib for Japanese font support
try:
    import japanize_matplotlib

    # Ensure minus signs are displayed correctly
    mpl.rcParams["axes.unicode_minus"] = False
except ImportError:
    print(
        "Warning: japanize_matplotlib could not be imported. Japanese text may not display correctly."
    )

from tascpy.domains.load_displacement import LoadDisplacementCollection
from tascpy.visualization.functional.core.plot import plot as core_plot
from tascpy.visualization import backend_mpl as mpl_backend


def plot_load_displacement(
    x_values: np.ndarray,
    y_values: np.ndarray,
    x_label: str = "Displacement",
    y_label: str = "Load",
    title: Optional[str] = None,
    ax: Optional[Axes] = None,
    **kwargs
) -> Axes:
    """荷重-変位曲線をプロットします

    荷重-変位データを二次元グラフとしてプロットします.
    既存の軸オブジェクトを指定することも、新しく作成することもできます.

    Args:
        collection: 荷重-変位コレクション
        ax: プロット先の軸(None の場合は新規作成)
        **kwargs: matplotlib の plot 関数に渡す追加引数

    Returns:
        Axes: プロットされた軸オブジェクト
        
    Examples:
        >>> from tascpy.visualization.functional.load_displacement.plot import plot_load_displacement
        >>> import numpy as np
        >>> disp = np.array([0, 1, 2, 3])
        >>> load = np.array([0, 5, 10, 8])
        >>> ax = plot_load_displacement(disp, load, x_label="Disp (mm)", y_label="Load (kN)")
    """
    if title is None:
        title = "Load-Displacement Curve"
        
    plot_kwargs = kwargs.copy()
    plot_kwargs.setdefault("plot_type", "line")

    return core_plot(
        x_values=x_values, y_values=y_values, x_label=x_label, y_label=y_label, title=title, ax=ax, **plot_kwargs
    )


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
    """スケルトン曲線をプロットします

    create_skeleton_curve 関数で作成したスケルトン曲線をプロットします.
    元の荷重-変位データと比較して表示することも可能です.

    スケルトン曲線データは、列または metadata["curves"]["skeleton_curve"] から取得します.
    メタデータに格納されている場合はそちらが優先されます.

    # スケルトン曲線の配列と、オプションで元データをプロットします.

    Args:
        skeleton_x: スケルトン曲線の変位配列
        skeleton_y: スケルトン曲線の荷重配列
        # x_values: 元データの変位配列(None の場合はプロットしない)
        # y_values: 元データの荷重配列(None の場合はプロットしない)
        x_label: X軸ラベル
        y_label: Y軸ラベル
        ax: プロット先の軸(None の場合は新規作成)
        original_kwargs: 元データプロット用の追加引数
        skeleton_kwargs: スケルトン曲線プロット用の追加引数

    Returns:
        Axes: プロットされた軸オブジェクト
        
    Examples:
        >>> from tascpy.visualization.functional.load_displacement.plot import plot_skeleton_curve
        >>> import numpy as np
        >>> disp_orig = np.array([0, 1, 2, 3, 4, 5])
        >>> load_orig = np.array([0, 5, 10, 8, 12, 10])
        >>> skeleton_x = np.array([0, 2, 4])
        >>> skeleton_y = np.array([0, 10, 12])
        >>> ax = plot_skeleton_curve(skeleton_x, skeleton_y, x_values=disp_orig, y_values=load_orig)
    """
    # デフォルト引数の設定
    if original_kwargs is None:
        original_kwargs = {"alpha": 0.5, "label": "Original Data", "color": "gray"}
    if skeleton_kwargs is None:
        skeleton_kwargs = {"label": "Skeleton Curve", "color": "red", "linewidth": 2}

    # 軸が指定されていない場合は新規作成
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
        created_new_figure = True
    else:
        fig = ax.figure
        created_new_figure = False

    # 元のデータをプロット
    if x_values is not None and y_values is not None:
        # core_plotを使用して元データをプロット
        plot_kwargs = original_kwargs.copy()
        plot_kwargs.setdefault("plot_type", "line")
        core_plot(
            x_values=x_values,
            y_values=y_values,
            x_label=x_label,
            y_label=y_label,
            ax=ax,
            **plot_kwargs,
        )

    # スケルトン曲線のプロット
    ax.plot(skeleton_x, skeleton_y, **skeleton_kwargs)

    # タイトル設定とグリッド表示
    ax.set_title("Skeleton Curve Analysis")
    ax.grid(True, linestyle="--", alpha=0.7)
    ax.legend()

    # 新しい図を作成した場合のみグラフを表示
    if created_new_figure:
        plt.show()

    return ax


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
    """累積曲線をプロットします

    # 累積曲線の配列と、オプションで元データをプロットします.

    Args:
        cumulative_x: 累積曲線の変位配列
        cumulative_y: 累積曲線の荷重配列
        x_values: 元データの変位配列(None の場合はプロットしない)
        y_values: 元データの荷重配列(None の場合はプロットしない)
        x_label: X軸ラベル
        y_label: Y軸ラベル
        ax: プロット先の軸(None の場合は新規作成)
        original_kwargs: 元データプロット用の追加引数
        cumulative_kwargs: 累積曲線プロット用の追加引数

    Returns:
        Axes: プロットされた軸オブジェクト
        
    Examples:
        >>> from tascpy.visualization.functional.load_displacement.plot import plot_cumulative_curve
        >>> import numpy as np
        >>> disp_orig = np.array([0, 1, 2, 3, 4, 5])
        >>> load_orig = np.array([0, 5, 10, 8, 12, 10])
        >>> cumulative_x = np.array([0, 1, 2, 3, 4, 5])
        >>> cumulative_y = np.cumsum(np.abs(load_orig)) # Example cumulative load
        >>> ax = plot_cumulative_curve(cumulative_x, cumulative_y, x_values=disp_orig, y_values=load_orig)
    """
    # デフォルト引数の設定
    if original_kwargs is None:
        original_kwargs = {"alpha": 0.5, "label": "Original Data", "color": "gray"}
    if cumulative_kwargs is None:
        cumulative_kwargs = {
            "label": "Cumulative Curve",
            "color": "blue",
            "linewidth": 2,
        }

    # 軸が指定されていない場合は新規作成
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
        created_new_figure = True
    else:
        fig = ax.figure
        created_new_figure = False

    # 元のデータをプロット
    if x_values is not None and y_values is not None:
        # core_plotを使用して元データをプロット
        plot_kwargs = original_kwargs.copy()
        plot_kwargs.setdefault("plot_type", "line")
        core_plot(
            x_values=x_values,
            y_values=y_values,
            x_label=x_label,
            y_label=y_label,
            ax=ax,
            **plot_kwargs,
        )

    # 累積曲線のプロット
    ax.plot(cumulative_x, cumulative_y, **cumulative_kwargs)

    # タイトル設定とグリッド表示
    ax.set_title("Cumulative Curve Analysis")
    ax.grid(True, linestyle="--", alpha=0.7)
    ax.legend()

    # 新しい図を作成した場合のみグラフを表示
    if created_new_figure:
        plt.show()

    return ax


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
    result_prefix: str = "yield",
    **kwargs,
) -> Axes:
    """降伏点解析結果をプロットします

    find_yield_point 関数で解析した降伏点情報をビジュアル化します.
    元データ、初期勾配線、オフセット線などを表示できます.

    Args:
        yield_disp: 降伏点の変位
        yield_load: 降伏点の荷重
        yield_method: 降伏点決定の手法
        initial_slope: 初期勾配
        yield_parameters: 分析のパラメータ(オフセット値や係数など)
        x_values: 元の変位データ配列(Noneならプロットしない)
        y_values: 元の荷重データ配列(Noneならプロットしない)
        x_label: X軸ラベル
        y_label: Y軸ラベル
        ax: プロット先の軸(None の場合は新規作成)
        plot_original_data: 元の荷重-変位データもプロットするかどうか
        plot_initial_slope: 初期勾配線をプロットするかどうか
        plot_offset_line: オフセット線をプロットするかどうか(オフセット法の場合)
        result_prefix: 降伏点データの接頭辞
        **kwargs: matplotlib の plot 関数に渡す追加引数

    Returns:
        Axes: プロットされた軸オブジェクト
        
    Examples:
        >>> from tascpy.visualization.functional.load_displacement.plot import plot_yield_point
        >>> import numpy as np
        >>> disp = np.array([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
        >>> load = np.array([0, 2.5, 5.0, 6.5, 7.0, 7.2, 7.3])
        >>> yield_disp = 1.5
        >>> yield_load = 6.5
        >>> initial_slope = 5.0
        >>> ax = plot_yield_point(yield_disp, yield_load, initial_slope=initial_slope, x_values=disp, y_values=load)
        >>> # オフセット法の場合
        >>> yield_disp_offset = 1.2
        >>> yield_load_offset = 5.5
        >>> yield_params_offset = {"offset_value": 0.002}
        >>> ax_offset = plot_yield_point(yield_disp_offset, yield_load_offset, yield_method="offset",
        ...                              initial_slope=initial_slope, yield_parameters=yield_params_offset,
        ...                              x_values=disp, y_values=load)
    """
    if yield_parameters is None:
        yield_parameters = {}

    # 軸が指定されていない場合は新規作成
    created_new_figure = False
    if ax is None:
        ax = mpl_backend.create_figure(figsize=(8, 6))
        created_new_figure = True
    else:
        fig = ax.figure

    # 元の荷重変位データをプロット
    if plot_original_data and x_values is not None and y_values is not None:
        plot_load_displacement(
            x_values=x_values, y_values=y_values, x_label=x_label, y_label=y_label, ax=ax, **kwargs
        )

    mpl_backend.scatter_points(
        [yield_disp],
        [yield_load],
        ax=ax,
        color="red",
        s=80,
        marker="o",
        label=f"Yield Point ({yield_method})",
        zorder=5,
    )

    # 初期勾配線のプロット
    if plot_initial_slope:
        mpl_backend.draw_axline(
            ax=ax,
            xy1=(0, 0),
            slope=initial_slope,
            color="orange",
            linestyle="--",
            label="Initial Slope",
        )

    # オフセット法の場合はオフセット線も表示
    if yield_method == "offset" and plot_offset_line and "offset_value" in yield_parameters:
        offset_value = yield_parameters["offset_value"]
        mpl_backend.draw_axline(
            ax=ax,
            xy1=(offset_value, 0), slope=initial_slope, color="blue", linestyle="--"
        )

    # 一般降伏法の場合は勾配変化点の視覚化
    if yield_method == "general" and "factor" in yield_parameters:
        factor = yield_parameters["factor"]
        # 接線を表示
        tangent_length = yield_disp * 0.5
        x_vals = np.array([yield_disp - tangent_length, yield_disp + tangent_length])
        tangent_slope = initial_slope * factor
        y_vals = tangent_slope * (x_vals - yield_disp) + yield_load
        mpl_backend.draw_line(
            x_vals, y_vals, ax=ax, color="m", linestyle="--", label=f"Tangent ({factor:.2f}×Initial)", zorder=4
        )

    mpl_backend.add_legend(ax)
    mpl_backend.add_grid(ax, linestyle="--", alpha=0.7)

    # 新しい図を作成した場合のみグラフを表示
    if created_new_figure:
        mpl_backend.show_plot()

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
    **kwargs
) -> Axes:
    """降伏点解析の詳細情報をプロットします

    find_yield_point 関数で解析した降伏点情報の詳細をビジュアル化します.
    初期勾配の計算範囲などの追加情報も表示します.

    Args:
        yield_disp: 降伏点の変位
        yield_load: 降伏点の荷重
        yield_method: 降伏点決定の手法
        initial_slope: 初期勾配
        yield_parameters: 分析のパラメータ
        # x_values: 元の変位データ配列
        # y_values: 元の荷重データ配列
        x_label: X軸ラベル
        y_label: Y軸ラベル
        ax: プロット先の軸(None の場合は新規作成)
        **kwargs: matplotlib の plot 関数に渡す追加引数

    Returns:
        Axes: プロットされた軸オブジェクト
        
    Examples:
        >>> from tascpy.visualization.functional.load_displacement.plot import plot_yield_analysis_details
        >>> import numpy as np
        >>> disp = np.array([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
        >>> load = np.array([0, 2.5, 5.0, 6.5, 7.0, 7.2, 7.3])
        >>> yield_disp = 1.5
        >>> yield_load = 6.5
        >>> initial_slope = 5.0
        >>> yield_params = {"range_start": 0.1, "range_end": 0.4}
        >>> ax = plot_yield_analysis_details(yield_disp, yield_load, initial_slope=initial_slope,
        ...                                  yield_parameters=yield_params, x_values=disp, y_values=load)
    """
    if yield_parameters is None:
        yield_parameters = {}

    # 基本の降伏点プロット作成(委譲)
    plot_yield_point(
        yield_disp=yield_disp,
        yield_load=yield_load,
        yield_method=yield_method,
        initial_slope=initial_slope,
        yield_parameters=yield_parameters,
        x_values=x_values,
        y_values=y_values,
        x_label=x_label,
        y_label=y_label,
        ax=ax,
        **kwargs
    )

    # 使用されたaxオブジェクトを取得
    created_new_figure = False
    if ax is None:
        # 新しくplot_yield_pointが作成したaxを見つける必要がある
        # しかし plot_yield_point は ax を返さないので、Figureから取得するしかない (既存ロジック維持)
        if plt.get_fignums():
             fig = plt.gcf()  # 現在のfigureを取得
             if fig.axes:
                 ax = fig.axes[0]  # 最初のaxesを取得
                 created_new_figure = True
             else:
                 # fallback
                 ax = mpl_backend.create_figure()
        else:
             ax = mpl_backend.create_figure()
    else:
        fig = ax.figure
        created_new_figure = False

    # 初期勾配計算に使用した範囲をハイライト
    if x_values is not None and y_values is not None and "range_start" in yield_parameters and "range_end" in yield_parameters:
        range_start = yield_parameters["range_start"]
        range_end = yield_parameters["range_end"]
        max_load = np.max(y_values)

        lower_bound = max_load * range_start
        upper_bound = max_load * range_end

        range_mask = (y_values >= lower_bound) & (y_values <= upper_bound)
        range_disps = x_values[range_mask]
        range_loads = y_values[range_mask]

        mpl_backend.scatter_points(
            range_disps,
            range_loads,
            ax=ax,
            color="cyan",
            s=40,
            alpha=0.7,
            label=f"Initial Slope Range ({range_start:.2f}-{range_end:.2f})",
            zorder=4,
        )

    # 方法に応じた追加情報の表示
    title_text = f"Yield Point Analysis ({yield_method.capitalize()} Method)"
    mpl_backend.set_labels(ax, title=title_text)

    # 降伏点情報のテキスト表示
    info_text = (
        f"Yield Point:\n"
        f"  Displacement: {yield_disp:.4f}\n"
        f"  Load: {yield_load:.4f}\n"
        f"  Initial Slope: {initial_slope:.4f}"
    )

    # テキストボックスで情報表示
    props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
    mpl_backend.add_text(
        ax,
        0.05,
        0.95,
        info_text,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=props,
    )

    # 新しい図を作成した場合のみグラフを表示
    if created_new_figure:
        mpl_backend.show_plot()

    return ax



def compare_yield_methods(
    yield_results: List[Dict[str, Any]],
    x_values: Optional[np.ndarray] = None,
    y_values: Optional[np.ndarray] = None,
    x_label: str = "Displacement",
    y_label: str = "Load",
    ax: Optional[Axes] = None,
    **kwargs,
) -> Axes:
    """複数の降伏点計算結果を比較してプロットします

    異なる手法で計算した複数の降伏点データ(配列情報)を
    一つのグラフ上に表示して比較できます.

    Args:
        yield_results: 降伏点データとパラメータのリスト.例:
            [
              {
    Args:
        yield_results: 各降伏点メソッドの結果を含む辞書のリスト
        # x_values: 元の変位データ配列（Noneならプロットしない）
        # y_values: 元の荷重データ配列（Noneならプロットしない）
        x_label: X軸ラベル
        y_label: Y軸ラベル
        ax: プロット先の軸（None の場合は新規作成）
        **kwargs: 基礎となる荷重-変位プロットへの追加引数
        
    Examples:
        >>> from tascpy.visualization.functional.load_displacement.plot import compare_yield_methods
        >>> import numpy as np
        >>> disp = np.array([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
        >>> load = np.array([0, 2.5, 5.0, 6.5, 7.0, 7.2, 7.3])
        >>> results = [
        ...     {"method": "offset", "yield_disp": 1.2, "yield_load": 5.5, "initial_slope": 5.0, "parameters": {"offset_value": 0.002}},
        ...     {"method": "general", "yield_disp": 1.8, "yield_load": 6.8, "initial_slope": 5.0, "parameters": {"factor": 0.33}}
        ... ]
        >>> ax = compare_yield_methods(results, x_values=disp, y_values=load)
    """
    if not yield_results:
        return ax

    # 軸が指定されていない場合は新規作成
    created_new_figure = False
    if ax is None:
        ax = mpl_backend.create_figure(figsize=(10, 6))
        created_new_figure = True
    else:
        fig = ax.figure

    # 元データが提供されている場合のみプロットする
    if x_values is not None and y_values is not None:
        plot_load_displacement(
            x_values=x_values,
            y_values=y_values,
            x_label=x_label,
            y_label=y_label,
            ax=ax,
            label="Load-Displacement Data",
            color="black",
            alpha=0.7,
            **kwargs,
        )

    colors = ["red", "blue", "green", "purple", "orange"]

    for i, yield_data in enumerate(yield_results):
        color = colors[i % len(colors)]
        
        yield_disp = yield_data.get("yield_disp")
        yield_load = yield_data.get("yield_load")
        if yield_disp is None or yield_load is None:
            continue
            
        method = yield_data.get("method", "unknown")
        params = yield_data.get("parameters", {})
        initial_slope = yield_data.get("initial_slope", 1.0)

        method_name = method.capitalize()
        if method == "offset":
            method_label = f"{method_name} ({params.get('offset_value', 0.002)})"
        else:
            method_label = f"{method_name} (factor={params.get('factor', 0.33)})"

        mpl_backend.scatter_points(
            [yield_disp],
            [yield_load],
            ax=ax,
            color=color,
            s=80,
            marker="o",
            label=f"{method_label}",
            zorder=5 + i,
        )

        # 初期勾配線
        if x_values is not None:
            max_disp = np.max(x_values)
        else:
            max_disp = yield_disp * 2.0
            
        x_vals = np.array([0, max_disp])

        if method == "offset":
            # オフセット線も表示
            offset_value = params.get("offset_value", 0.002)
            y_vals = initial_slope * x_vals - initial_slope * offset_value
            mpl_backend.draw_line(
                x_vals,
                y_vals,
                ax=ax,
                linestyle="--",
                color=color,
                alpha=0.6,
                label=f"Offset Line ({offset_value})",
                zorder=2 + i,
            )

    mpl_backend.add_legend(ax)
    mpl_backend.add_grid(ax, linestyle="--", alpha=0.7)
    mpl_backend.set_labels(ax, title="Comparison of Yield Point Methods")

    # 新しい図を作成した場合のみグラフを表示
    if created_new_figure:
        mpl_backend.show_plot()

    return ax


def plot_multiple_curves(
    curves_data: List[Dict[str, Any]],
    x_label: str = "Displacement",
    y_label: str = "Load",
    ax: Optional[Axes] = None,
    **kwargs,
) -> Axes:
    """複数の曲線を指定してプロットします

    Args:
        curves_data: プロットする曲線の配列情報リスト.例:
                [
                    {
                        "type": "original", 
                        "x": np.ndarray, 
                        "y": np.ndarray, 
                        "kwargs": {...}
                    },
                    ...
                ]
        x_label: X軸ラベル
        y_label: Y軸ラベル
        ax: プロット先の軸(None の場合は新規作成)
        **kwargs: その他のオプション

    Returns:
        Axes: プロットされた軸オブジェクト
    """
    # 軸が指定されていない場合は新規作成
    created_new_figure = False
    if ax is None:
        ax = mpl_backend.create_figure(figsize=(10, 8))
        created_new_figure = True
    else:
        fig = ax.figure

    # 各曲線をプロット
    for curve_config in curves_data:
        curve_type = curve_config.get("type", "unknown")
        plot_kwargs = curve_config.get("kwargs", {}).copy()
        
        x_arr = curve_config.get("x")
        y_arr = curve_config.get("y")
        
        if x_arr is None or y_arr is None:
            print(f"Warning: Data for {curve_type} curve not found.")
            continue

        if curve_type == "original":
            # 元データのプロット
            plot_kwargs.setdefault("plot_type", "line")
            core_plot(
                x_values=x_arr,
                y_values=y_arr,
                x_label=x_label,
                y_label=y_label,
                ax=ax,
                **plot_kwargs,
            )
        else:
            # その他の曲線(スケルトン、累積など)のプロット
            mpl_backend.draw_line(x_arr, y_arr, ax=ax, **plot_kwargs)

    mpl_backend.add_legend(ax)
    mpl_backend.add_grid(ax, linestyle="--", alpha=0.7)

    # 新しい図を作成した場合のみグラフを表示
    if created_new_figure:
        mpl_backend.show_plot()

    return ax


