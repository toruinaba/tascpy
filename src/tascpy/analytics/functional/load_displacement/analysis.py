"""荷重-変位データ解析用の純粋関数群"""

from typing import Any, Dict, NamedTuple, Tuple

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
    disp = np.asarray(disp_data, dtype=float)
    load = np.asarray(load_data, dtype=float)
    if len(disp) != len(load):
        raise ValueError("変位と荷重データの長さは一致する必要があります")
    if len(disp) < 2:
        raise ValueError("2つ以上のデータポイントが必要です")

    d_disp = np.diff(disp)
    with np.errstate(divide="ignore", invalid="ignore"):
        slopes = np.where(d_disp != 0, np.diff(load) / d_disp, np.nan)
    return np.concatenate([[np.nan], slopes])


def _peak_load(load_data: np.ndarray) -> float:
    """絶対値が最大の荷重（符号付き）"""
    return float(load_data[np.argmax(np.abs(load_data))])


def compute_stiffness(
    disp_data: np.ndarray,
    load_data: np.ndarray,
    range_start: float = 0.2,
    range_end: float = 0.8,
    method: str = "linear_regression"
) -> float:
    """指定範囲における剛性（傾き）を計算します。

    Args:
        disp_data: 変位データの配列
        load_data: 荷重データの配列
        range_start: 最大荷重に対する計算開始点の割合
        range_end: 最大荷重に対する計算終了点の割合
        method: 計算方法 ("linear_regression" または "secant")

    最大荷重は絶対値が最大の荷重（符号付き）です。圧縮側（負の荷重）のデータでも同じように計算できます。

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
    disp_data = np.asarray(disp_data, dtype=float)
    load_data = np.asarray(load_data, dtype=float)
    valid_mask = ~(np.isnan(disp_data) | np.isnan(load_data))
    disp_data = disp_data[valid_mask]
    load_data = load_data[valid_mask]

    if len(load_data) < 2:
        raise ValueError("剛性計算に十分なデータがありません")

    lower, upper = sorted((_peak_load(load_data) * range_start, _peak_load(load_data) * range_end))
    range_mask = (load_data >= lower) & (load_data <= upper)
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
    """オフセット法による降伏点の計算（オフセットの向きは最大荷重の符号に合わせる）"""
    offset_amount = initial_slope * offset_value * np.sign(_peak_load(load_data))
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


class YieldPoint(NamedTuple):
    """降伏点の計算結果（タプルとして (is_valid, displacement, load, info) に分解できる）

    info には常に method・initial_slope（求められなければ NaN）・parameters が入り、
    失敗時は error、成功時は手法ごとの診断情報（diff_stats / slopes_stats など）も入ります。
    """

    is_valid: bool
    displacement: float
    load: float
    info: Dict[str, Any]


YIELD_METHODS = ("offset", "general")


def compute_yield_point(
    disp_data: np.ndarray,
    load_data: np.ndarray,
    method: str = "offset",
    offset_value: float = 0.002,
    range_start: float = 0.1,
    range_end: float = 0.3,
    factor: float = 0.33,
    fail_silently: bool = False,
) -> YieldPoint:
    """降伏点を計算します

    初期剛性を最大荷重（絶対値が最大の荷重）の range_start〜range_end の範囲から求め、
    "offset" は初期剛性線を offset_value だけ平行移動した直線との交点、
    "general" は接線剛性が初期剛性 × factor を下回る点を降伏点とします。

    Args:
        fail_silently: True なら計算できない場合も例外にせず、is_valid=False と info["error"] を返す

    Raises:
        ValueError: method が未知の場合、または fail_silently=False で計算できない場合
    """
    if method not in YIELD_METHODS:
        raise ValueError(f"未知の降伏点の計算方法です: {method}（{', '.join(YIELD_METHODS)} のいずれか）")
    parameters = {"range_start": range_start, "range_end": range_end,
                  **({"offset_value": offset_value} if method == "offset" else {"factor": factor})}
    info: Dict[str, Any] = {"method": method, "initial_slope": np.nan, "parameters": parameters}

    disp = np.asarray(disp_data, dtype=float)
    load = np.asarray(load_data, dtype=float)
    valid = ~(np.isnan(disp) | np.isnan(load))
    disp, load = disp[valid], load[valid]

    try:
        initial_slope = compute_stiffness(disp, load, range_start=range_start, range_end=range_end)
        if not np.isfinite(initial_slope):
            raise ValueError("初期剛性(initial_slope)が NaN または Inf となりました。")
        info["initial_slope"] = initial_slope
        if method == "offset":
            is_valid, x, y, details = compute_yield_point_offset(disp, load, initial_slope, offset_value)
        else:
            is_valid, x, y, details = compute_yield_point_general(disp, load, initial_slope, factor)
    except ValueError as e:
        if not fail_silently:
            raise
        return YieldPoint(False, np.nan, np.nan, {**info, "error": str(e)})
    return YieldPoint(is_valid, x, y, {**details, **info})
