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
from ...visualization import backend_mpl as mpl_backend


@operation(domain="load_displacement")
def plot_load_displacement(
    collection: LoadDisplacementCollection, ax: Optional[Axes] = None, **kwargs
) -> Axes:
    """荷重-変位曲線をプロットします

    荷重-変位データを二次元グラフとしてプロットします。
    既存の軸オブジェクトを指定することも、新しく作成することもできます。

    Args:
        collection: 荷重-変位コレクション
        ax: プロット先の軸（None の場合は新規作成）
        **kwargs: matplotlib の plot 関数に渡す追加引数

    Returns:
        Axes: プロットされた軸オブジェクト
    """
    # 荷重と変位のカラムを取得
    disp_column = collection.displacement_column
    load_column = collection.load_column

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
) -> Axes:
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
        Axes: プロットされた軸オブジェクト

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
    orig_load_column = collection.load_column
    orig_disp_column = collection.displacement_column

    curve_data = collection.results["skeleton_curve"].to_dict()["data"]
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

    return ax


@operation(domain="load_displacement")
def plot_cumulative_curve(
    collection: LoadDisplacementCollection,
    plot_original: bool = True,
    cumulative_load_column: Optional[str] = None,
    cumulative_disp_column: Optional[str] = None,
    ax: Optional[Axes] = None,
    original_kwargs: Optional[Dict[str, Any]] = None,
    cumulative_kwargs: Optional[Dict[str, Any]] = None,
) -> Axes:
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
        Axes: プロットされた軸オブジェクト

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
    orig_load_column = collection.load_column
    orig_disp_column = collection.displacement_column

    # collection.results から曲線データを取得
    curve_data = collection.results["cumulative_curve"].to_dict()["data"]
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

    return ax


@operation(domain="load_displacement")
def plot_yield_point(
    collection: LoadDisplacementCollection,
    ax: Optional[Axes] = None,
    plot_original_data: bool = True,
    plot_initial_slope: bool = True,
    plot_offset_line: bool = True,
    result_prefix: str = "yield",
    **kwargs,
) -> Axes:
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
        Axes: プロットされた軸オブジェクト
    """
    # 降伏点の存在確認
    if "yield_point" not in collection.results:
        raise ValueError("コレクションに降伏点の解析結果が含まれていません")

    yield_point = collection.results["yield_point"]
    yield_data = yield_point.metadata
    method = yield_data.get("method", "unknown")
    initial_slope = yield_data.get("initial_slope", 1.0)

    # 軸が指定されていない場合は新規作成
    created_new_figure = False
    if ax is None:
        ax = mpl_backend.create_figure(figsize=(8, 6))
        created_new_figure = True
    else:
        fig = ax.figure

    # 元の荷重変位データをプロット
    if plot_original_data:
        plot_load_displacement(
            collection, ax=ax, label="Load-Displacement Data", **kwargs
        )
    else:
        # プロットしない場合でも、後続の処理のためにaxをcollectionに関連付けるなどの処理が必要な場合はここで行う
        # ただし、現在の実装では単にプロットするだけなので、何もしなくて良い
        pass

    # 荷重と変位データの取得
    disp_data, load_data = collection.valid_data

    # 降伏点のプロット
    yield_disp = yield_point.x
    yield_load = yield_point.y

    mpl_backend.scatter_points(
        [yield_disp],
        [yield_load],
        ax=ax,
        color="red",
        s=80,
        marker="o",
        label=f"Yield Point ({method})",
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
    if method == "offset" and plot_offset_line:
        offset_value = yield_data["parameters"]["offset_value"]
        mpl_backend.draw_axline(
            ax=ax,
            xy1=(offset_value, 0), slope=initial_slope, color="blue", linestyle="--"
        )

    # 一般降伏法の場合は勾配変化点の視覚化
    if method == "general":
        factor = yield_data["parameters"]["factor"]
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



@operation(domain="load_displacement")
def plot_yield_analysis_details(
    collection: LoadDisplacementCollection, ax: Optional[Axes] = None, **kwargs
) -> Axes:
    """降伏点解析の詳細情報をプロットします

    find_yield_point 関数で解析した降伏点情報の詳細をビジュアル化します。
    初期勾配の計算範囲などの追加情報も表示します。

    Args:
        collection: 降伏点情報を含む荷重-変位コレクション
        ax: プロット先の軸（None の場合は新規作成）
        **kwargs: matplotlib の plot 関数に渡す追加引数

    Returns:
        Axes: プロットされた軸オブジェクト
    """
    # 降伏点の確認
    if "yield_point" not in collection.results:
        raise ValueError("コレクションに降伏点の解析結果が含まれていません")

    yield_point = collection.results["yield_point"]
    yield_data = yield_point.metadata
    method = yield_data.get("method", "unknown")

    # プロット作成
    plot_yield_point(collection, ax=ax, **kwargs)

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
    disp_data, load_data = collection.valid_data

    range_start = yield_data["parameters"]["range_start"]
    range_end = yield_data["parameters"]["range_end"]
    max_load = np.max(load_data)

    lower_bound = max_load * range_start
    upper_bound = max_load * range_end

    range_mask = (load_data >= lower_bound) & (load_data <= upper_bound)
    range_disps = disp_data[range_mask]
    range_loads = load_data[range_mask]

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
    title_text = f"Yield Point Analysis ({method.capitalize()} Method)"
    mpl_backend.set_labels(ax, title=title_text)

    # 降伏点情報のテキスト表示
    info_text = (
        f"Yield Point:\n"
        f"  Displacement: {yield_point.x:.4f}\n"
        f"  Load: {yield_point.y:.4f}\n"
        f"  Initial Slope: {yield_data.get('initial_slope', 0):.4f}"
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



@operation(domain="load_displacement")
def compare_yield_methods(
    collection: LoadDisplacementCollection,
    methods: List[Dict[str, Any]] = None,
    ax: Optional[Axes] = None,
    **kwargs,
) -> Axes:
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
        Axes: プロットされた軸オブジェクト
    """
    from ...operations.load_displacement.analysis import find_yield_point

    if methods is None:
        methods = [
            {
                "method": "offset",
                "offset_value": 0.002,
            },
            {"method": "general", "factor": 0.33},
        ]

    # 軸が指定されていない場合は新規作成
    created_new_figure = False
    if ax is None:
        ax = mpl_backend.create_figure(figsize=(10, 8))
        created_new_figure = True
    else:
        fig = ax.figure

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

        if "result_prefix" in params_copy:
            del params_copy["result_prefix"]

        # 降伏点計算
        result = find_yield_point(collection, **params_copy)

        # 降伏点のプロット
        yield_point = result.results.get("yield_point")
        if not yield_point:
            continue
            
        yield_data = yield_point.metadata
        yield_disp = yield_point.x
        yield_load = yield_point.y

        method_name = params["method"].capitalize()
        if params["method"] == "offset":
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
        initial_slope = yield_data.get("initial_slope", 1.0)
        max_disp = np.max(collection[collection.displacement_column].values)
        x_vals = np.array([0, max_disp])

        if params["method"] == "offset":
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


@operation(domain="load_displacement")
def plot_multiple_curves(
    collection: LoadDisplacementCollection,
    curves: List[Dict[str, Any]],
    ax: Optional[Axes] = None,
    **kwargs,
) -> Axes:
    """複数の曲線を指定してプロットします

    Args:
        collection: 荷重-変位コレクション
        curves: プロットする曲線の設定リスト
                [
                    {"type": "original", "kwargs": {...}},
                    {"type": "skeleton", "kwargs": {...}},
                    {"type": "cumulative", "kwargs": {...}}
                ]
        ax: プロット先の軸（None の場合は新規作成）
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
    for curve_config in curves:
        curve_type = curve_config.get("type")
        plot_kwargs = curve_config.get("kwargs", {}).copy()

        if curve_type == "original":
            # 元データのプロット
            orig_load_column = collection.load_column
            orig_disp_column = collection.displacement_column
            plot_kwargs.setdefault("plot_type", "line")
            core_plot(
                collection,
                x_column=orig_disp_column,
                y_column=orig_load_column,
                ax=ax,
                **plot_kwargs,
            )

        elif curve_type == "skeleton":
            # スケルトン曲線のプロット
            if "skeleton_curve" in collection.results:
                curve_data = collection.results["skeleton_curve"].to_dict()["data"]
                mpl_backend.draw_line(curve_data["x"], curve_data["y"], ax=ax, **plot_kwargs)
            else:
                print("Warning: Skeleton curve data not found.")

        elif curve_type == "cumulative":
            # 累積曲線のプロット
            if "cumulative_curve" in collection.results:
                curve_data = collection.results["cumulative_curve"].to_dict()["data"]
                mpl_backend.draw_line(curve_data["x"], curve_data["y"], ax=ax, **plot_kwargs)
            else:
                print("Warning: Cumulative curve data not found.")

    mpl_backend.add_legend(ax)
    mpl_backend.add_grid(ax, linestyle="--", alpha=0.7)

    # 新しい図を作成した場合のみグラフを表示
    if created_new_figure:
        mpl_backend.show_plot()

    return ax


