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
    range_start: float = 0.1,  # 0.3から0.1に変更して、より初期段階のデータを使用
    range_end: float = 0.3,  # 0.7から0.3に変更して、線形領域内に収める
    factor: float = 0.33,
    result_prefix: Optional[str] = "yield",
    debug_mode: bool = False,  # デバッグモードフラグを追加
    fail_silently: bool = False,  # エラー時に例外を発生させずに結果を返すかどうか
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
        debug_mode: 詳細な計算過程情報を出力するかどうか
        fail_silently: 降伏点が見つからない場合に例外を発生させずに情報を返すかどうか

    Returns:
        LoadDisplacementCollection: 降伏点情報または計算過程情報を含むコレクション

    Raises:
        ValueError: 降伏点が見つかりず、fail_silently=False の場合
    """
    # 荷重と変位データの取得
    disp_column = get_displacement_column(collection)
    load_column = get_load_column(collection)

    disp_data, load_data = get_valid_data(collection)

    if len(load_data) < 3:
        raise ValueError("降伏点計算に十分なデータがありません")

    # 結果オブジェクトを作成
    result = collection.clone()

    # デバッグ情報を格納する辞書
    debug_info = {
        "method": method,
        "parameters": {
            "offset_value": offset_value,
            "range_start": range_start,
            "range_end": range_end,
            "factor": factor,
        },
        "data_stats": {
            "min_load": float(np.min(load_data)),
            "max_load": float(np.max(load_data)),
            "min_disp": float(np.min(disp_data)),
            "max_disp": float(np.max(disp_data)),
            "data_points": len(load_data),
        },
    }

    # 最大荷重と対応するインデックス
    max_load = np.max(load_data)

    # 初期勾配計算のための範囲
    lower_bound = max_load * range_start
    upper_bound = max_load * range_end

    range_mask = (load_data >= lower_bound) & (load_data <= upper_bound)
    range_disps = disp_data[range_mask]
    range_loads = load_data[range_mask]

    if len(range_loads) < 2:
        error_msg = f"指定範囲 ({range_start*100}% - {range_end*100}%) に十分なデータがありません"
        if debug_mode:
            print(error_msg)
            print(f"データ範囲: 荷重={lower_bound:.2f}～{upper_bound:.2f}")
            print(f"該当するデータ点数: {len(range_loads)}")

        # 範囲不足のデバッグ情報を追加
        debug_info["error"] = error_msg
        debug_info["data_range"] = {
            "lower_bound": float(lower_bound),
            "upper_bound": float(upper_bound),
            "num_points_in_range": len(range_loads),
        }

        # 失敗情報をメタデータに保存
        if "analysis" not in result.metadata:
            result.metadata["analysis"] = {}

        result.metadata["analysis"]["yield_point_calculation"] = {
            "status": "failed",
            "reason": error_msg,
            "debug_info": debug_info,
        }

        if fail_silently:
            # 失敗を示す結果列の作成
            result.columns[f"{result_prefix}_calculation_failed"] = Column(
                ch=None,
                name=f"{result_prefix}_calculation_failed",
                unit=None,
                values=[True],
                metadata={"description": f"降伏点計算に失敗 ({method} method)"},
            )
            return result
        else:
            raise ValueError(error_msg)

    # 初期勾配を計算
    # 直線の方程式 y = mx + b で、mが初期勾配
    initial_slope, intercept = np.polyfit(range_disps, range_loads, 1)

    # R²（決定係数）を計算して、線形回帰の品質を確認
    y_pred = initial_slope * range_disps + intercept
    ss_total = np.sum((range_loads - np.mean(range_loads)) ** 2)
    ss_residual = np.sum((range_loads - y_pred) ** 2)
    r_squared = 1 - (ss_residual / ss_total) if ss_total != 0 else 0

    # デバッグ情報に初期勾配情報を追加
    debug_info["initial_slope"] = float(initial_slope)
    debug_info["intercept"] = float(intercept)
    debug_info["r_squared"] = float(r_squared)
    debug_info["data_range"] = {
        "range_start": range_start,
        "range_end": range_end,
        "lower_bound": float(lower_bound),
        "upper_bound": float(upper_bound),
        "num_points_in_range": len(range_loads),
    }

    # R²が低い場合（例: 0.95未満）は警告またはより狭い範囲を試みる
    if r_squared < 0.95:
        warning_msg = (
            f"警告: 初期勾配計算の線形回帰の品質が低いです (R² = {r_squared:.3f})"
        )
        if debug_mode:
            print(warning_msg)

        debug_info["warnings"] = [warning_msg]

        # より低い範囲でもう一度試してみる
        narrower_upper = min(0.2, range_end)
        if narrower_upper > range_start:
            narrower_mask = (load_data >= lower_bound) & (
                load_data <= max_load * narrower_upper
            )
            if np.sum(narrower_mask) >= 2:
                narrower_disps = disp_data[narrower_mask]
                narrower_loads = load_data[narrower_mask]
                narrower_slope, narrower_intercept = np.polyfit(
                    narrower_disps, narrower_loads, 1
                )

                # 狭い範囲での情報をデバッグ情報に追加
                debug_info["narrower_range"] = {
                    "upper_bound": float(max_load * narrower_upper),
                    "num_points": int(np.sum(narrower_mask)),
                    "slope": float(narrower_slope),
                }

                # 元の結果と比較して、大きく異なる場合は狭い範囲を使用
                if abs(narrower_slope - initial_slope) / initial_slope > 0.1:
                    initial_slope = narrower_slope
                    intercept = narrower_intercept
                    info_msg = f"より狭い範囲 (0-{narrower_upper*100}%) での初期勾配を使用します: {initial_slope:.3f}"
                    if debug_mode:
                        print(info_msg)

                    if "info" not in debug_info:
                        debug_info["info"] = []
                    debug_info["info"].append(info_msg)
                    debug_info["initial_slope_updated"] = True

    try:
        # 降伏点を計算（メソッドによって異なる）
        if method == "offset":
            # オフセット線: y = initial_slope * x - initial_slope * offset_value * max(disp_data)
            offset_amount = initial_slope * offset_value
            offset_line = initial_slope * disp_data - offset_amount
            diff = load_data - offset_line

            # オフセット法特有の情報をデバッグ情報に追加
            debug_info["offset_method"] = {
                "offset_value": offset_value,
                "offset_amount": float(offset_amount),
                "diff_stats": {
                    "min": float(np.min(diff)),
                    "max": float(np.max(diff)),
                    "mean": float(np.mean(diff)),
                    "has_sign_change": any(
                        diff[i - 1] * diff[i] <= 0 for i in range(1, len(diff))
                    ),
                },
            }

            # 評価ポイントのサンプルを追加
            sample_indices = np.linspace(
                0, len(disp_data) - 1, min(20, len(disp_data)), dtype=int
            )
            evaluation_points = []
            for idx in sample_indices:
                evaluation_points.append(
                    {
                        "index": int(idx),
                        "displacement": float(disp_data[idx]),
                        "load": float(load_data[idx]),
                        "offset_line_value": float(offset_line[idx]),
                        "difference": float(diff[idx]),
                    }
                )
            debug_info["offset_method"]["evaluation_points"] = evaluation_points

            # 交点を探す（符号の変化を検出）
            found_yield_point = False
            for i in range(1, len(diff)):
                if diff[i - 1] * diff[i] <= 0:  # 符号が変化または一方がゼロの場合
                    # 線形補間で交点を求める
                    ratio = abs(diff[i - 1]) / (abs(diff[i - 1]) + abs(diff[i]))
                    yield_disp = disp_data[i - 1] + ratio * (
                        disp_data[i] - disp_data[i - 1]
                    )
                    yield_load = load_data[i - 1] + ratio * (
                        load_data[i] - load_data[i - 1]
                    )
                    found_yield_point = True

                    # 交点情報をデバッグ情報に追加
                    debug_info["yield_point"] = {
                        "found": True,
                        "displacement": float(yield_disp),
                        "load": float(yield_load),
                        "intersection_indices": [int(i - 1), int(i)],
                        "intersection_ratio": float(ratio),
                    }
                    break

            if not found_yield_point:
                error_msg = "オフセット線と荷重-変位曲線の交点が見つかりませんでした"

                if debug_mode:
                    print(f"エラー: {error_msg}")
                    print(
                        f"オフセット線の差分範囲: {np.min(diff):.2f} ～ {np.max(diff):.2f}"
                    )
                    print(
                        f"符号変化の有無: {'あり' if any(diff[i-1] * diff[i] <= 0 for i in range(1, len(diff))) else 'なし'}"
                    )

                    # 評価ポイントの一部を表示
                    print("\n評価ポイント一覧（抜粋）:")
                    print("インデックス, 変位, 荷重, オフセット線値, 差分")
                    for i in range(0, len(disp_data), max(1, len(disp_data) // 10)):
                        print(
                            f"{i}, {disp_data[i]:.5f}, {load_data[i]:.2f}, {offset_line[i]:.2f}, {diff[i]:.2f}"
                        )

                debug_info["yield_point"] = {"found": False}
                debug_info["error"] = error_msg

                # 失敗情報をメタデータに保存
                if "analysis" not in result.metadata:
                    result.metadata["analysis"] = {}

                result.metadata["analysis"]["yield_point_calculation"] = {
                    "status": "failed",
                    "reason": error_msg,
                    "debug_info": debug_info,
                }

                if fail_silently:
                    # 失敗を示す結果列の作成
                    result.columns[f"{result_prefix}_calculation_failed"] = Column(
                        ch=None,
                        name=f"{result_prefix}_calculation_failed",
                        unit=None,
                        values=[True],
                        metadata={"description": f"降伏点計算に失敗 ({method} method)"},
                    )
                    return result
                else:
                    raise ValueError(error_msg)

        elif method == "general":
            # 各点での傾きを計算
            slopes = np.gradient(load_data, disp_data)

            # 一般降伏法特有の情報をデバッグ情報に追加
            debug_info["general_method"] = {
                "factor": factor,
                "threshold": float(initial_slope * factor),
                "slopes_stats": {
                    "min": float(np.min(slopes)),
                    "max": float(np.max(slopes)),
                    "mean": float(np.mean(slopes)),
                },
            }

            # サンプルの勾配データをデバッグ情報に追加
            sample_indices = np.linspace(
                0, len(disp_data) - 1, min(20, len(disp_data)), dtype=int
            )
            slope_samples = []
            for idx in sample_indices:
                slope_samples.append(
                    {
                        "index": int(idx),
                        "displacement": float(disp_data[idx]),
                        "load": float(load_data[idx]),
                        "slope": float(slopes[idx]),
                    }
                )
            debug_info["general_method"]["slope_samples"] = slope_samples

            # 初期勾配のfactor倍以下になる点を探す
            threshold = initial_slope * factor
            yield_idx = np.where(slopes <= threshold)[0]

            if len(yield_idx) == 0:
                error_msg = f"降伏点が見つかりませんでした（初期勾配の{factor*100}%以下になる点がありません）"

                if debug_mode:
                    print(f"エラー: {error_msg}")
                    print(f"初期勾配: {initial_slope:.2f}")
                    print(f"閾値: {threshold:.2f}")
                    print(f"最小勾配: {np.min(slopes):.2f}")

                    # 勾配データの一部を表示
                    print("\n勾配データ一覧（抜粋）:")
                    print("インデックス, 変位, 荷重, 勾配")
                    for i in range(0, len(disp_data), max(1, len(disp_data) // 10)):
                        print(
                            f"{i}, {disp_data[i]:.5f}, {load_data[i]:.2f}, {slopes[i]:.2f}"
                        )

                debug_info["yield_point"] = {"found": False}
                debug_info["error"] = error_msg

                # 失敗情報をメタデータに保存
                if "analysis" not in result.metadata:
                    result.metadata["analysis"] = {}

                result.metadata["analysis"]["yield_point_calculation"] = {
                    "status": "failed",
                    "reason": error_msg,
                    "debug_info": debug_info,
                }

                if fail_silently:
                    # 失敗を示す結果列の作成
                    result.columns[f"{result_prefix}_calculation_failed"] = Column(
                        ch=None,
                        name=f"{result_prefix}_calculation_failed",
                        unit=None,
                        values=[True],
                        metadata={"description": f"降伏点計算に失敗 ({method} method)"},
                    )
                    return result
                else:
                    raise ValueError(error_msg)

            yield_idx = yield_idx[0]  # 最初の点を使用
            yield_disp = disp_data[yield_idx]
            yield_load = load_data[yield_idx]

            # 降伏点情報をデバッグ情報に追加
            debug_info["yield_point"] = {
                "found": True,
                "displacement": float(yield_disp),
                "load": float(yield_load),
                "index": int(yield_idx),
                "slope_at_point": float(slopes[yield_idx]),
            }

        else:
            error_msg = f"未対応の計算方法: {method}"
            debug_info["error"] = error_msg

            if fail_silently:
                # 失敗を示す結果列の作成
                result.columns[f"{result_prefix}_calculation_failed"] = Column(
                    ch=None,
                    name=f"{result_prefix}_calculation_failed",
                    unit=None,
                    values=[True],
                    metadata={"description": f"降伏点計算に失敗 (未対応のメソッド)"},
                )

                # 失敗情報をメタデータに保存
                if "analysis" not in result.metadata:
                    result.metadata["analysis"] = {}

                result.metadata["analysis"]["yield_point_calculation"] = {
                    "status": "failed",
                    "reason": error_msg,
                    "debug_info": debug_info,
                }

                return result
            else:
                raise ValueError(error_msg)

        # 成功情報をメタデータに追加
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

        # デバッグ情報も保存
        result.metadata["analysis"]["yield_point_calculation"] = {
            "status": "success",
            "debug_info": debug_info,
        }

        # 単一値の結果カラムを作成
        result.columns[f"{result_prefix}_displacement"] = Column(
            ch=None,
            name=f"{result_prefix}_displacement",
            unit=(
                collection[disp_column].unit
                if hasattr(collection[disp_column], "unit")
                else None
            ),
            values=[yield_disp],
            metadata={"description": f"Yield displacement ({method} method)"},
        )

        result.columns[f"{result_prefix}_load"] = Column(
            ch=None,
            name=f"{result_prefix}_load",
            unit=(
                collection[load_column].unit
                if hasattr(collection[load_column], "unit")
                else None
            ),
            values=[yield_load],
            metadata={"description": f"Yield load ({method} method)"},
        )

        return result

    except Exception as e:
        # 予期せぬエラーの場合
        error_msg = f"降伏点計算中にエラーが発生しました: {str(e)}"

        if debug_mode:
            print(f"エラー: {error_msg}")
            import traceback

            traceback.print_exc()

        debug_info["error"] = error_msg

        # 失敗情報をメタデータに保存
        if "analysis" not in result.metadata:
            result.metadata["analysis"] = {}

        result.metadata["analysis"]["yield_point_calculation"] = {
            "status": "failed",
            "reason": error_msg,
            "debug_info": debug_info,
        }

        if fail_silently:
            # 失敗を示す結果列の作成
            result.columns[f"{result_prefix}_calculation_failed"] = Column(
                ch=None,
                name=f"{result_prefix}_calculation_failed",
                unit=None,
                values=[True],
                metadata={"description": f"降伏点計算に失敗 (エラー発生)"},
            )
            return result
        else:
            raise
