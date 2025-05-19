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

from ...domains.load_displacement import LoadDisplacementCollection
from ...operations.registry import operation
from ...operations.core.plot import plot as core_plot
from .utils import get_load_column, get_displacement_column, get_valid_data
from .curves import get_curve_data, list_available_curves


@operation(domain="load_displacement")
def plot_load_displacement(
    collection: LoadDisplacementCollection, ax: Optional[Axes] = None, **kwargs
) -> LoadDisplacementCollection:
    """荷重-変位曲線をプロットします

    荷重-変位データを二次元グラフとしてプロットします。
    既存の軸オブジェクトを指定することも、新しく作成することもできます。

    Args:
        collection: 荷重-変位コレクション
        ax: プロット先の軸（None の場合は新規作成）
        **kwargs: matplotlib の plot 関数に渡す追加引数

    Returns:
        LoadDisplacementCollection: 元の荷重-変位コレクション
    """
    # 荷重と変位のカラムを取得
    disp_column = get_displacement_column(collection)
    load_column = get_load_column(collection)

    # コアモジュールのplot関数を使用
    plot_kwargs = kwargs.copy()
    plot_kwargs.setdefault("plot_type", "line")  # デフォルトで線グラフ

    # core_plotを呼び出す
    return core_plot(
        collection, x_column=disp_column, y_column=load_column, ax=ax, **plot_kwargs
    )


@operation(domain="load_displacement")
def plot_skeleton_curve(
    collection: LoadDisplacementCollection,
    plot_original: bool = True,
    skeleton_load_column: Optional[str] = None,
    skeleton_disp_column: Optional[str] = None,
    ax: Optional[Axes] = None,
    original_kwargs: Optional[Dict[str, Any]] = None,
    skeleton_kwargs: Optional[Dict[str, Any]] = None,
) -> LoadDisplacementCollection:
    """スケルトン曲線をプロットします

    create_skeleton_curve 関数で作成したスケルトン曲線をプロットします。
    元の荷重-変位データと比較して表示することも可能です。

    スケルトン曲線データは、列または metadata["curves"]["skeleton_curve"] から取得します。
    メタデータに格納されている場合はそちらが優先されます。

    Args:
        collection: スケルトン曲線を含む荷重-変位コレクション
        plot_original: 元の荷重-変位データもプロットするかどうか
        skeleton_load_column: スケルトン曲線の荷重列名（None の場合は自動検出）
        skeleton_disp_column: スケルトン曲線の変位列名（None の場合は自動検出）
        ax: プロット先の軸（None の場合は新規作成）
        original_kwargs: 元データプロット用の追加引数
        skeleton_kwargs: スケルトン曲線プロット用の追加引数

    Returns:
        LoadDisplacementCollection: 元の荷重-変位コレクション

    Raises:
        ValueError: スケルトン曲線データが列にもメタデータにも見つからない場合
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

    # 元のデータの列名
    orig_load_column = get_load_column(collection)
    orig_disp_column = get_displacement_column(collection)

    curve_data = get_curve_data(collection, "skeleton_curve")
    skeleton_x = curve_data["x"]
    skeleton_y = curve_data["y"]

    # 元のデータをプロット
    if plot_original:
        # core_plotを使用して元データをプロット
        plot_kwargs = original_kwargs.copy()
        plot_kwargs.setdefault("plot_type", "line")
        core_plot(
            collection,
            x_column=orig_disp_column,
            y_column=orig_load_column,
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

    return collection


@operation(domain="load_displacement")
def plot_cumulative_curve(
    collection: LoadDisplacementCollection,
    plot_original: bool = True,
    cumulative_load_column: Optional[str] = None,
    cumulative_disp_column: Optional[str] = None,
    ax: Optional[Axes] = None,
    original_kwargs: Optional[Dict[str, Any]] = None,
    cumulative_kwargs: Optional[Dict[str, Any]] = None,
) -> LoadDisplacementCollection:
    """累積曲線をプロットします

    create_cumulative_curve 関数で作成した累積曲線をプロットします。
    元の荷重-変位データと比較して表示することも可能です。

    累積曲線データは、列または metadata["curves"]["cumulative_curve"] から取得します。
    メタデータに格納されている場合はそちらが優先されます。

    Args:
        collection: 累積曲線を含む荷重-変位コレクション
        plot_original: 元の荷重-変位データもプロットするかどうか
        cumulative_load_column: 累積曲線の荷重列名（None の場合は自動検出）
        cumulative_disp_column: 累積曲線の変位列名（None の場合は自動検出）
        ax: プロット先の軸（None の場合は新規作成）
        original_kwargs: 元データプロット用の追加引数
        cumulative_kwargs: 累積曲線プロット用の追加引数

    Returns:
        LoadDisplacementCollection: 元の荷重-変位コレクション

    Raises:
        ValueError: 累積曲線データが列にもメタデータにも見つからない場合
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

    # 元のデータの列名
    orig_load_column = get_load_column(collection)
    orig_disp_column = get_displacement_column(collection)

    # 累積曲線データの取得
    # get_curve_data関数でメタデータから曲線データを取得
    curve_data = get_curve_data(collection, "cumulative_curve")
    cumulative_x = curve_data["x"]
    cumulative_y = curve_data["y"]

    # 元のデータをプロット
    if plot_original:
        # core_plotを使用して元データをプロット
        plot_kwargs = original_kwargs.copy()
        plot_kwargs.setdefault("plot_type", "line")
        core_plot(
            collection,
            x_column=orig_disp_column,
            y_column=orig_load_column,
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

    return collection


@operation(domain="load_displacement")
def plot_yield_point(
    collection: LoadDisplacementCollection,
    ax: Optional[Axes] = None,
    plot_original_data: bool = True,
    plot_initial_slope: bool = True,
    plot_offset_line: bool = True,
    result_prefix: str = "yield",
    **kwargs,
) -> LoadDisplacementCollection:
    """降伏点解析結果をプロットします

    find_yield_point 関数で解析した降伏点情報をビジュアル化します。
    元データ、初期勾配線、オフセット線などを表示できます。

    Args:
        collection: 降伏点情報を含む荷重-変位コレクション
        ax: プロット先の軸（None の場合は新規作成）
        plot_original_data: 元の荷重-変位データもプロットするかどうか
        plot_initial_slope: 初期勾配線をプロットするかどうか
        plot_offset_line: オフセット線をプロットするかどうか（オフセット法の場合）
        result_prefix: 降伏点データの接頭辞
        **kwargs: matplotlib の plot 関数に渡す追加引数

    Returns:
        LoadDisplacementCollection: 元の荷重-変位コレクション
    """
    # 降伏点のメタデータ確認
    if (
        "analysis" not in collection.metadata
        or "yield_point" not in collection.metadata["analysis"]
    ):
        raise ValueError("コレクションに降伏点の解析結果が含まれていません")

    yield_data = collection.metadata["analysis"]["yield_point"]
    method = yield_data["method"]
    initial_slope = yield_data["initial_slope"]

    # 元データプロット
    if plot_original_data:
        # 元の荷重変位データをプロットし、コレクションとaxを取得
        collection = plot_load_displacement(
            collection, ax=ax, label="Load-Displacement Data", **kwargs
        )
        # 使用されたaxオブジェクトを取得
        if ax is None:
            # 新しくplot_load_displacementが作成したaxを見つける必要がある
            fig = plt.gcf()  # 現在のfigureを取得
            ax = fig.axes[0]  # 最初のaxesを取得
            created_new_figure = True
        else:
            fig = ax.figure
            created_new_figure = False
    else:
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 6))
            created_new_figure = True
        else:
            fig = ax.figure
            created_new_figure = False

    # 荷重と変位データの取得
    disp_data, load_data = get_valid_data(collection)

    # 降伏点のプロット
    yield_disp = yield_data["displacement"]
    yield_load = yield_data["load"]

    ax.scatter(
        [yield_disp],
        [yield_load],
        color="red",
        s=80,
        marker="o",
        label=f"Yield Point ({method})",
        zorder=5,
    )

    # 初期勾配線のプロット
    if plot_initial_slope:
        max_disp = np.max(disp_data)
        x_vals = np.array([0, max_disp])
        y_vals = initial_slope * x_vals
        ax.plot(
            x_vals, y_vals, "g--", label=f"Initial Slope: {initial_slope:.2f}", zorder=3
        )

    # オフセット法の場合はオフセット線も表示
    if method == "offset" and plot_offset_line:
        offset_value = yield_data["parameters"]["offset_value"]
        max_disp = np.max(disp_data)
        x_vals = np.array([0, max_disp])
        y_vals = initial_slope * x_vals - initial_slope * offset_value
        ax.plot(x_vals, y_vals, "b--", label=f"Offset Line ({offset_value})", zorder=2)

    # 一般降伏法の場合は勾配変化点の視覚化
    if method == "general":
        factor = yield_data["parameters"]["factor"]
        # 接線を表示
        tangent_length = yield_disp * 0.5
        x_vals = np.array([yield_disp - tangent_length, yield_disp + tangent_length])
        tangent_slope = initial_slope * factor
        y_vals = tangent_slope * (x_vals - yield_disp) + yield_load
        ax.plot(
            x_vals, y_vals, "m--", label=f"Tangent ({factor:.2f}×Initial)", zorder=4
        )

    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.7)

    # 新しい図を作成した場合のみグラフを表示
    if created_new_figure:
        plt.show()

    return collection


@operation(domain="load_displacement")
def plot_yield_analysis_details(
    collection: LoadDisplacementCollection, ax: Optional[Axes] = None, **kwargs
) -> LoadDisplacementCollection:
    """降伏点解析の詳細情報をプロットします

    find_yield_point 関数で解析した降伏点情報の詳細をビジュアル化します。
    初期勾配の計算範囲などの追加情報も表示します。

    Args:
        collection: 降伏点情報を含む荷重-変位コレクション
        ax: プロット先の軸（None の場合は新規作成）
        **kwargs: matplotlib の plot 関数に渡す追加引数

    Returns:
        LoadDisplacementCollection: 元の荷重-変位コレクション
    """
    # 降伏点のメタデータ確認
    if (
        "analysis" not in collection.metadata
        or "yield_point" not in collection.metadata["analysis"]
    ):
        raise ValueError("コレクションに降伏点の解析結果が含まれていません")

    yield_data = collection.metadata["analysis"]["yield_point"]
    method = yield_data["method"]

    # プロット作成
    collection = plot_yield_point(collection, ax=ax, **kwargs)

    # 使用されたaxオブジェクトを取得
    if ax is None:
        # 新しくplot_yield_pointが作成したaxを見つける必要がある
        fig = plt.gcf()  # 現在のfigureを取得
        ax = fig.axes[0]  # 最初のaxesを取得
        created_new_figure = True
    else:
        fig = ax.figure
        created_new_figure = False

    # 初期勾配計算に使用した範囲をハイライト
    disp_data, load_data = get_valid_data(collection)

    range_start = yield_data["parameters"]["range_start"]
    range_end = yield_data["parameters"]["range_end"]
    max_load = np.max(load_data)

    lower_bound = max_load * range_start
    upper_bound = max_load * range_end

    range_mask = (load_data >= lower_bound) & (load_data <= upper_bound)
    range_disps = disp_data[range_mask]
    range_loads = load_data[range_mask]

    ax.scatter(
        range_disps,
        range_loads,
        color="cyan",
        s=40,
        alpha=0.7,
        label=f"Initial Slope Range ({range_start:.2f}-{range_end:.2f})",
        zorder=4,
    )

    # 方法に応じた追加情報の表示
    title_text = f"Yield Point Analysis ({method.capitalize()} Method)"
    ax.set_title(title_text)

    # 降伏点情報のテキスト表示
    info_text = (
        f"Yield Point:\n"
        f"  Displacement: {yield_data['displacement']:.4f}\n"
        f"  Load: {yield_data['load']:.4f}\n"
        f"  Initial Slope: {yield_data['initial_slope']:.4f}"
    )

    # テキストボックスで情報表示
    props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
    ax.text(
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
        plt.show()

    return collection


@operation(domain="load_displacement")
def compare_yield_methods(
    collection: LoadDisplacementCollection,
    methods: List[Dict[str, Any]] = None,
    ax: Optional[Axes] = None,
    **kwargs,
) -> LoadDisplacementCollection:
    """複数の降伏点計算方法を比較してプロットします

    異なるパラメータや手法で計算した複数の降伏点を
    一つのグラフ上に表示して比較できます。

    Args:
        collection: 荷重-変位コレクション
        methods: 計算方法とパラメータのリスト。例:
                 [{"method": "offset", "offset_value": 0.002},
                  {"method": "general", "factor": 0.33}]
        ax: プロット先の軸（None の場合は新規作成）
        **kwargs: プロット関数に渡す追加引数

    Returns:
        LoadDisplacementCollection: 元の荷重-変位コレクション
    """
    from ...operations.load_displacement.analysis import find_yield_point

    if methods is None:
        methods = [
            {
                "method": "offset",
                "offset_value": 0.002,
                "result_prefix": "yield_offset",
            },
            {"method": "general", "factor": 0.33, "result_prefix": "yield_general"},
        ]

    # 軸が指定されていない場合は新規作成
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))
        created_new_figure = True
    else:
        fig = ax.figure
        created_new_figure = False

    # 元データプロット
    plot_load_displacement(
        collection,
        ax=ax,
        label="Load-Displacement Data",
        color="black",
        alpha=0.7,
        **kwargs,
    )

    # 各方法で降伏点を計算してプロット
    colors = ["red", "blue", "green", "purple", "orange"]

    for i, params in enumerate(methods):
        color = colors[i % len(colors)]
        params_copy = params.copy()  # パラメータのコピーを作成して変更

        # 降伏点計算
        result = find_yield_point(collection, **params_copy)

        # 降伏点のプロット
        yield_data = result.metadata["analysis"]["yield_point"]
        yield_disp = yield_data["displacement"]
        yield_load = yield_data["load"]

        method_name = params["method"].capitalize()
        if params["method"] == "offset":
            method_label = f"{method_name} ({params.get('offset_value', 0.002)})"
        else:
            method_label = f"{method_name} (factor={params.get('factor', 0.33)})"

        ax.scatter(
            [yield_disp],
            [yield_load],
            color=color,
            s=80,
            marker="o",
            label=f"{method_label}",
            zorder=5 + i,
        )

        # 初期勾配線
        initial_slope = yield_data["initial_slope"]
        max_disp = np.max(collection[get_displacement_column(collection)].values)
        x_vals = np.array([0, max_disp])

        if params["method"] == "offset":
            # オフセット線も表示
            offset_value = params.get("offset_value", 0.002)
            y_vals = initial_slope * x_vals - initial_slope * offset_value
            ax.plot(
                x_vals,
                y_vals,
                "--",
                color=color,
                alpha=0.6,
                label=f"Offset Line ({offset_value})",
                zorder=2 + i,
            )

    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.7)
    ax.set_title("Comparison of Yield Point Methods")

    # 新しい図を作成した場合のみグラフを表示
    if created_new_figure:
        plt.show()

    return collection
