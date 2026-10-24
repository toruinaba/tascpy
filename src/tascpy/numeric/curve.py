"""x-y 曲線の解析（傾き・剛性・降伏点・ピーク・面積）の純粋関数

荷重-変位（x: 変位, y: 荷重）や応力-ひずみ（x: ひずみ, y: 応力）など、任意の x-y 曲線に使えます。
"""

from typing import Any, Dict, NamedTuple, Optional, Tuple

import numpy as np


def compute_slopes(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """隣り合う点の間の傾き dy/dx を計算します。

    Args:
        x: x の配列（変位など）
        y: y の配列（荷重など）

    Returns:
        np.ndarray: 傾きの配列（最初の要素と、x が変化しない区間は NaN）

    Examples:
        >>> from tascpy.numeric.curve import compute_slopes
        >>> import numpy as np
        >>> compute_slopes(np.array([0, 1, 2, 4]), np.array([0, 10, 20, 30]))
        array([nan, 10., 10.,  5.])
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) != len(y):
        raise ValueError("x と y の長さは一致する必要があります")
    if len(x) < 2:
        raise ValueError("2つ以上のデータポイントが必要です")

    dx = np.diff(x)
    with np.errstate(divide="ignore", invalid="ignore"):
        slopes = np.where(dx != 0, np.diff(y) / dx, np.nan)
    return np.concatenate([[np.nan], slopes])


def _peak(y: np.ndarray) -> float:
    """絶対値が最大の y（符号付き）"""
    return float(y[np.argmax(np.abs(y))])


def compute_stiffness(
    x: np.ndarray,
    y: np.ndarray,
    range_start: float = 0.2,
    range_end: float = 0.8,
    method: str = "linear_regression",
) -> float:
    """y が最大値の range_start〜range_end 倍の範囲にある点から、剛性（傾き）を計算します。

    最大値は絶対値が最大の y（符号付き）です。圧縮側（負の y）のデータでも同じように計算できます。

    単調な曲線を前提にしています。繰り返し載荷のデータを渡すと、範囲に入る除荷途中の点も計算に含まれ、
    エラーにならずに誤った値になります。最初の載荷区間やスケルトン曲線（`hysteresis.compute_skeleton_curve`）に使ってください。

    Args:
        x: x の配列（変位など）
        y: y の配列（荷重など）
        range_start: 最大値に対する範囲の開始の割合
        range_end: 最大値に対する範囲の終了の割合
        method: "linear_regression"（最小二乗の傾き）または "secant"（範囲の両端を結ぶ傾き）

    Returns:
        float: 剛性

    Examples:
        >>> from tascpy.numeric.curve import compute_stiffness
        >>> import numpy as np
        >>> compute_stiffness(np.array([0, 1, 2, 3, 4]), np.array([0, 100, 200, 300, 400]))
        100.0
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    valid = ~(np.isnan(x) | np.isnan(y))
    x, y = x[valid], y[valid]

    if len(y) < 2:
        raise ValueError("剛性計算に十分なデータがありません")

    lower, upper = sorted((_peak(y) * range_start, _peak(y) * range_end))
    in_range = (y >= lower) & (y <= upper)
    range_x, range_y = x[in_range], y[in_range]

    if len(range_y) < 2:
        raise ValueError("指定範囲以内に十分なデータがありません")

    if np.ptp(range_x) == 0:
        raise ValueError(
            "指定範囲内の x に変動がありません（分散ゼロ）。"
            "SVDエラーを防ぐため、事前に .ops.remove_consecutive_duplicates_across() "
            "などを実行して重複データを除去してください。"
        )

    if method == "linear_regression":
        try:
            slope, _ = np.polyfit(range_x, range_y, 1)
            return float(slope)
        except np.linalg.LinAlgError:
            raise ValueError(
                "線形回帰(np.polyfit)でSVDエラーが発生しました。"
                "前処理で .ops.remove_consecutive_duplicates_across() を試してください。"
            )
    elif method == "secant":
        dx = range_x[-1] - range_x[0]
        if dx == 0:
            return float("inf")
        return float((range_y[-1] - range_y[0]) / dx)
    else:
        raise ValueError(f"未対応の計算方法: {method}")


def _yield_point_offset(
    x: np.ndarray, y: np.ndarray, initial_slope: float, offset_value: float
) -> Tuple[bool, float, float, Dict[str, Any]]:
    """オフセット法による降伏点（オフセットの向きは最大値の符号に合わせる）"""
    offset_amount = initial_slope * offset_value * np.sign(_peak(y))
    offset_line = initial_slope * x - offset_amount
    diff = y - offset_line

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
            yield_x = x[i - 1] + ratio * (x[i] - x[i - 1])
            yield_y = y[i - 1] + ratio * (y[i] - y[i - 1])
            return True, float(yield_x), float(yield_y), debug_info

    return False, np.nan, np.nan, debug_info


def _yield_point_general(
    x: np.ndarray, y: np.ndarray, initial_slope: float, factor: float
) -> Tuple[bool, float, float, Dict[str, Any]]:
    """一般降伏法による降伏点"""
    # np.gradient は同じ x が連続するとゼロ除算になるため、重複を除く
    unique_mask = np.insert(np.diff(x) != 0, 0, True)

    if not np.any(unique_mask) or np.sum(unique_mask) < 2:
        raise ValueError(
            "x がすべて同じか、勾配計算に十分な変動がありません。"
            "事前に .ops.remove_consecutive_duplicates_across() を実行してください。"
        )

    unique_x = x[unique_mask]
    unique_y = y[unique_mask]

    slopes = np.gradient(unique_y, unique_x)
    threshold = initial_slope * factor

    debug_info = {
        "factor": factor,
        "threshold": float(threshold),
        "slopes_stats": {
            "min": float(np.min(slopes)),
            "max": float(np.max(slopes)),
            "mean": float(np.mean(slopes)),
        },
    }

    yield_idx = np.where(slopes <= threshold)[0]
    if len(yield_idx) > 0:
        idx = yield_idx[0]
        return True, float(unique_x[idx]), float(unique_y[idx]), debug_info

    return False, np.nan, np.nan, debug_info


class YieldPoint(NamedTuple):
    """降伏点の計算結果（タプルとして (is_valid, x, y, info) に分解できる）

    info には常に method・initial_slope（求められなければ NaN）・parameters が入り、
    失敗時は error、成功時は手法ごとの診断情報（diff_stats / slopes_stats など）も入ります。
    """

    is_valid: bool
    x: float
    y: float
    info: Dict[str, Any]


YIELD_METHODS = ("offset", "general")


def compute_yield_point(
    x: np.ndarray,
    y: np.ndarray,
    method: str = "offset",
    offset_value: float = 0.002,
    range_start: float = 0.1,
    range_end: float = 0.3,
    factor: float = 0.33,
    fail_silently: bool = False,
) -> YieldPoint:
    """降伏点を計算します

    単調な曲線を前提にしています（`compute_stiffness` と同じ）。繰り返し載荷のデータではスケルトン曲線に使ってください。

    初期剛性を `compute_stiffness(x, y, range_start, range_end)` で求め、
    "offset" は初期剛性線を x 方向に offset_value だけ平行移動した直線との交点、
    "general" は接線剛性が初期剛性 × factor を下回る最初の点を降伏点とします。

    Args:
        x: x の配列（変位・ひずみなど）
        y: y の配列（荷重・応力など）
        method: "offset" または "general"
        offset_value: オフセット量（x の単位。0.2% オフセットなら 0.002）
        range_start: 初期剛性を求める範囲の開始（最大値に対する割合）
        range_end: 初期剛性を求める範囲の終了（最大値に対する割合）
        factor: 一般降伏法のしきい値の係数
        fail_silently: True なら計算できない場合も例外にせず、is_valid=False と info["error"] を返す

    Raises:
        ValueError: method が未知の場合、または fail_silently=False で計算できない場合

    Examples:
        >>> from tascpy.numeric.curve import compute_yield_point
        >>> import numpy as np
        >>> strain = np.array([0.0, 0.001, 0.002, 0.004, 0.006])
        >>> stress = np.array([0.0, 200.0, 400.0, 440.0, 450.0])
        >>> point = compute_yield_point(strain, stress, range_start=0.0, range_end=0.9)
        >>> round(point.x, 4), round(point.y, 1)
        (0.0042, 441.0)
    """
    if method not in YIELD_METHODS:
        raise ValueError(f"未知の降伏点の計算方法です: {method}（{', '.join(YIELD_METHODS)} のいずれか）")
    parameters = {"range_start": range_start, "range_end": range_end,
                  **({"offset_value": offset_value} if method == "offset" else {"factor": factor})}
    info: Dict[str, Any] = {"method": method, "initial_slope": np.nan, "parameters": parameters}

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    valid = ~(np.isnan(x) | np.isnan(y))
    x, y = x[valid], y[valid]

    try:
        initial_slope = compute_stiffness(x, y, range_start=range_start, range_end=range_end)
        if not np.isfinite(initial_slope):
            raise ValueError("初期剛性(initial_slope)が NaN または Inf となりました。")
        info["initial_slope"] = initial_slope
        if method == "offset":
            is_valid, yield_x, yield_y, details = _yield_point_offset(x, y, initial_slope, offset_value)
        else:
            is_valid, yield_x, yield_y, details = _yield_point_general(x, y, initial_slope, factor)
    except ValueError as e:
        if not fail_silently:
            raise
        return YieldPoint(False, np.nan, np.nan, {**info, "error": str(e)})
    return YieldPoint(is_valid, yield_x, yield_y, {**details, **info})


def compute_polygon_area(x: np.ndarray, y: np.ndarray) -> float:
    """頂点 (x, y) を順に結んだ多角形の面積を計算します（靴紐の公式、3点未満は 0）

    Examples:
        >>> from tascpy.numeric.curve import compute_polygon_area
        >>> import numpy as np
        >>> compute_polygon_area(np.array([0, 1, 1, 0]), np.array([0, 0, 1, 1]))
        1.0
    """
    if len(x) < 3 or len(y) < 3:
        return 0.0
    return 0.5 * float(np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1))))


def compute_peaks_and_valleys(
    values: np.ndarray,
    distance: int = 1,
    threshold: Optional[float] = None,
) -> np.ndarray:
    """配列内の極大値(1)と極小値(-1)を検出します。

    Args:
        values: 対象の配列（欠損は NaN）
        distance: 前後 distance 点の中で最大（最小）である点だけを残す
        threshold: 隣接点との差がこれ未満のピーク（バレー）は除く

    Returns:
        np.ndarray: ピーク(1)、バレー(-1)、その他(0)のフラグ配列

    Examples:
        >>> from tascpy.numeric.curve import compute_peaks_and_valleys
        >>> import numpy as np
        >>> compute_peaks_and_valleys(np.array([0, 2, 1, 0, -1, -2, -1, 0]))
        array([ 0,  1,  0,  0,  0, -1,  0,  0])
    """
    v = np.asarray(values, dtype=float)
    n = len(v)
    flags = np.zeros(n, dtype=int)
    dist = max(1, distance)

    for i in range(1, n - 1):
        if np.isnan(v[i]):
            continue

        if v[i] > v[i - 1] and v[i] > v[i + 1]:
            is_peak = not np.any(v[max(0, i - dist):i] >= v[i])
            if is_peak:
                is_peak = not np.any(v[i + 1:min(n, i + dist + 1)] >= v[i])
            if is_peak and threshold is not None:
                if v[i] - min(v[max(0, i - 1)], v[min(n - 1, i + 1)]) < threshold:
                    is_peak = False
            if is_peak:
                flags[i] = 1

        if v[i] < v[i - 1] and v[i] < v[i + 1]:
            is_valley = not np.any(v[max(0, i - dist):i] <= v[i])
            if is_valley:
                is_valley = not np.any(v[i + 1:min(n, i + dist + 1)] <= v[i])
            if is_valley and threshold is not None:
                if max(v[max(0, i - 1)], v[min(n - 1, i + 1)]) - v[i] < threshold:
                    is_valley = False
            if is_valley:
                flags[i] = -1

    return flags
