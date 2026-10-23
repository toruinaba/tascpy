"""荷重-変位データの特殊曲線に関する純粋関数群"""

from typing import List, Tuple, Any
import numpy as np


def _cycle_groups(loads: np.ndarray, displacements: np.ndarray,
                  markers: np.ndarray) -> Tuple[np.ndarray, List[Tuple[List[float], List[float]]]]:
    """サイクル番号（昇順）と、サイクルごとの (荷重, 変位) リスト。サイクル番号が欠損の行は除く"""
    loads = np.asarray(loads, dtype=float)
    displacements = np.asarray(displacements, dtype=float)
    markers = np.asarray(markers, dtype=float)
    keys = np.unique(markers[~np.isnan(markers)])
    groups = [(loads[markers == k].tolist(), displacements[markers == k].tolist()) for k in keys]
    return keys, groups


def extend_data_edge(
    x_data: List[float], 
    y_data: List[float], 
    target: float, 
    target_type: str = "x", 
    extend_position: str = "end"
) -> Tuple[float, float]:
    """指定された方向にデータを線形補間により延長する関数

    Args:
        x_data: x座標データのリスト
        y_data: y座標データのリスト
        target: 延長先のターゲット値
        target_type: 延長する軸の種類 ("x"または"y")
        extend_position: 延長する位置 ("start"または"end")

    Returns:
        Tuple: 延長後の(x, y)座標
        
    Examples:
        >>> from tascpy.analytics.functional.load_displacement.curves import extend_data_edge
        >>> x = [0.0, 1.0]
        >>> y = [0.0, 10.0]
        >>> extend_data_edge(x, y, 2.0, target_type="x", extend_position="end")
        (2.0, 20.0)
    """
    if extend_position == "end":
        if len(x_data) < 2 or len(y_data) < 2:
            return (target, y_data[-1]) if target_type == "x" else (x_data[-1], target)

        x1, y1 = x_data[-2], y_data[-2]
        x2, y2 = x_data[-1], y_data[-1]
    else:  # start
        if len(x_data) < 2 or len(y_data) < 2:
            return (target, y_data[0]) if target_type == "x" else (x_data[0], target)

        x1, y1 = x_data[0], y_data[0]
        x2, y2 = x_data[1], y_data[1]

    if target_type == "x":
        if x1 == x2:
            return target, y1
        y = y1 + (y2 - y1) * (target - x1) / (x2 - x1)
        return target, y
    else:  # "y"
        if y1 == y2:
            return x1, target
        x = x1 + (x2 - x1) * (target - y1) / (y2 - y1)
        return x, target


def compute_skeleton_curve(
    loads: np.ndarray,
    displacements: np.ndarray,
    markers: np.ndarray,
    has_decrease: bool = False,
    decrease_type: str = "envelope",
    *args,
    **kwargs
) -> Tuple[List[float], List[float]]:
    """荷重-変位データからスケルトン曲線を計算します。
    
    Args:
        loads: 荷重データ
        displacements: 変位データ
        markers: サイクルマーカー
        has_decrease: 減少部分も含めるか
        decrease_type: 減少部分の処理方法 ('envelope', 'continuous_only', 'both')
        
    Returns:
        Tuple[List[float], List[float]]: スケルトン曲線の(変位, 荷重)リスト
        
    Examples:
        >>> from tascpy.analytics.functional.load_displacement.curves import compute_skeleton_curve
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
        return [], []
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
            if load[i] is not None and not np.isnan(load[i]) and load[i] > p_max:
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
                if l is not None and not np.isnan(l) and d is not None and not np.isnan(d)
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
                if p_end is not None and not np.isnan(p_end) and d_end is not None and not np.isnan(d_end):
                    p_ske.append(p_end)
                    d_ske.append(d_end + d_offset)

            elif decrease_type == "continuous_only":
                if load_max_idx == disp_max_idx:
                    continue
                for i in range(min(load_max_idx, disp_max_idx), max(load_max_idx, disp_max_idx) + 1):
                    if load[i] is None or np.isnan(load[i]) or disp[i] is None or np.isnan(disp[i]):
                        continue
                    if p_ske and load[i] == p_ske[-1] and disp[i] + d_offset == d_ske[-1]:
                        continue
                    p_ske.append(load[i])
                    d_ske.append(disp[i] + d_offset)

            elif decrease_type == "both":
                if load_max_idx == disp_max_idx:
                    if load[disp_max_idx] is not None and not np.isnan(load[disp_max_idx]) and disp[disp_max_idx] is not None and not np.isnan(disp[disp_max_idx]):
                        p_ske.append(load[disp_max_idx])
                        d_ske.append(disp[disp_max_idx] + d_offset)
                else:
                    for i in range(min(load_max_idx, disp_max_idx), max(load_max_idx, disp_max_idx) + 1):
                        if load[i] is None or np.isnan(load[i]) or disp[i] is None or np.isnan(disp[i]):
                            continue
                        if p_ske and load[i] == p_ske[-1] and disp[i] + d_offset == d_ske[-1]:
                            continue
                        p_ske.append(load[i])
                        d_ske.append(disp[i] + d_offset)

    return d_ske, p_ske


def compute_cumulative_curve(
    loads: np.ndarray,
    displacements: np.ndarray,
    markers: np.ndarray,
    *args,
    **kwargs
) -> Tuple[List[float], List[float]]:
    """荷重-変位データから累積曲線を計算します。
    
    Args:
        loads: 荷重データ
        displacements: 変位データ
        markers: サイクルマーカー
        
    Returns:
        Tuple[List[float], List[float]]: 累積曲線の(変位, 荷重)リスト
        
    Examples:
        >>> from tascpy.analytics.functional.load_displacement.curves import compute_cumulative_curve
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
            if (l is not None and not np.isnan(l) and d is not None and not np.isnan(d))
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

    return d_cum, p_cum
