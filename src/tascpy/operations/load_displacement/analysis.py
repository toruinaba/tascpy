"""荷重-変位データの解析関数"""

from typing import List, Optional, Dict, Any, Tuple, Union
import numpy as np
from ...operations.registry import operation
from ...domains.load_displacement import LoadDisplacementCollection
from ...core.column import Column
from .utils import (
    get_load_column,
    get_displacement_column,
    get_load_data,
    get_displacement_data,
    get_valid_data,
)


@operation(domain="load_displacement")
def calculate_slopes(
    collection: LoadDisplacementCollection,
    result_column: Optional[str] = None,
    x_column: Optional[str] = None,
    y_column: Optional[str] = None,
) -> LoadDisplacementCollection:
    """変位と荷重の間の傾きを計算

    変位と荷重の間の点ごとの傾きを計算します。
    デフォルトでは変位列を独立変数（X軸）、荷重列を従属変数（Y軸）として使用します。

    Args:
        collection: 荷重-変位コレクション
        result_column: 結果を格納する列名
        x_column: X軸データの列名（指定がない場合は変位列を使用）
        y_column: Y軸データの列名（指定がない場合は荷重列を使用）

    Returns:
        LoadDisplacementCollection: 傾きデータを含むコレクション
    """
    # 列の特定
    if x_column is None:
        x_column = get_displacement_column(collection)
    if y_column is None:
        y_column = get_load_column(collection)

    # データ取得
    x_data = collection[x_column].values
    y_data = collection[y_column].values

    if len(x_data) != len(y_data):
        raise ValueError("XとYのデータの長さは一致する必要があります")

    if len(x_data) < 2:
        raise ValueError("2つ以上のデータポイントが必要です")

    # 傾き計算
    slopes = []
    for i in range(1, len(x_data)):
        if (
            x_data[i] is not None
            and x_data[i - 1] is not None
            and y_data[i] is not None
            and y_data[i - 1] is not None
            and x_data[i] != x_data[i - 1]
        ):  # ゼロ除算を避ける

            slope = (y_data[i] - y_data[i - 1]) / (x_data[i] - x_data[i - 1])
            slopes.append(slope)
        else:
            slopes.append(None)

    # 最初の点は傾きを計算できないのでNone
    slopes = [None] + slopes

    # 結果列名の決定
    if result_column is None:
        result_column = f"slope_{y_column}_{x_column}"

    # 結果を新しいコレクションとして作成
    result = collection.clone()

    # 単位の計算（あれば）
    y_unit = collection[y_column].unit if hasattr(collection[y_column], "unit") else ""
    x_unit = collection[x_column].unit if hasattr(collection[x_column], "unit") else ""
    slope_unit = f"{y_unit}/{x_unit}" if y_unit and x_unit else None

    result.columns[result_column] = Column(
        ch=None,  # ch パラメータを追加
        name=result_column,
        unit=slope_unit,  # unit パラメータを正しい位置に
        values=slopes,
        metadata={
            "description": f"Slope between {y_column} and {x_column}"
        },  # description を metadata に移動
    )

    return result


@operation(domain="load_displacement")
def calculate_stiffness(
    collection: LoadDisplacementCollection,
    range_start: float = 0.2,
    range_end: float = 0.8,
    method: str = "linear_regression",
) -> float:
    """荷重-変位曲線から剛性を計算

    指定された範囲内のデータを使用して荷重-変位間の剛性（傾き）を計算します。

    Args:
        collection: 荷重-変位コレクション
        range_start: 最大荷重に対する計算開始点の割合
        range_end: 最大荷重に対する計算終了点の割合
        method: 剛性計算方法 ("linear_regression" または "secant")

    Returns:
        float: 剛性値
    """
    disp_data, load_data = get_valid_data(collection)

    if len(load_data) < 2:
        raise ValueError("剛性計算に十分なデータがありません")

    # 荷重の範囲を計算
    max_load = np.max(load_data)
    start_load = max_load * range_start
    end_load = max_load * range_end

    # 指定範囲内のデータを抽出
    range_mask = (load_data >= start_load) & (load_data <= end_load)
    range_disp = disp_data[range_mask]
    range_load = load_data[range_mask]

    if len(range_load) < 2:
        raise ValueError(
            f"指定範囲 ({range_start*100}% - {range_end*100}%) に十分なデータがありません"
        )

    if method == "linear_regression":
        # 線形回帰で傾きを計算
        slope, _ = np.polyfit(range_disp, range_load, 1)
        return float(slope)

    elif method == "secant":
        # 割線法で計算
        return float(
            (range_load[-1] - range_load[0]) / (range_disp[-1] - range_disp[0])
        )

    else:
        raise ValueError(f"未対応の計算方法: {method}")


@operation(domain="load_displacement")
def find_yield_point(
    collection: LoadDisplacementCollection,
    method: str = "offset",
    offset_value: float = 0.002,
    range_start: float = 0.3,
    range_end: float = 0.7,
    factor: float = 0.33,
    result_prefix: Optional[str] = "yield",
) -> LoadDisplacementCollection:
    """降伏点を計算

    荷重-変位データから降伏点を計算します。
    オフセット法または一般降伏法から選択できます。

    Args:
        collection: 荷重-変位コレクション
        method: 計算方法 ('offset', 'general')
        offset_value: オフセット降伏法でのオフセット量
        range_start: 初期勾配計算の範囲開始（最大荷重に対する比率）
        range_end: 初期勾配計算の範囲終了（最大荷重に対する比率）
        factor: 一般降伏法での勾配比率
        result_prefix: 結果列の接頭辞

    Returns:
        LoadDisplacementCollection: 降伏点情報を含むコレクション
    """
    # 荷重と変位データの取得
    disp_column = get_displacement_column(collection)
    load_column = get_load_column(collection)

    disp_data, load_data = get_valid_data(collection)

    if len(load_data) < 3:
        raise ValueError("降伏点計算に十分なデータがありません")

    # 最大荷重と対応するインデックス
    max_load = np.max(load_data)

    # 初期勾配計算のための範囲
    lower_bound = max_load * range_start
    upper_bound = max_load * range_end

    range_mask = (load_data >= lower_bound) & (load_data <= upper_bound)
    range_disps = disp_data[range_mask]
    range_loads = load_data[range_mask]

    if len(range_loads) < 2:
        raise ValueError(
            f"指定範囲 ({range_start*100}% - {range_end*100}%) に十分なデータがありません"
        )

    # 初期勾配を計算
    initial_slope, _ = np.polyfit(range_disps, range_loads, 1)

    # 降伏点を計算（メソッドによって異なる）
    if method == "offset":
        # オフセット線: y = initial_slope * x - initial_slope * offset_value
        offset_line = initial_slope * disp_data - initial_slope * offset_value
        diff = load_data - offset_line
        print(diff)
        print(initial_slope)

        # 交点を探す（符号の変化を検出）
        for i in range(1, len(diff)):
            if diff[i - 1] * diff[i] <= 0:  # 符号が変化または一方がゼロの場合
                # 線形補間で交点を求める
                ratio = abs(diff[i - 1]) / (abs(diff[i - 1]) + abs(diff[i]))
                yield_disp = disp_data[i - 1] + ratio * (
                    disp_data[i] - disp_data[i - 1]
                )
                yield_load = initial_slope * yield_disp - initial_slope * offset_value
                break
        else:
            raise ValueError("降伏点が見つかりませんでした")

    elif method == "general":
        # 各点での傾きを計算
        slopes = np.gradient(load_data, disp_data)

        # 初期勾配のfactor倍以下になる点を探す
        threshold = initial_slope * factor
        yield_idx = np.where(slopes <= threshold)[0]

        if len(yield_idx) == 0:
            raise ValueError("降伏点が見つかりませんでした")

        yield_idx = yield_idx[0]  # 最初の点を使用
        yield_disp = disp_data[yield_idx]
        yield_load = load_data[yield_idx]

    else:
        raise ValueError(f"未対応の計算方法: {method}")

    # 結果オブジェクトを作成
    result = collection.clone()

    # 結果列の作成
    yield_disp_col = f"{result_prefix}_displacement"
    yield_load_col = f"{result_prefix}_load"

    # メタデータに降伏点情報を追加
    if "analysis" not in result.metadata:
        result.metadata["analysis"] = {}

    result.metadata["analysis"]["yield_point"] = {
        "method": method,
        "displacement": float(yield_disp),
        "load": float(yield_load),
        "initial_slope": float(initial_slope),
        "parameters": {
            "offset_value": offset_value,
            "range_start": range_start,
            "range_end": range_end,
            "factor": factor,
        },
    }

    # 単一値の結果カラムを作成
    result.columns[yield_disp_col] = Column(
        ch=None,  # ch パラメータを追加
        name=yield_disp_col,
        unit=(
            collection[disp_column].unit
            if hasattr(collection[disp_column], "unit")
            else None
        ),
        values=[yield_disp],
        metadata={
            "description": f"Yield displacement ({method} method)"
        },  # description を metadata に移動
    )

    result.columns[yield_load_col] = Column(
        ch=None,  # ch パラメータを追加
        name=yield_load_col,
        unit=(
            collection[load_column].unit
            if hasattr(collection[load_column], "unit")
            else None
        ),
        values=[yield_load],
        metadata={
            "description": f"Yield load ({method} method)"
        },  # description を metadata に移動
    )

    return result
