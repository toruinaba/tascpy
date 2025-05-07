"""荷重-変位データのプロット関数"""

from typing import Optional, Dict, Any, Tuple, List, Union
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from ...domains.load_displacement import LoadDisplacementCollection
from ...operations.registry import operation
from .utils import get_load_column, get_displacement_column, get_valid_data


@operation(domain="load_displacement")
def plot_load_displacement(
    collection: LoadDisplacementCollection, ax: Optional[Axes] = None, **kwargs
) -> Tuple[Figure, Axes]:
    """荷重-変位曲線をプロットする

    Args:
        collection: 荷重-変位コレクション
        ax: プロット先の軸（Noneの場合は新規作成）
        **kwargs: matplotlibのplot関数に渡す追加引数

    Returns:
        Tuple[Figure, Axes]: プロットのfigureとaxesオブジェクト
    """
    # 軸が指定されていない場合は新規作成
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
    else:
        fig = ax.figure

    # 荷重と変位データの取得
    disp_column = get_displacement_column(collection)
    load_column = get_load_column(collection)

    disp_data, load_data = get_valid_data(collection)

    # 基本プロット
    ax.plot(disp_data, load_data, **kwargs)

    # 軸ラベルの設定
    disp_unit = (
        collection[disp_column].unit if hasattr(collection[disp_column], "unit") else ""
    )
    load_unit = (
        collection[load_column].unit if hasattr(collection[load_column], "unit") else ""
    )

    ax.set_xlabel(f"{disp_column} [{disp_unit}]" if disp_unit else disp_column)
    ax.set_ylabel(f"{load_column} [{load_unit}]" if load_unit else load_column)

    return fig, ax


@operation(domain="load_displacement")
def plot_yield_point(
    collection: LoadDisplacementCollection,
    ax: Optional[Axes] = None,
    plot_original_data: bool = True,
    plot_initial_slope: bool = True,
    plot_offset_line: bool = True,
    result_prefix: str = "yield",
    **kwargs,
) -> Tuple[Figure, Axes]:
    """降伏点解析結果をプロットする

    Args:
        collection: 降伏点情報を含む荷重-変位コレクション
        ax: プロット先の軸（Noneの場合は新規作成）
        plot_original_data: 元の荷重-変位データをプロットするかどうか
        plot_initial_slope: 初期勾配線をプロットするかどうか
        plot_offset_line: オフセット線をプロットするかどうか（オフセット法の場合）
        result_prefix: 降伏点データの接頭辞
        **kwargs: matplotlibのplot関数に渡す追加引数

    Returns:
        Tuple[Figure, Axes]: プロットのfigureとaxesオブジェクト
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
        fig, ax = plot_load_displacement(
            collection, ax=ax, label="Load-Displacement Data", **kwargs
        )
    else:
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 6))
        else:
            fig = ax.figure

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
        y_vals = initial_slope * x_vals - initial_slope * offset_value * max_disp
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

    return fig, ax


@operation(domain="load_displacement")
def plot_yield_analysis_details(
    collection: LoadDisplacementCollection, ax: Optional[Axes] = None, **kwargs
) -> Tuple[Figure, Axes]:
    """降伏点解析の詳細情報をプロット

    Args:
        collection: 降伏点情報を含む荷重-変位コレクション
        ax: プロット先の軸（Noneの場合は新規作成）
        **kwargs: matplotlibのplot関数に渡す追加引数

    Returns:
        Tuple[Figure, Axes]: プロットのfigureとaxesオブジェクト
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
    fig, ax = plot_yield_point(collection, ax=ax, **kwargs)

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

    return fig, ax


@operation(domain="load_displacement")
def compare_yield_methods(
    collection: LoadDisplacementCollection,
    methods: List[Dict[str, Any]] = None,
    ax: Optional[Axes] = None,
    **kwargs,
) -> Tuple[Figure, Axes]:
    """複数の降伏点計算方法を比較してプロット

    Args:
        collection: 荷重-変位コレクション
        methods: 計算方法とパラメータのリスト。例:
                 [{"method": "offset", "offset_value": 0.002},
                  {"method": "general", "factor": 0.33}]
        ax: プロット先の軸（Noneの場合は新規作成）
        **kwargs: プロット関数に渡す追加引数

    Returns:
        Tuple[Figure, Axes]: プロットのfigureとaxesオブジェクト
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
            y_vals = initial_slope * x_vals - initial_slope * offset_value * max_disp
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

    return fig, ax
