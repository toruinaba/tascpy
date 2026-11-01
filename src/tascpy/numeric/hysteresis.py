"""繰り返し載荷の荷重-変位曲線（サイクル・履歴エネルギー・割線剛性・スケルトン曲線・累積曲線）の純粋関数

引数はすべて (displacement, load) の順で、曲線を返す関数は (変位, 荷重) の順の配列を返します。
"""

from typing import List, Literal, NamedTuple, Optional, Tuple, Union, overload

import numpy as np

from .curve import compute_polygon_area, compute_stiffness


def compute_cycle_markers(values: np.ndarray, step: float = 0.5) -> np.ndarray:
    """値の符号反転からサイクル番号を数えます。

    0 と欠損（NaN）は符号を持たない点として飛ばし、直前の有効な値と符号が変わった位置で
    step だけ数を進めます（step=0.5 なら正負の往復で 1 サイクル）。サイクル番号は 1 から始まります。

    Args:
        values: 符号の反転を見る配列（通常は荷重。欠損は NaN または None）
        step: 符号反転1回あたりの増分

    Returns:
        np.ndarray: サイクル番号の配列（整数）

    Examples:
        >>> from tascpy.numeric.hysteresis import compute_cycle_markers
        >>> import numpy as np
        >>> compute_cycle_markers(np.array([10, 5, -5, -10, 5, 10]), step=0.5)
        array([1, 1, 1, 1, 2, 2])
        >>> compute_cycle_markers(np.array([10, 0, -10, np.nan, 10]), step=0.5)
        array([1, 1, 1, 1, 2])
    """
    sign = np.nan_to_num(np.sign(np.asarray(values, dtype=float)))
    nonzero = np.flatnonzero(sign)
    flips = np.zeros(len(sign))
    flips[nonzero[1:]] = sign[nonzero[1:]] != sign[nonzero[:-1]]
    return np.floor(1 + step * np.cumsum(flips)).astype(int)


def compute_reversal_indices(values: np.ndarray, ratio: float = 0.05, min_amplitude: float = 0.0) -> np.ndarray:
    """値の向きが反転する点（正側・負側の極値）の位置を求めます。

    直前の反転点（最初は先頭の点）からの片振幅を amplitude としたとき、それまでの極値から
    amplitude × ratio 以上戻った時点で反転を確定し、その極値の位置を反転点とします。
    戻り量を振幅に対する比率で見るため、振幅が漸増する載荷でも小振幅の反転を拾えます。

    片振幅が min_amplitude に届かない間は反転とみなしません（載荷の立ち上がりのノイズ除け）。
    その間に反対向きへ進んだ場合は、反転点を作らずに向きだけを切り替えます。
    欠損（NaN）は飛ばします。先頭と末尾の点は反転点に含みません。

    Args:
        values: 反転を見る配列（通常は変位。欠損は NaN または None）
        ratio: 反転を確定する戻り量の、片振幅に対する比率（0 以上）
        min_amplitude: 反転とみなす最小の片振幅（values の単位。0 以上）

    Returns:
        np.ndarray: 反転点の位置（昇順の整数配列）

    Raises:
        ValueError: ratio または min_amplitude が負の場合

    Examples:
        >>> from tascpy.numeric.hysteresis import compute_reversal_indices
        >>> import numpy as np
        >>> compute_reversal_indices(np.array([0, 1, 2, 1, 0, -1, -2, -1, 0, 2, 4]))
        array([2, 6])

        小さな戻り（2 → 1.95）は振幅 2 の 5% 未満なので反転とみなしません。

        >>> compute_reversal_indices(np.array([0, 1, 2, 1.95, 2.5, 0, -2]), ratio=0.05)
        array([4])
    """
    if ratio < 0:
        raise ValueError(f"ratio は 0 以上にしてください: {ratio}")
    if min_amplitude < 0:
        raise ValueError(f"min_amplitude は 0 以上にしてください: {min_amplitude}")
    v = np.asarray(values, dtype=float)
    valid = np.flatnonzero(~np.isnan(v))
    reversals: List[int] = []
    if len(valid) == 0:
        return np.array(reversals, dtype=int)

    anchor = v[valid[0]]
    extreme, extreme_index, direction = anchor, int(valid[0]), 0.0
    for i in valid[1:]:
        value = v[i]
        if direction == 0:
            if value != anchor:
                direction, extreme, extreme_index = np.sign(value - anchor), value, int(i)
            continue
        if (value - extreme) * direction > 0:
            extreme, extreme_index = value, int(i)
            continue
        amplitude = abs(extreme - anchor)
        retreat = abs(extreme - value)
        if amplitude >= min_amplitude and retreat > 0 and retreat >= ratio * amplitude:
            reversals.append(extreme_index)
            anchor, direction = extreme, -direction
            extreme, extreme_index = value, int(i)
        elif amplitude < min_amplitude and (value - anchor) * direction < 0:
            direction, extreme, extreme_index = -direction, value, int(i)
    return np.array(reversals, dtype=int)


Direction = Literal["both", "positive", "negative"]
DIRECTIONS = ("both", "positive", "negative")


def compute_plastic_deformation(
    displacement: np.ndarray,
    load: np.ndarray,
    *,
    range_start: float = 0.1,
    range_end: float = 0.3,
    direction: Direction = "both",
) -> np.ndarray:
    """1つの載荷区間（反転点から次の反転点までなど）の、始点からの塑性変形を各点について求めます。

    始点（最初の有効な点）を原点とした Δd, ΔP と、その範囲の剛性 K
    （`compute_stiffness(Δd, ΔP, range_start, range_end)`。原点を移した曲線の `compute_yield_point` の初期剛性と同じ）から、
    載荷の向き s（Δd の絶対値が最大の点の符号）への塑性変形 s·(Δd − ΔP/K) を求め、それまでの最大値（負なら 0）を返します。
    値は始点で 0 で、単調に増えます。オフセット法の降伏点では、オフセット量に等しくなります。

    Args:
        displacement: 変位の配列（区間の分）
        load: 荷重の配列（区間の分）
        range_start: 剛性を求める範囲の開始（ΔP の最大値に対する割合）
        range_end: 剛性を求める範囲の終了（ΔP の最大値に対する割合）
        direction: "both"、または "positive" / "negative"（載荷の向きが異なる区間は 0）

    Returns:
        np.ndarray: 各点の塑性変形（変位の単位。荷重・変位が欠損の点は NaN）

    Raises:
        ValueError: direction が未知の場合、または剛性を求められない場合

    Examples:
        剛性 10・降伏荷重 10 の完全弾塑性のばねを、荷重 -10 の状態から +3 まで載荷します。

        >>> from tascpy.numeric.hysteresis import compute_plastic_deformation
        >>> import numpy as np
        >>> disp = np.array([-2.0, -1.0, 0.0, 1.0, 3.0])
        >>> load = np.array([-10.0, 0.0, 10.0, 10.0, 10.0])
        >>> compute_plastic_deformation(disp, load, range_start=0.0, range_end=0.6)
        array([0., 0., 0., 1., 3.])
        >>> compute_plastic_deformation(disp, load, range_start=0.0, range_end=0.6, direction="negative")
        array([0., 0., 0., 0., 0.])
    """
    if direction not in DIRECTIONS:
        raise ValueError(f"direction は {' / '.join(DIRECTIONS)} のいずれかにしてください: {direction}")
    d = np.asarray(displacement, dtype=float)
    p = np.asarray(load, dtype=float)
    valid = ~(np.isnan(d) | np.isnan(p))
    result = np.where(valid, 0.0, np.nan)
    if not valid.any():
        return result
    first = int(np.flatnonzero(valid)[0])
    delta_d, delta_p = d - d[first], p - p[first]
    sign = float(np.sign(delta_d[valid][np.argmax(np.abs(delta_d[valid]))]))
    if sign == 0 or (direction != "both" and (sign > 0) != (direction == "positive")):
        return result
    stiffness = compute_stiffness(delta_d[valid], delta_p[valid], range_start=range_start, range_end=range_end)
    if not np.isfinite(stiffness) or stiffness == 0:
        raise ValueError("剛性が NaN・Inf・0 のため、塑性変形を求められません")
    plastic = np.fmax.accumulate(np.where(valid, sign * (delta_d - delta_p / stiffness), -np.inf))
    return np.where(valid, np.maximum(plastic, 0.0), np.nan)


def _valid_pairs(displacement: np.ndarray, load: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    d = np.asarray(displacement, dtype=float)
    p = np.asarray(load, dtype=float)
    if len(d) != len(p):
        raise ValueError("変位と荷重のデータ長が一致しません")
    valid = ~(np.isnan(d) | np.isnan(p))
    return d[valid], p[valid]


def compute_hysteresis_energy(
    displacement: np.ndarray,
    load: np.ndarray,
) -> Tuple[float, float, float, float, float]:
    """1サイクルの履歴ループの面積（エネルギー散逸）と、荷重・変位の最大・最小を計算します。

    1サイクル分の配列を渡します（サイクルの切り分けは `compute_cycle_markers` の番号で行います）。
    荷重・変位の両方が有効な点が3点未満なら、エネルギーは 0、最大・最小は NaN です。

    Returns:
        (エネルギー, 最大荷重, 最小荷重, 最大変位, 最小変位)

    Examples:
        >>> from tascpy.numeric.hysteresis import compute_hysteresis_energy
        >>> import numpy as np
        >>> compute_hysteresis_energy(np.array([0, 1, 2, 1, 0]), np.array([0, 100, 0, -100, 0]))
        (200.0, 100.0, -100.0, 2.0, 0.0)
    """
    d, p = _valid_pairs(displacement, load)
    if len(p) < 3:
        return (0.0, np.nan, np.nan, np.nan, np.nan)
    return (compute_polygon_area(d, p), float(p.max()), float(p.min()), float(d.max()), float(d.min()))


def compute_secant_stiffness(displacement: np.ndarray, load: np.ndarray) -> float:
    """1サイクルの割線剛性（最大荷重点と最小荷重点を結ぶ直線の傾き）を計算します。

    荷重・変位の両方が有効な点が2点未満、または2点の変位が同じなら NaN です。

    Examples:
        >>> from tascpy.numeric.hysteresis import compute_secant_stiffness
        >>> import numpy as np
        >>> compute_secant_stiffness(np.array([0, 1, 0, -1, 0]), np.array([0, 100, 0, -100, 0]))
        100.0
    """
    d, p = _valid_pairs(displacement, load)
    if len(p) < 2:
        return np.nan
    i_max, i_min = int(np.argmax(p)), int(np.argmin(p))
    delta = d[i_max] - d[i_min]
    if abs(delta) < 1e-9:
        return np.nan
    return float((p[i_max] - p[i_min]) / delta)


def _markers_or_default(load: np.ndarray, markers: Optional[np.ndarray]) -> np.ndarray:
    return compute_cycle_markers(load) if markers is None else np.asarray(markers)


def _cycle_groups(displacement: np.ndarray, load: np.ndarray,
                  markers: np.ndarray) -> Tuple[np.ndarray, List[Tuple[List[float], List[float], List[int]]]]:
    """サイクル番号（昇順）と、サイクルごとの (荷重, 変位, 元の行 index) リスト。サイクル番号が欠損の行は除く"""
    load = np.asarray(load, dtype=float)
    displacement = np.asarray(displacement, dtype=float)
    markers = np.asarray(markers, dtype=float)
    keys = np.unique(markers[~np.isnan(markers)])
    groups = []
    for k in keys:
        rows = np.flatnonzero(markers == k)
        groups.append((load[rows].tolist(), displacement[rows].tolist(), rows.tolist()))
    return keys, groups


def _extend_edge(x: List[float], y: List[float], target: float, target_type: str = "x",
                 position: str = "end") -> Tuple[float, float]:
    """端の2点を結ぶ直線を、x または y が target になる点まで延長した (x, y)（1点しかなければ水平・垂直に延長）"""
    if position == "end":
        if len(x) < 2 or len(y) < 2:
            return (target, y[-1]) if target_type == "x" else (x[-1], target)
        x1, y1, x2, y2 = x[-2], y[-2], x[-1], y[-1]
    else:
        if len(x) < 2 or len(y) < 2:
            return (target, y[0]) if target_type == "x" else (x[0], target)
        x1, y1, x2, y2 = x[0], y[0], x[1], y[1]

    if target_type == "x":
        if x1 == x2:
            return target, y1
        return target, y1 + (y2 - y1) * (target - x1) / (x2 - x1)
    if y1 == y2:
        return x1, target
    return x1 + (x2 - x1) * (target - y1) / (y2 - y1), target


Side = Literal["positive", "negative"]
SIDES = ("positive", "negative")


def _side_sign(side: str) -> float:
    if side not in SIDES:
        raise ValueError(f"side は {' / '.join(SIDES)} のいずれかにしてください: {side}")
    return 1.0 if side == "positive" else -1.0


def _on_side(func, displacement: np.ndarray, load: np.ndarray, side: str, return_index: bool, **kwargs):
    """正側の計算 func を side の側に適用する（負側は符号を反転して計算し、結果の符号を戻す）"""
    sign = _side_sign(side)
    d, p, rows = func(sign * np.asarray(displacement, dtype=float), sign * np.asarray(load, dtype=float), **kwargs)
    curve = (sign * d + 0.0, sign * p + 0.0)  # + 0.0 で -0.0 を 0.0 にする
    return (*curve, rows) if return_index else curve


@overload
def compute_skeleton_curve(
    displacement: np.ndarray, load: np.ndarray, markers: Optional[np.ndarray] = None, has_decrease: bool = False,
    decrease_type: str = "envelope", *, side: Side = "positive", return_index: Literal[False] = False,
) -> Tuple[np.ndarray, np.ndarray]: ...
@overload
def compute_skeleton_curve(
    displacement: np.ndarray, load: np.ndarray, markers: Optional[np.ndarray] = None, has_decrease: bool = False,
    decrease_type: str = "envelope", *, side: Side = "positive", return_index: Literal[True],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]: ...
def compute_skeleton_curve(
    displacement: np.ndarray,
    load: np.ndarray,
    markers: Optional[np.ndarray] = None,
    has_decrease: bool = False,
    decrease_type: str = "envelope",
    *,
    side: Side = "positive",
    return_index: bool = False,
) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """繰り返し載荷の荷重-変位曲線からスケルトン曲線を計算します。

    以下は正側（side="positive"）の説明です。負側（side="negative"）は荷重・変位の符号を反転して同じ計算をし、
    結果の符号を戻します（荷重の最小を更新した点をつなぎ、変位は負の向きにずらします）。

    最大荷重のサイクルまでは、各サイクルで荷重がそれまでの最大を更新した点をつなぎます。
    2サイクル目以降は、そのサイクルで最初に最大を更新した点が、前のサイクルまでの包絡線の終端を
    延長した直線上に来るよう変位をずらします（ずらし量はサイクルごとに1回だけ決め、1サイクル目はずらさない）。

    曲線の各点は元データのいずれかの行で、荷重はその行の値、変位はその行の値にずらし量を足したものです。

    Args:
        displacement: 変位の配列
        load: 荷重の配列
        markers: サイクル番号の配列（省略時は `compute_cycle_markers(load)`）
        has_decrease: 最大荷重のサイクル以降の減少部分も含めるか
        decrease_type: 減少部分の取り方 ('envelope', 'continuous_only', 'both')
        side: "positive"（正側）または "negative"（負側）
        return_index: 各点の元の行 index も返すか

    Returns:
        スケルトン曲線の (変位, 荷重)。return_index=True なら (変位, 荷重, 元の行 index)

    Raises:
        ValueError: decrease_type または side が未知の場合

    Examples:
        >>> from tascpy.numeric.hysteresis import compute_skeleton_curve
        >>> import numpy as np
        >>> disp = np.array([0.0, 1.0, 0.0, -1.0, 0.0, 2.0, 0.0])
        >>> load = np.array([0.0, 10.0, 0.0, -10.0, 0.0, 15.0, 0.0])
        >>> compute_skeleton_curve(disp, load)
        (array([1., 2.]), array([10., 15.]))
        >>> compute_skeleton_curve(disp, load, return_index=True)[2]
        array([1, 5])
        >>> compute_skeleton_curve(disp, load, side="negative")
        (array([-1.]), array([-10.]))
    """
    if decrease_type not in ("envelope", "continuous_only", "both"):
        raise ValueError("decrease_typeは'envelope', 'continuous_only', 'both'のいずれかである必要があります")
    return _on_side(_positive_skeleton_curve, displacement, load, side, return_index, markers=markers,
                    has_decrease=has_decrease, decrease_type=decrease_type)


def _positive_skeleton_curve(displacement: np.ndarray, load: np.ndarray, markers: Optional[np.ndarray],
                             has_decrease: bool, decrease_type: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    rows: List[int] = []
    p_ske: List[float] = []
    d_ske: List[float] = []

    def append(row: int, p: float, d: float, skip_duplicate: bool = False) -> None:
        if skip_duplicate and p_ske and p == p_ske[-1] and d == d_ske[-1]:
            return
        rows.append(row)
        p_ske.append(p)
        d_ske.append(d)

    markers = _markers_or_default(load, markers)
    keys, groups = _cycle_groups(displacement, load, markers)
    if len(keys) > 0:
        marker_arr = np.asarray(markers, dtype=float)
        has_marker = ~np.isnan(marker_arr)
        max_marker = marker_arr[has_marker][np.nanargmax(np.asarray(load, dtype=float)[has_marker])]
        p_max = 0.0
        d_offset = 0.0

        # 増加部分（最大荷重のサイクルまで）
        for key, (cycle_load, cycle_disp, cycle_rows) in zip(keys, groups):
            if key > max_marker:
                break
            d_offset = 0.0
            offset_fixed = False

            for i in range(len(cycle_load)):
                if not np.isnan(cycle_load[i]) and cycle_load[i] > p_max:
                    p_max = cycle_load[i]
                    # ずらし量はサイクルで最初に最大荷重を超えた点で、前のサイクルまでの包絡線から1回だけ決める
                    if not offset_fixed:
                        if len(p_ske) >= 2:
                            x, _ = _extend_edge(d_ske, p_ske, cycle_load[i], "y", "end")
                            d_offset = x - cycle_disp[i]
                        offset_fixed = True
                    append(cycle_rows[i], cycle_load[i], cycle_disp[i] + d_offset)

        # 減少部分（最大荷重のサイクル以降）。最大荷重のサイクルは増加部分と重なるため、直前と同じ点は追加しない
        if has_decrease:
            for key, (cycle_load, cycle_disp, cycle_rows) in zip(keys, groups):
                if key < max_marker:
                    continue

                valid_indices = [
                    i for i, (l, d) in enumerate(zip(cycle_load, cycle_disp))
                    if not np.isnan(l) and not np.isnan(d)
                ]
                if not valid_indices:
                    continue

                valid_load = [cycle_load[i] for i in valid_indices]
                valid_disp = [cycle_disp[i] for i in valid_indices]
                load_max_idx = valid_indices[valid_load.index(max(valid_load))]
                disp_max_idx = valid_indices[valid_disp.index(max(valid_disp))]

                if decrease_type == "envelope" or (decrease_type == "both" and load_max_idx == disp_max_idx):
                    append(cycle_rows[disp_max_idx], cycle_load[disp_max_idx], cycle_disp[disp_max_idx] + d_offset,
                           skip_duplicate=True)
                elif load_max_idx != disp_max_idx:
                    for i in range(min(load_max_idx, disp_max_idx), max(load_max_idx, disp_max_idx) + 1):
                        if np.isnan(cycle_load[i]) or np.isnan(cycle_disp[i]):
                            continue
                        append(cycle_rows[i], cycle_load[i], cycle_disp[i] + d_offset, skip_duplicate=True)

    return np.asarray(d_ske, dtype=float), np.asarray(p_ske, dtype=float), np.asarray(rows, dtype=np.int64)


@overload
def compute_cumulative_curve(
    displacement: np.ndarray, load: np.ndarray, markers: Optional[np.ndarray] = None, *,
    side: Side = "positive", return_index: Literal[False] = False,
) -> Tuple[np.ndarray, np.ndarray]: ...
@overload
def compute_cumulative_curve(
    displacement: np.ndarray, load: np.ndarray, markers: Optional[np.ndarray] = None, *,
    side: Side = "positive", return_index: Literal[True],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]: ...
def compute_cumulative_curve(
    displacement: np.ndarray,
    load: np.ndarray,
    markers: Optional[np.ndarray] = None,
    *,
    side: Side = "positive",
    return_index: bool = False,
) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """繰り返し載荷の荷重-変位曲線から累積曲線を計算します。

    正側（荷重 >= 0）の各区間を荷重 0 の点から荷重 0 の点まで取り出し、変位方向につなげます。
    side="negative" なら負側（荷重 <= 0）の各区間を、負の向きにつなげます。
    区間は `compute_excursions` の区間で、曲線は区間ごとに「前に補う荷重 0 の点、区間の行、後ろに補う荷重 0 の点」を
    並べ、`chain_offsets` の規則（最初の区間は始点を 0 に、2つ目以降は始点を前の区間の終点に重ねる）で変位をずらして
    つないだものです。区間の始点の位置は、それまでのその側の区間の残留変形の合計になります。
    `LoadDisplacementOps.split_by_excursions(side=...).chain(変位列).concat()` と同じ曲線です。

    Args:
        displacement: 変位の配列
        load: 荷重の配列
        markers: サイクル番号の配列（省略時は `compute_cycle_markers(load)`）
        side: "positive"（正側）または "negative"（負側）
        return_index: 各点の元の行 index も返すか（追加した荷重 0 の点は元の行がないため -1）

    Returns:
        累積曲線の (変位, 荷重)。return_index=True なら (変位, 荷重, 元の行 index)

    Raises:
        ValueError: side が未知の場合

    Examples:
        >>> from tascpy.numeric.hysteresis import compute_cumulative_curve
        >>> import numpy as np
        >>> disp = np.array([0.0, 1.0, 2.0, 1.5, 0.5, 0.0, 1.0, 2.5])
        >>> load = np.array([0.0, 10.0, 20.0, 10.0, -10.0, -5.0, 15.0, 22.0])
        >>> d_cum, p_cum, rows = compute_cumulative_curve(disp, load, return_index=True)
        >>> d_cum, p_cum, rows
        (array([0.  , 1.  , 2.  , 1.5 , 1.  , 1.  , 1.75, 3.25]), array([ 0., 10., 20., 10.,  0.,  0., 15., 22.]), array([ 0,  1,  2,  3, -1, -1,  6,  7]))
    """
    return _on_side(_positive_cumulative_curve, displacement, load, side, return_index, markers=markers)


class Excursion(NamedTuple):
    """荷重 0 の点から荷重 0 の点までの区間（`compute_excursions` の要素）

    rows は区間に入る元の行の index、start / end は区間の前後に補う荷重 0 の点の変位です
    （補わない端は None。端の行の荷重がちょうど 0 の場合と、データの末尾で荷重 0 に届いていない場合）。
    """

    rows: np.ndarray
    start: Optional[float]
    end: Optional[float]


def compute_excursions(
    displacement: np.ndarray,
    load: np.ndarray,
    markers: Optional[np.ndarray] = None,
    *,
    side: Side = "positive",
) -> List[Excursion]:
    """荷重の片側の区間（荷重 0 の点から荷重 0 の点まで）を求めます。

    正側の区間は、荷重 >= 0 の行が続く範囲のうち荷重 > 0 の行を含むものです（荷重・変位・サイクル番号が
    欠損の行は飛ばします）。荷重 > 0 の行どうしの間で markers の番号が変わる位置でも区切ります。
    区間の両端の荷重 0 の点は、荷重の符号をまたぐ前後の2行の直線補間で求めます。markers の番号で区切った端と、
    データの先頭（載荷の始まりで弾性とみなせる）で荷重 0 から始まっていない端では、区間の端の2行を延長します。
    端の行の荷重がちょうど 0 ならその行が荷重 0 の点で、データの末尾で荷重 0 に届いていない端（載荷の途中で
    終わっている）には荷重 0 の点はありません（どちらも start / end は None）。

    side="negative" なら負側（荷重 <= 0）の区間です。`compute_cumulative_curve` と
    `LoadDisplacementOps.split_by_excursions` はこの区間を使います。

    Args:
        displacement: 変位の配列
        load: 荷重の配列
        markers: サイクル番号の配列（省略時は `compute_cycle_markers(load)`）
        side: "positive"（正側）または "negative"（負側）

    Returns:
        List[Excursion]: 区間のリスト（時系列順）

    Raises:
        ValueError: side が未知の場合

    Examples:
        >>> from tascpy.numeric.hysteresis import compute_excursions
        >>> import numpy as np
        >>> disp = np.array([0.0, 1.0, 2.0, 1.5, 0.5, 0.0, 1.0, 2.5])
        >>> load = np.array([0.0, 10.0, 20.0, 10.0, -10.0, -5.0, 15.0, 22.0])
        >>> [(e.rows.tolist(), e.start, e.end) for e in compute_excursions(disp, load)]
        [([0, 1, 2, 3], None, 1.0), ([6, 7], 0.25, None)]
        >>> [(e.rows.tolist(), e.start, e.end) for e in compute_excursions(disp, load, side="negative")]
        [([4, 5], 1.0, 0.25)]
    """
    sign = _side_sign(side)
    d, p = sign * np.asarray(displacement, dtype=float), sign * np.asarray(load, dtype=float)
    return [Excursion(rows, None if x_s is None else sign * x_s + 0.0, None if x_e is None else sign * x_e + 0.0)
            for rows, x_s, x_e in _positive_excursions(d, p, markers)]


def _positive_excursions(
    displacement: np.ndarray, load: np.ndarray, markers: Optional[np.ndarray],
) -> List[Tuple[np.ndarray, Optional[float], Optional[float]]]:
    """正側の区間ごとの (行 index, 前に補う荷重 0 の点の変位, 後ろに補う荷重 0 の点の変位)"""
    d = np.asarray(displacement, dtype=float)
    p = np.asarray(load, dtype=float)
    m = np.asarray(_markers_or_default(p, markers), dtype=float)
    valid = np.flatnonzero(~(np.isnan(d) | np.isnan(p) | np.isnan(m)))

    # 荷重 >= 0 の行が続く範囲。荷重 > 0 の行どうしの間でサイクル番号が変わる位置でも区切る
    runs: List[List[int]] = []
    current: List[int] = []
    for k, i in enumerate(valid):
        prev = valid[k - 1] if k > 0 else None
        if p[i] < 0:
            if current:
                runs.append(current)
            current = []
            continue
        if current and prev is not None and p[i] > 0 and p[prev] > 0 and m[i] != m[prev]:
            runs.append(current)
            current = []
        current.append(int(i))
    if current:
        runs.append(current)

    position = {int(i): k for k, i in enumerate(valid)}

    def zero_point(rows: List[int], at_start: bool) -> Optional[float]:
        """区間の端に補う荷重 0 の点の変位（端の行の荷重が 0 か、データの末尾で荷重 0 に届いていなければ None）"""
        edge = rows[0] if at_start else rows[-1]
        if p[edge] == 0:
            return None
        k = position[edge] + (-1 if at_start else 1)
        if not 0 <= k < len(valid):
            if not at_start:
                return None
            # データの先頭（載荷の始まり）は弾性とみなし、区間の最初の2行を延長する
            x, _ = _extend_edge(d[rows].tolist(), p[rows].tolist(), 0.0, "y", "start")
            return float(x)
        other = valid[k]
        if p[other] < 0:
            t = p[edge] / (p[edge] - p[other])
            return float(d[edge] + t * (d[other] - d[edge]))
        x, _ = _extend_edge(d[rows].tolist(), p[rows].tolist(), 0.0, "y", "start" if at_start else "end")
        return float(x)

    return [(np.asarray(rows, dtype=np.int64), zero_point(rows, True), zero_point(rows, False))
            for rows in runs if np.any(p[rows] > 0)]


def chain_offsets(firsts: List[float], lasts: List[float]) -> List[float]:
    """区間をつなぐずらし量（最初の区間は始点を 0 に、2つ目以降は始点を前の区間の終点に重ねる）

    firsts / lasts は各区間の始点・終点の値です。`OpsList.chain` と累積曲線が使います。

    Examples:
        >>> from tascpy.numeric.hysteresis import chain_offsets
        >>> chain_offsets([0.0, 0.25], [1.0, 2.5])
        [0.0, 0.75]
    """
    offsets: List[float] = []
    end_of_previous = 0.0
    for first, last in zip(firsts, lasts):
        offset = end_of_previous - first
        offsets.append(offset)
        end_of_previous = last + offset
    return offsets


def _positive_cumulative_curve(displacement: np.ndarray, load: np.ndarray,
                               markers: Optional[np.ndarray]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    d = np.asarray(displacement, dtype=float)
    p = np.asarray(load, dtype=float)
    pieces = []
    for rows, x_s, x_e in _positive_excursions(d, p, markers):
        seg_d = ([] if x_s is None else [x_s]) + d[rows].tolist() + ([] if x_e is None else [x_e])
        seg_p = ([] if x_s is None else [0.0]) + p[rows].tolist() + ([] if x_e is None else [0.0])
        seg_rows = ([] if x_s is None else [-1]) + rows.tolist() + ([] if x_e is None else [-1])
        pieces.append((seg_d, seg_p, seg_rows))
    offsets = chain_offsets([seg_d[0] for seg_d, _, _ in pieces], [seg_d[-1] for seg_d, _, _ in pieces])
    d_cum = [x + offset for (seg_d, _, _), offset in zip(pieces, offsets) for x in seg_d]
    p_cum = [y for _, seg_p, _ in pieces for y in seg_p]
    rows_out = [r for _, _, seg_rows in pieces for r in seg_rows]
    return np.asarray(d_cum, dtype=float), np.asarray(p_cum, dtype=float), np.asarray(rows_out, dtype=np.int64)
