"""繰り返し載荷（サイクル・ヒステリシス・スケルトン曲線・累積曲線）の純粋関数"""

from typing import List, Tuple

import numpy as np

from .curve import calculate_polygon_area, extend_data_edge


def compute_cycle_markers(data: np.ndarray, step: float = 0.5) -> np.ndarray:
    """データの符号反転からサイクル番号を数えます。

    0 と欠損（NaN）は符号を持たない点として飛ばし、直前の有効な値と符号が変わった位置で
    step だけ数を進めます（step=0.5 なら正負の往復で 1 サイクル）。サイクル番号は 1 から始まります。

    Args:
        data: 対象データ配列（欠損は NaN または None）
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
    sign = np.nan_to_num(np.sign(np.asarray(data, dtype=float)))
    nonzero = np.flatnonzero(sign)
    flips = np.zeros(len(sign))
    flips[nonzero[1:]] = sign[nonzero[1:]] != sign[nonzero[:-1]]
    return np.floor(1 + step * np.cumsum(flips)).astype(int)


def compute_hysteresis_energy(
    loads: np.ndarray,
    disps: np.ndarray,
) -> Tuple[float, float, float, float, float]:
    """1サイクルのヒステリシスループ面積（エネルギー散逸）と統計量を計算します。

    Args:
        loads: 荷重データ配列
        disps: 変位データ配列

    Returns:
        Tuple[float, float, float, float, float]:
            (エネルギー, 最大荷重, 最小荷重, 最大変位, 最小変位)
            
    Examples:
        >>> from tascpy.numeric.hysteresis import compute_hysteresis_energy
        >>> import numpy as np
        >>> loads = np.array([0, 100, 0, -100, 0])
        >>> disps = np.array([0, 1, 2, 1, 0])
        >>> compute_hysteresis_energy(loads, disps)
        (200.0, 100.0, -100.0, 2.0, 0.0)
    """
    load = np.asarray(loads, dtype=float)
    disp = np.asarray(disps, dtype=float)
    if len(load) != len(disp):
        raise ValueError("荷重と変位のデータ長が一致しません")

    valid = ~(np.isnan(load) | np.isnan(disp))
    if valid.sum() < 3:
        return (0.0, np.nan, np.nan, np.nan, np.nan)
    l_arr, d_arr = load[valid], disp[valid]
    return (calculate_polygon_area(d_arr, l_arr), float(l_arr.max()), float(l_arr.min()),
            float(d_arr.max()), float(d_arr.min()))


def compute_secant_stiffness(
    max_load: float,
    min_load: float,
    disp_at_max_load: float,
    disp_at_min_load: float,
) -> float:
    """最大荷重点と最小荷重点を結ぶ直線の傾き（割線剛性）を計算します。

    Args:
        max_load: 最大荷重
        min_load: 最小荷重
        disp_at_max_load: 最大荷重点の変位
        disp_at_min_load: 最小荷重点の変位

    Returns:
        float: 割線剛性（計算不能時は np.nan）

    Examples:
        >>> from tascpy.numeric.hysteresis import compute_secant_stiffness
        >>> compute_secant_stiffness(100.0, -100.0, 1.0, -1.0)
        100.0
    """
    values = (max_load, min_load, disp_at_max_load, disp_at_min_load)
    if any(v is None or np.isnan(v) for v in values):
        return np.nan

    delta_disp = disp_at_max_load - disp_at_min_load
    if abs(delta_disp) < 1e-9:
        return np.nan
    return float((max_load - min_load) / delta_disp)


def compute_energy_and_stats(
    loads: np.ndarray,
    disps: np.ndarray,
    markers: np.ndarray,
) -> Tuple[float, float, float, float, float, float]:
    """1サイクルのヒステリシス解析結果と各種統計情報をまとめて計算します。
    
    Args:
        loads: 荷重データ配列
        disps: 変位データ配列
        markers: サイクルマーカーの配列。先頭要素をサイクル番号として抽出します。
        
    Returns:
        Tuple: (サイクル番号, エネルギー, 最大荷重, 最小荷重, 最大変位, 最小変位)
        
    Examples:
        >>> from tascpy.numeric.hysteresis import compute_energy_and_stats
        >>> import numpy as np
        >>> loads = np.array([0, 100, 0, -100, 0])
        >>> disps = np.array([0, 1, 2, 1, 0])
        >>> markers = np.array([1, 1, 1, 1, 1])
        >>> compute_energy_and_stats(loads, disps, markers)
        (1.0, 200.0, 100.0, -100.0, 2.0, 0.0)
    """
    energy, max_l, min_l, max_d, min_d = compute_hysteresis_energy(loads, disps)
    c_num = float(markers[0]) if len(markers) > 0 else 1.0
    return c_num, energy, max_l, min_l, max_d, min_d


def compute_stiffness_degradation_stats(
    loads: np.ndarray,
    disps: np.ndarray,
    markers: np.ndarray,
) -> Tuple[float, float]:
    """1サイクルの割線剛性（最大荷重点と最小荷重点を結ぶ直線の傾き）を計算します。

    Args:
        loads: 荷重データ配列
        disps: 変位データ配列
        markers: サイクルマーカーの配列。先頭要素をサイクル番号として抽出します。

    Returns:
        Tuple: (サイクル番号, 割線剛性)。荷重・変位がともに有効な点が2点未満なら剛性は NaN

    Examples:
        >>> from tascpy.numeric.hysteresis import compute_stiffness_degradation_stats
        >>> import numpy as np
        >>> loads = np.array([0, 100, 0, -100, 0])
        >>> disps = np.array([0, 1, 0, -1, 0])
        >>> markers = np.array([1, 1, 1, 1, 1])
        >>> compute_stiffness_degradation_stats(loads, disps, markers)
        (1.0, 100.0)
    """
    c_num = float(markers[0]) if len(markers) > 0 else 1.0
    loads = np.asarray(loads, dtype=float)
    disps = np.asarray(disps, dtype=float)
    valid = ~(np.isnan(loads) | np.isnan(disps))
    if valid.sum() < 2:
        return c_num, np.nan
    l_arr, d_arr = loads[valid], disps[valid]
    i_max, i_min = int(np.argmax(l_arr)), int(np.argmin(l_arr))
    return c_num, compute_secant_stiffness(l_arr[i_max], l_arr[i_min], d_arr[i_max], d_arr[i_min])


def _cycle_groups(loads: np.ndarray, displacements: np.ndarray,
                  markers: np.ndarray) -> Tuple[np.ndarray, List[Tuple[List[float], List[float]]]]:
    """サイクル番号（昇順）と、サイクルごとの (荷重, 変位) リスト。サイクル番号が欠損の行は除く"""
    loads = np.asarray(loads, dtype=float)
    displacements = np.asarray(displacements, dtype=float)
    markers = np.asarray(markers, dtype=float)
    keys = np.unique(markers[~np.isnan(markers)])
    groups = [(loads[markers == k].tolist(), displacements[markers == k].tolist()) for k in keys]
    return keys, groups


def compute_skeleton_curve(
    loads: np.ndarray,
    displacements: np.ndarray,
    markers: np.ndarray,
    has_decrease: bool = False,
    decrease_type: str = "envelope",
) -> Tuple[np.ndarray, np.ndarray]:
    """荷重-変位データからスケルトン曲線を計算します。
    
    Args:
        loads: 荷重データ
        displacements: 変位データ
        markers: サイクルマーカー
        has_decrease: 減少部分も含めるか
        decrease_type: 減少部分の処理方法 ('envelope', 'continuous_only', 'both')
        
    Returns:
        Tuple[np.ndarray, np.ndarray]: スケルトン曲線の (変位, 荷重)
        
    Examples:
        >>> from tascpy.numeric.hysteresis import compute_skeleton_curve
        >>> import numpy as np
        >>> loads = np.array([0, 10, 20, 15, 0])
        >>> disps = np.array([0, 1, 2, 3, 4])
        >>> markers = np.array([1, 1, 1, 1, 1])
        >>> d_ske, p_ske = compute_skeleton_curve(loads, disps, markers, has_decrease=True)
    """
    if decrease_type not in ("envelope", "continuous_only", "both"):
        raise ValueError("decrease_typeは'envelope', 'continuous_only', 'both'のいずれかである必要があります")

    keys, groups = _cycle_groups(loads, displacements, markers)
    if len(keys) == 0:
        return np.array([]), np.array([])
    marker_arr = np.asarray(markers, dtype=float)
    has_marker = ~np.isnan(marker_arr)
    max_marker = marker_arr[has_marker][np.nanargmax(np.asarray(loads, dtype=float)[has_marker])]

    p_ske = []
    d_ske = []
    p_max = 0.0
    d_offset = 0.0

    # 増加部分（最大荷重のサイクルまで）
    for key, (load, disp) in zip(keys, groups):
        if key > max_marker:
            break
        d_offset = 0.0

        for i in range(len(load)):
            if not np.isnan(load[i]) and load[i] > p_max:
                p_max = load[i]
                if d_offset == 0.0 and len(p_ske) >= 2:
                    x, _ = extend_data_edge(d_ske, p_ske, load[i], "y", "end")
                    d_offset = x - disp[i]
                p_ske.append(load[i])
                d_ske.append(disp[i] + d_offset)

    # 減少部分（最大荷重のサイクル以降）
    if has_decrease:
        for key, (load, disp) in zip(keys, groups):
            if key < max_marker:
                continue

            valid_indices = [
                i for i, (l, d) in enumerate(zip(load, disp))
                if not np.isnan(l) and not np.isnan(d)
            ]

            if not valid_indices:
                continue

            valid_load = [load[i] for i in valid_indices]
            valid_disp = [disp[i] for i in valid_indices]

            if not valid_load or not valid_disp:
                continue

            load_max = max(valid_load)
            disp_max = max(valid_disp)
            load_max_idx = valid_indices[valid_load.index(load_max)]
            disp_max_idx = valid_indices[valid_disp.index(disp_max)]

            if decrease_type == "envelope":
                p_end = load[disp_max_idx]
                d_end = disp[disp_max_idx]
                if not np.isnan(p_end) and not np.isnan(d_end):
                    p_ske.append(p_end)
                    d_ske.append(d_end + d_offset)

            elif decrease_type == "continuous_only":
                if load_max_idx == disp_max_idx:
                    continue
                for i in range(min(load_max_idx, disp_max_idx), max(load_max_idx, disp_max_idx) + 1):
                    if np.isnan(load[i]) or np.isnan(disp[i]):
                        continue
                    if p_ske and load[i] == p_ske[-1] and disp[i] + d_offset == d_ske[-1]:
                        continue
                    p_ske.append(load[i])
                    d_ske.append(disp[i] + d_offset)

            elif decrease_type == "both":
                if load_max_idx == disp_max_idx:
                    if not np.isnan(load[disp_max_idx]) and not np.isnan(disp[disp_max_idx]):
                        p_ske.append(load[disp_max_idx])
                        d_ske.append(disp[disp_max_idx] + d_offset)
                else:
                    for i in range(min(load_max_idx, disp_max_idx), max(load_max_idx, disp_max_idx) + 1):
                        if np.isnan(load[i]) or np.isnan(disp[i]):
                            continue
                        if p_ske and load[i] == p_ske[-1] and disp[i] + d_offset == d_ske[-1]:
                            continue
                        p_ske.append(load[i])
                        d_ske.append(disp[i] + d_offset)

    return np.asarray(d_ske, dtype=float), np.asarray(p_ske, dtype=float)


def compute_cumulative_curve(
    loads: np.ndarray,
    displacements: np.ndarray,
    markers: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """荷重-変位データから累積曲線を計算します。
    
    Args:
        loads: 荷重データ
        displacements: 変位データ
        markers: サイクルマーカー
        
    Returns:
        Tuple[np.ndarray, np.ndarray]: 累積曲線の (変位, 荷重)
        
    Examples:
        >>> from tascpy.numeric.hysteresis import compute_cumulative_curve
        >>> import numpy as np
        >>> loads = np.array([0, 10, 0, -10, 0, 15, 0])
        >>> disps = np.array([0, 1, 2, 1, 0, 1.5, 2.5])
        >>> markers = np.array([1, 1, 1, 1, 1, 2, 2])
        >>> d_cum, p_cum = compute_cumulative_curve(loads, disps, markers)
    """
    _, groups = _cycle_groups(loads, displacements, markers)

    p_cum = []
    d_cum = []

    for load, displacement in groups:

        valid_indices = [
            j for j, (l, d) in enumerate(zip(load, displacement))
            if (not np.isnan(l) and not np.isnan(d))
        ]
        valid_load = [load[j] for j in valid_indices]
        valid_disp = [displacement[j] for j in valid_indices]

        if not valid_load or not valid_disp:
            continue

        pos_idx = [j for j, x in enumerate(valid_load) if x >= 0.0]
        pos_loads = [valid_load[j] for j in pos_idx]
        pos_displacements = [valid_disp[j] for j in pos_idx]

        if not pos_loads or not pos_displacements:
            continue

        x_s, y_s = extend_data_edge(pos_displacements, pos_loads, 0.0, "y", "start")
        x_e, y_e = extend_data_edge(pos_displacements, pos_loads, 0.0, "y", "end")

        d_offset = d_cum[-1] - x_s if d_cum else 0.0

        p_extended = [y_s] + pos_loads + [y_e]
        d_extended = [x_s] + pos_displacements + [x_e]
        d_offsetted = [x + d_offset for x in d_extended]

        p_cum.extend(p_extended)
        d_cum.extend(d_offsetted)

    return np.asarray(d_cum, dtype=float), np.asarray(p_cum, dtype=float)
