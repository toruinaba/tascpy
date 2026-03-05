"""荷重-変位データ解析用の純粋関数群"""

from typing import Tuple, Dict, Any, List, Optional
import numpy as np


def compute_slopes(disp_data: np.ndarray, load_data: np.ndarray) -> np.ndarray:
    """変位と荷重の間の点ごとの傾きを計算します。
    
    Args:
        disp_data: 変位データの配列
        load_data: 荷重データの配列
        
    Returns:
        np.ndarray: 計算された傾きの配列（最初の要素は NaN）
        
    Examples:
        >>> from tascpy.analytics.functional.load_displacement.analysis import compute_slopes
        >>> import numpy as np
        >>> disp = np.array([0, 1, 2, 4])
        >>> load = np.array([0, 10, 20, 30])
        >>> compute_slopes(disp, load)
        array([nan, 10., 10.,  5.])
    """
    if len(disp_data) != len(load_data):
        raise ValueError("変位と荷重データの長さは一致する必要があります")
    if len(disp_data) < 2:
        raise ValueError("2つ以上のデータポイントが必要です")
        
    slopes = [np.nan]
    for i in range(1, len(disp_data)):
        if (
            disp_data[i] is not None
            and disp_data[i - 1] is not None
            and load_data[i] is not None
            and load_data[i - 1] is not None
            and disp_data[i] != disp_data[i - 1]
        ):
            slope = (load_data[i] - load_data[i - 1]) / (disp_data[i] - disp_data[i - 1])
            slopes.append(slope)
        else:
            slopes.append(np.nan)
            
    return np.array(slopes, dtype=float)


def compute_stiffness(
    disp_data: np.ndarray,
    load_data: np.ndarray,
    range_start: float = 0.2,
    range_end: float = 0.8,
    method: str = "linear_regression"
) -> float:
    """指定範囲における剛性（傾き）を計算します。

    Args:
        disp_data: 変位データの配列 (NaN/None 除去済み)
        load_data: 荷重データの配列 (NaN/None 除去済み)
        range_start: 最大荷重に対する計算開始点の割合
        range_end: 最大荷重に対する計算終了点の割合
        method: 計算方法 ("linear_regression" または "secant")

    Returns:
        float: 計算された剛性値
        
    Examples:
        >>> from tascpy.analytics.functional.load_displacement.analysis import compute_stiffness
        >>> import numpy as np
        >>> disp = np.array([0, 1, 2, 3, 4])
        >>> load = np.array([0, 100, 200, 300, 400])
        >>> compute_stiffness(disp, load, range_start=0.2, range_end=0.8)
        100.0
    """
    if len(load_data) < 2:
        raise ValueError("剛性計算に十分なデータがありません")

    max_load = np.max(load_data)
    start_load = max_load * range_start
    end_load = max_load * range_end

    range_mask = (load_data >= start_load) & (load_data <= end_load)
    range_disp = disp_data[range_mask]
    range_load = load_data[range_mask]

    if len(range_load) < 2:
        raise ValueError(f"指定範囲以内に十分なデータがありません")

    if np.ptp(range_disp) == 0:
        raise ValueError(
            "指定範囲内の変位データに変動がありません（分散ゼロ）。"
            "SVDエラーを防ぐため、事前に .ops.remove_consecutive_duplicates_across() "
            "などを実行して重複データを除去してください。"
        )

    if method == "linear_regression":
        try:
            slope, _ = np.polyfit(range_disp, range_load, 1)
            return float(slope)
        except np.linalg.LinAlgError:
            raise ValueError(
                "線形回帰(np.polyfit)でSVDエラーが発生しました。"
                "前処理で .ops.remove_consecutive_duplicates_across() を試してください。"
            )
    elif method == "secant":
        d_disp = range_disp[-1] - range_disp[0]
        if d_disp == 0:
            return float('inf')
        return float((range_load[-1] - range_load[0]) / d_disp)
    else:
        raise ValueError(f"未対応の計算方法: {method}")


def compute_yield_point_offset(
    disp_data: np.ndarray,
    load_data: np.ndarray,
    initial_slope: float,
    offset_value: float = 0.002
) -> Tuple[bool, float, float, Dict[str, Any]]:
    """オフセット法による降伏点の計算"""
    offset_amount = initial_slope * offset_value
    offset_line = initial_slope * disp_data - offset_amount
    diff = load_data - offset_line
    
    debug_info = {
        "offset_value": offset_value,
        "offset_amount": float(offset_amount),
        "diff_stats": {
            "min": float(np.min(diff)),
            "max": float(np.max(diff)),
            "mean": float(np.mean(diff)),
            "has_sign_change": bool(any(diff[i - 1] * diff[i] <= 0 for i in range(1, len(diff)))),
        },
    }
    
    for i in range(1, len(diff)):
        if diff[i - 1] * diff[i] <= 0:
            ratio = abs(diff[i - 1]) / (abs(diff[i - 1]) + abs(diff[i]))
            yield_disp = disp_data[i - 1] + ratio * (disp_data[i] - disp_data[i - 1])
            yield_load = load_data[i - 1] + ratio * (load_data[i] - load_data[i - 1])
            return True, float(yield_disp), float(yield_load), debug_info
            
    return False, np.nan, np.nan, debug_info


def compute_yield_point_general(
    disp_data: np.ndarray,
    load_data: np.ndarray,
    initial_slope: float,
    factor: float = 0.33
) -> Tuple[bool, float, float, Dict[str, Any]]:
    """一般降伏法による降伏点の計算"""
    # np.gradientは同じx座標が連続するとゼロ除算エラーになるため、重複を排除
    diff_disp = np.diff(disp_data)
    unique_mask = np.insert(diff_disp != 0, 0, True)

    if not np.any(unique_mask) or np.sum(unique_mask) < 2:
        raise ValueError(
            "変位データがすべて同じか、勾配計算に十分な変動がありません。"
            "事前に .ops.remove_consecutive_duplicates_across() を実行してください。"
        )

    unique_disp = disp_data[unique_mask]
    unique_load = load_data[unique_mask]

    slopes = np.gradient(unique_load, unique_disp)
    threshold = initial_slope * factor
    
    debug_info = {
        "factor": factor,
        "threshold": float(threshold),
        "slopes_stats": {
            "min": float(np.min(slopes)),
            "max": float(np.max(slopes)),
            "mean": float(np.mean(slopes)),
        }
    }
    
    yield_idx = np.where(slopes <= threshold)[0]
    if len(yield_idx) > 0:
        idx = yield_idx[0]
        # 元の配列インデックスではなく、重複排除後のインデックスから値を取得
        return True, float(unique_disp[idx]), float(unique_load[idx]), debug_info
        
    return False, np.nan, np.nan, debug_info


def compute_yield_point(
    disp_data: np.ndarray,
    load_data: np.ndarray,
    method: str = "offset",
    offset_value: float = 0.002,
    range_start: float = 0.1,
    range_end: float = 0.3,
    factor: float = 0.33,
    debug_mode: bool = False,
    fail_silently: bool = False,
) -> Tuple[bool, float, float, Dict[str, Any]]:
    try:
        initial_slope = compute_stiffness(
            disp_data, load_data, range_start=range_start, range_end=range_end
        )
    except ValueError as e:
        if fail_silently:
            return False, np.nan, np.nan, {"error": str(e), "method": method}
        raise

    if np.isnan(initial_slope) or np.isinf(initial_slope):
        err_msg = "初期剛性(initial_slope)が NaN または Inf となりました。"
        if fail_silently:
            return False, np.nan, np.nan, {"error": err_msg, "method": method}
        raise ValueError(err_msg)
    if method == "offset":
        res_tuple = compute_yield_point_offset(disp_data, load_data, initial_slope, offset_value)
    elif method == "general":
        res_tuple = compute_yield_point_general(disp_data, load_data, initial_slope, factor)
    else:
        if fail_silently:
            return False, np.nan, np.nan, {"error": f"Unknown method: {method}", "method": method, "initial_slope": initial_slope}
        raise ValueError(f"Unknown yield calculation method: {method}")

    is_valid, x, y, debug_info = res_tuple
    debug_info["method"] = method
    debug_info["initial_slope"] = initial_slope
    
    if method == "offset":
        debug_info["parameters"] = {"offset_value": offset_value, "range_start": range_start, "range_end": range_end}
    elif method == "general":
        debug_info["parameters"] = {"factor": factor, "range_start": range_start, "range_end": range_end}

    return is_valid, x, y, debug_info
