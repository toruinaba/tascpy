"""繰り返し載荷の荷重-変位曲線（サイクル・履歴エネルギー・割線剛性・スケルトン曲線・累積曲線）の純粋関数

引数はすべて (displacement, load) の順で、曲線を返す関数は (変位, 荷重) の順の配列を返します。
"""

from typing import List, Optional, Tuple

import numpy as np

from .curve import compute_polygon_area


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
                  markers: np.ndarray) -> Tuple[np.ndarray, List[Tuple[List[float], List[float]]]]:
    """サイクル番号（昇順）と、サイクルごとの (荷重, 変位) リスト。サイクル番号が欠損の行は除く"""
    load = np.asarray(load, dtype=float)
    displacement = np.asarray(displacement, dtype=float)
    markers = np.asarray(markers, dtype=float)
    keys = np.unique(markers[~np.isnan(markers)])
    groups = [(load[markers == k].tolist(), displacement[markers == k].tolist()) for k in keys]
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


def compute_skeleton_curve(
    displacement: np.ndarray,
    load: np.ndarray,
    markers: Optional[np.ndarray] = None,
    has_decrease: bool = False,
    decrease_type: str = "envelope",
) -> Tuple[np.ndarray, np.ndarray]:
    """繰り返し載荷の荷重-変位曲線からスケルトン曲線を計算します。

    最大荷重のサイクルまでは、各サイクルで荷重がそれまでの最大を更新した点を、
    前のサイクルの終わりにつながるよう変位をずらしてつなぎます。

    Args:
        displacement: 変位の配列
        load: 荷重の配列
        markers: サイクル番号の配列（省略時は `compute_cycle_markers(load)`）
        has_decrease: 最大荷重のサイクル以降の減少部分も含めるか
        decrease_type: 減少部分の取り方 ('envelope', 'continuous_only', 'both')

    Returns:
        Tuple[np.ndarray, np.ndarray]: スケルトン曲線の (変位, 荷重)

    Examples:
        >>> from tascpy.numeric.hysteresis import compute_skeleton_curve
        >>> import numpy as np
        >>> disp = np.array([0.0, 1.0, 0.0, -1.0, 0.0, 2.0, 0.0])
        >>> load = np.array([0.0, 10.0, 0.0, -10.0, 0.0, 15.0, 0.0])
        >>> compute_skeleton_curve(disp, load)
        (array([1., 2.]), array([10., 15.]))
    """
    if decrease_type not in ("envelope", "continuous_only", "both"):
        raise ValueError("decrease_typeは'envelope', 'continuous_only', 'both'のいずれかである必要があります")

    markers = _markers_or_default(load, markers)
    keys, groups = _cycle_groups(displacement, load, markers)
    if len(keys) == 0:
        return np.array([]), np.array([])
    marker_arr = np.asarray(markers, dtype=float)
    has_marker = ~np.isnan(marker_arr)
    max_marker = marker_arr[has_marker][np.nanargmax(np.asarray(load, dtype=float)[has_marker])]

    p_ske = []
    d_ske = []
    p_max = 0.0
    d_offset = 0.0

    # 増加部分（最大荷重のサイクルまで）
    for key, (cycle_load, cycle_disp) in zip(keys, groups):
        if key > max_marker:
            break
        d_offset = 0.0

        for i in range(len(cycle_load)):
            if not np.isnan(cycle_load[i]) and cycle_load[i] > p_max:
                p_max = cycle_load[i]
                if d_offset == 0.0 and len(p_ske) >= 2:
                    x, _ = _extend_edge(d_ske, p_ske, cycle_load[i], "y", "end")
                    d_offset = x - cycle_disp[i]
                p_ske.append(cycle_load[i])
                d_ske.append(cycle_disp[i] + d_offset)

    # 減少部分（最大荷重のサイクル以降）
    if has_decrease:
        for key, (cycle_load, cycle_disp) in zip(keys, groups):
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

            if not valid_load or not valid_disp:
                continue

            load_max = max(valid_load)
            disp_max = max(valid_disp)
            load_max_idx = valid_indices[valid_load.index(load_max)]
            disp_max_idx = valid_indices[valid_disp.index(disp_max)]

            if decrease_type == "envelope":
                p_end = cycle_load[disp_max_idx]
                d_end = cycle_disp[disp_max_idx]
                if not np.isnan(p_end) and not np.isnan(d_end):
                    p_ske.append(p_end)
                    d_ske.append(d_end + d_offset)

            elif decrease_type == "continuous_only":
                if load_max_idx == disp_max_idx:
                    continue
                for i in range(min(load_max_idx, disp_max_idx), max(load_max_idx, disp_max_idx) + 1):
                    if np.isnan(cycle_load[i]) or np.isnan(cycle_disp[i]):
                        continue
                    if p_ske and cycle_load[i] == p_ske[-1] and cycle_disp[i] + d_offset == d_ske[-1]:
                        continue
                    p_ske.append(cycle_load[i])
                    d_ske.append(cycle_disp[i] + d_offset)

            elif decrease_type == "both":
                if load_max_idx == disp_max_idx:
                    if not np.isnan(cycle_load[disp_max_idx]) and not np.isnan(cycle_disp[disp_max_idx]):
                        p_ske.append(cycle_load[disp_max_idx])
                        d_ske.append(cycle_disp[disp_max_idx] + d_offset)
                else:
                    for i in range(min(load_max_idx, disp_max_idx), max(load_max_idx, disp_max_idx) + 1):
                        if np.isnan(cycle_load[i]) or np.isnan(cycle_disp[i]):
                            continue
                        if p_ske and cycle_load[i] == p_ske[-1] and cycle_disp[i] + d_offset == d_ske[-1]:
                            continue
                        p_ske.append(cycle_load[i])
                        d_ske.append(cycle_disp[i] + d_offset)

    return np.asarray(d_ske, dtype=float), np.asarray(p_ske, dtype=float)


def compute_cumulative_curve(
    displacement: np.ndarray,
    load: np.ndarray,
    markers: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """繰り返し載荷の荷重-変位曲線から累積曲線を計算します。

    各サイクルの正側（荷重 >= 0）の部分を、荷重 0 まで延長したうえで変位方向につなげます。

    Args:
        displacement: 変位の配列
        load: 荷重の配列
        markers: サイクル番号の配列（省略時は `compute_cycle_markers(load)`）

    Returns:
        Tuple[np.ndarray, np.ndarray]: 累積曲線の (変位, 荷重)

    Examples:
        >>> from tascpy.numeric.hysteresis import compute_cumulative_curve
        >>> import numpy as np
        >>> disp = np.array([0.0, 1.0, 0.0, -1.0, 0.0, 2.0, 0.0])
        >>> load = np.array([0.0, 10.0, 0.0, -10.0, 0.0, 15.0, 0.0])
        >>> d_cum, p_cum = compute_cumulative_curve(disp, load)
    """
    _, groups = _cycle_groups(displacement, load, _markers_or_default(load, markers))

    p_cum = []
    d_cum = []

    for cycle_load, cycle_disp in groups:

        valid_indices = [
            j for j, (l, d) in enumerate(zip(cycle_load, cycle_disp))
            if (not np.isnan(l) and not np.isnan(d))
        ]
        valid_load = [cycle_load[j] for j in valid_indices]
        valid_disp = [cycle_disp[j] for j in valid_indices]

        if not valid_load or not valid_disp:
            continue

        pos_idx = [j for j, x in enumerate(valid_load) if x >= 0.0]
        pos_loads = [valid_load[j] for j in pos_idx]
        pos_displacements = [valid_disp[j] for j in pos_idx]

        if not pos_loads or not pos_displacements:
            continue

        x_s, y_s = _extend_edge(pos_displacements, pos_loads, 0.0, "y", "start")
        x_e, y_e = _extend_edge(pos_displacements, pos_loads, 0.0, "y", "end")

        d_offset = d_cum[-1] - x_s if d_cum else 0.0

        p_extended = [y_s] + pos_loads + [y_e]
        d_extended = [x_s] + pos_displacements + [x_e]
        d_offsetted = [x + d_offset for x in d_extended]

        p_cum.extend(p_extended)
        d_cum.extend(d_offsetted)

    return np.asarray(d_cum, dtype=float), np.asarray(p_cum, dtype=float)
