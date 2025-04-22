from typing import Union, List, Optional


def cycle_count(data: Union[float, bool, None], step=0.5):
    cycle = [1.0]
    for i in range(1, len(data)):
        if data[i] * data[i - 1] < 0:
            c = cycle[i - 1] + step
            cycle.append(c)
        else:
            cycle.append(cycle[i - 1])
    markers = [int(c) for c in cycle]
    return markers


def calclate_slopes(x_data, y_data):
    if len(x_data) != len(y_data):
        raise ValueError("XとYのデータの長さは一致する必要があります")

    if len(x_data) < 2:
        raise ValueError("2つ以上のデータポイントが必要です")
    slopes = []
    for i in range(1, len(x_data)):
        slope = (y_data[i] - y_data[i - 1]) / (x_data[i] - x_data[i - 1])
        slopes.append(slope)
    return slopes


def interpolate_linear(
    value: float, p1: tuple[float, float], p2: tuple[float, float], direction: str = "x"
) -> tuple[float, float]:
    """2点間の線形補間/外挿を行う関数

    Args:
        value: 補間/外挿したい値（directionで指定した軸の値）
        p1: 既知の点1の座標 (x1, y1)
        p2: 既知の点2の座標 (x2, y2)
        direction: 補間の方向。'x'または'y'を指定

    Returns:
        補間/外挿された点の座標 (x, y)

    Raises:
        ValueError: 同じ座標を持つ2点が与えられた場合
        ValueError: 不正なdirectionが指定された場合
    """
    x1, y1 = p1
    x2, y2 = p2

    if direction == "x":
        if x1 == x2:
            raise ValueError("x1 と x2 は異なる値である必要があります")
        y = y1 + (y2 - y1) * (value - x1) / (x2 - x1)
        return (value, y)
    elif direction == "y":
        if y1 == y2:
            raise ValueError("y1 と y2 は異なる値である必要があります")
        x = x1 + (x2 - x1) * (value - y1) / (y2 - y1)
        return (x, value)
    else:
        raise ValueError("directionは'x'または'y'である必要があります")


def calculate_slope_average(x_data, y_data):
    slopes = calclate_slopes(x_data, y_data)
    return sum(slopes) / len(slopes)


def find_index_of_similar_value(data, target, comparison_mode="closest"):
    if not data:
        raise ValueError("データリストは空ではいけません")

    if comparison_mode == "closest":
        closest_index = min(range(len(data)), key=lambda i: abs(data[i] - target))
        return closest_index
    elif comparison_mode == "more_than":
        for i, value in enumerate(data):
            if value > target:
                return i
        return -1
    elif comparison_mode == "less_than":
        for i, value in enumerate(data):
            if value < target:
                return i
        return -1
    else:
        raise ValueError(
            "comparison_modeは'closest'、'more_than'、または'less_than'のいずれかである必要があります"
        )


def extract_range_indices_by_ratio(
    data: List[float], r_lower: float, r_upper: float
) -> List[float]:
    if not data:
        raise ValueError("データリストは空ではいけません")

    # r_lower と r_upper の範囲チェック
    if not (0 <= r_lower <= 1):
        raise ValueError("r_lowerは0以上1以下である必要があります")
    if not (0 <= r_upper <= 1):
        raise ValueError("r_upperは0以上1以下である必要があります")
    if r_lower > r_upper:
        raise ValueError("r_lowerはr_upper以下である必要があります")

    # 最大値を計算
    max_value = max(data)  # None を除外して最大値を計算

    # 比率に基づく範囲を計算
    lower_bound = max_value * r_lower
    upper_bound = max_value * r_upper
    print(
        f"max: {max_value}, lower_bound: {lower_bound}, upper_bound: {upper_bound}"
    )  # デバッグ用

    # 範囲のインデックスを取得
    start_index = find_index_of_similar_value(
        data, lower_bound, comparison_mode="closest"
    )
    end_index = find_index_of_similar_value(
        data, upper_bound, comparison_mode="closest"
    )
    print(f"start_index: {start_index}, end_index: {end_index}")  # デバッグ用

    return start_index, end_index


def calculate_ranged_slope_average(
    x_data: List[float],
    y_data: List[float],
    r_lower: float,
    r_upper: float,
    base_on: str = "y",
) -> Optional[float]:
    """指定された範囲に基づいて傾きを計算する関数
    Args:
        x_data: X軸のデータ
        y_data: Y軸のデータ
        r_lower: 範囲の下限比率 (0から1の間)
        r_upper: 範囲の上限比率 (0から1の間)
        base_on: "x" または "y" のいずれかを指定。範囲の基準を指定
    Returns:
        指定された範囲に基づく平均傾き
    """
    if base_on == "x":
        start_index, end_index = extract_range_indices_by_ratio(
            x_data, r_lower, r_upper
        )
    elif base_on == "y":
        start_index, end_index = extract_range_indices_by_ratio(
            y_data, r_lower, r_upper
        )
    else:
        raise ValueError("base_onは'x'または'y'である必要があります")
    if start_index == -1 or end_index == -1:
        raise ValueError("指定された範囲にデータが存在しません")
    if start_index >= end_index:
        raise ValueError("start_indexはend_indexより小さい必要があります")
    return calculate_slope_average(
        x_data[start_index : end_index + 1], y_data[start_index : end_index + 1]
    )


def find_general_yield_point(
    displacements: List[float],
    loads: List[float],
    r_lower: float = 0.3,
    r_upper: float = 0.7,
    factor: float = 0.33,
) -> Optional[float]:
    """降伏点を計算する関数
    Args:
        displacements: 変位データ
        loads: 荷重データ
        r_lower: 範囲の下限比率 (0から1の間)
        r_upper: 範囲の上限比率 (0から1の間)
        base_on: "x" または "y" のいずれかを指定。範囲の基準を指定
    Returns:
        降伏点(index)
    """
    initial_slope = calculate_ranged_slope_average(
        displacements, loads, r_lower, r_upper, base_on="y"
    )
    print(f"initial_slope: {initial_slope}")  # デバッグ用
    if initial_slope is None:
        return None
    slopes = calclate_slopes(displacements, loads)
    print(f"slopes: {slopes}")  # デバッグ用
    yield_index = find_index_of_similar_value(
        slopes, initial_slope * factor, "less_than"
    )
    print(f"yield_index: {yield_index}")  # デバッグ用
    return loads[yield_index], displacements[yield_index], initial_slope


def find_offset_yield_point(
    displacements: List[float],
    loads: List[float],
    offset_value: float = 0.2,
    r_lower: float = 0.3,
    r_upper: float = 0.7,
) -> Optional[float]:
    """オフセット降伏点を計算する関数
    Args:
        displacements: 変位データ
        loads: 荷重データ
        r_lower: 範囲の下限比率 (0から1の間)
        r_upper: 範囲の上限比率 (0から1の間)
        base_on: "x" または "y" のいずれかを指定。範囲の基準を指定
    Returns:
        降伏点(index)
    """
    initial_slope = calculate_ranged_slope_average(
        displacements, loads, r_lower, r_upper, base_on="y"
    )
    if initial_slope is None:
        return None
    offset_displacements = [
        d * initial_slope - initial_slope * offset_value for d in displacements
    ]
    differences = [offset - load for offset, load in zip(offset_displacements, loads)]
    yield_index = find_index_of_similar_value(differences, 0.0, "closest")
    return loads[yield_index], displacements[yield_index], initial_slope


def extend_data_edge(
    x_data: List[float],
    y_data: List[float],
    target: float,
    target_type: str = "x",  # "x" または "y"
    extend_position: str = "end",  # "start" または "end"
):
    """指定された方向にデータを延長する関数

    Args:
        x_data: X軸のデータ
        y_data: Y軸のデータ
        target: 拡張したい値
        target_type: ターゲットの値の種類。'x'または'y'を指定
        extend_position: 延長する位置。"start"または"end"を指定
    Returns:
        拡張されたデータ (x, y)

    Raises:
        ValueError: 不正なdirectionまたはextend_positionが指定された場合
    """
    if extend_position == "end":
        if target_type == "x":
            x, y = interpolate_linear(
                target,
                (x_data[-2], y_data[-2]),
                (x_data[-1], y_data[-1]),
                direction="x",
            )
        elif target_type == "y":
            x, y = interpolate_linear(
                target,
                (x_data[-2], y_data[-2]),
                (x_data[-1], y_data[-1]),
                direction="y",
            )
        else:
            raise ValueError("target_typeは'x'または'y'である必要があります")
    elif extend_position == "start":
        if target_type == "x":
            x, y = interpolate_linear(
                target,
                (x_data[0], y_data[0]),
                (x_data[1], y_data[1]),
                direction="x",
            )
        elif target_type == "y":
            x, y = interpolate_linear(
                target,
                (x_data[0], y_data[0]),
                (x_data[1], y_data[1]),
                direction="y",
            )
        else:
            raise ValueError("target_typeは'x'または'y'である必要があります")
    else:
        raise ValueError("extend_positionは'start'または'end'である必要があります")
    return x, y


def create_skeleton_curve(
    displacements: List[float],
    loads: List[float],
    has_decrease: bool = False,
    decrease_type: str = "envelope",
):
    """スケルトン曲線を作成する関数

    Args:
        displacements: 変位データ
        loads: 荷重データ
        has_decrease: 減少があるかどうか
        decrease_type: 減少の種類。'envelope', 'continous_only', 'both'を指定

    Returns:
        スケルトン曲線のデータ (x, y)
    """
    from ..utils.split import split_list_by_integers

    p_ske = []
    d_ske = []
    p_max = 0.0

    markers = cycle_count(loads)
    max_index = loads.index(max(loads))
    max_marker = markers[max_index]
    end_marker = markers[-1]
    splitted_loads = split_list_by_integers(loads, markers)
    splitted_disps = split_list_by_integers(displacements, markers)

    for cyc in range(max_marker):
        load = splitted_loads[cyc]
        disp = splitted_disps[cyc]
        d_offset = 0.0
        for i in range(len(load)):
            if load[i] > p_max:
                p_max = load[i]
                if d_offset == 0.0:
                    if len(p_ske) >= 2:
                        x, _ = extend_data_edge(d_ske, p_ske, load[i], "y", "end")
                        d_offset = x - disp[i]
                p_ske.append(load[i])
                d_ske.append(disp[i] + d_offset)

    if has_decrease:
        for cyc in range(max_marker - 1, end_marker):
            load = splitted_loads[cyc]
            disp = splitted_disps[cyc]
            load_max_index = load.index(max(load))
            disp_max_index = disp.index(max(disp))
            if decrease_type == "envelope":
                p_end = load[disp_max_index]
                d_end = disp[disp_max_index]
                p_ske.append(p_end)
                d_ske.append(d_end + d_offset)
            elif decrease_type == "continuous_only":
                if load_max_index == disp_max_index:
                    continue
                d_offset = 0.0
                for i in range(load_max_index, disp_max_index + 1):
                    if d_offset == 0.0:
                        d_offset = d_ske[-1] - disp[i]
                    if load[i] == p_ske[-1] and disp[i] + d_offset == d_ske[-1]:
                        continue
                    p_ske.append(load[i])
                    d_ske.append(disp[i] + d_offset)
            elif decrease_type == "both":
                if load_max_index == disp_max_index:
                    p_end = load[disp_max_index]
                    d_end = disp[disp_max_index]
                    p_ske.append(p_end)
                else:
                    d_offset = 0.0
                    for i in range(load_max_index, disp_max_index + 1):
                        if d_offset == 0.0:
                            d_offset = d_ske[-1] - disp[i]
                        if load[i] == p_ske[-1] and disp[i] + d_offset == d_ske[-1]:
                            continue
                        p_ske.append(load[i])
                        d_ske.append(disp[i] + d_offset)
            else:
                raise ValueError(
                    "decrease_typeは'envelope', 'continous_only', 'both'のいずれかである必要があります"
                )
    return p_ske, d_ske


def create_cumulative_curve(displacements: List[float], loads: List[float]):
    """累積曲線を作成する関数

    Args:
        displacements (List[float]):変位データのリスト
        loads (List[float]): 荷重データのリスト
    Returns:
        Tuple[List[float], List[float]]: 累積荷重と累積変位のタプル
    """
    from ..utils.split import split_list_by_integers, split_list_by_condition

    markers = cycle_count(loads)
    splitted_loads = split_list_by_integers(loads, markers)
    splitted_displacements = split_list_by_integers(displacements, markers)
    p_cum = []
    d_cum = []
    for i in range(len(splitted_loads)):
        load = splitted_loads[i]
        displacement = splitted_displacements[i]
        pos_idx = [
            i for i, x in enumerate(load) if x >= 0.0
        ]  # 荷重が正の値を持つインデックスを取得
        neg_idx = [
            i for i, x in enumerate(load) if x < 0.0
        ]  # 荷重が負の値を持つインデックスを取得
        pos_loads = [load[i] for i in pos_idx]
        neg_loads = [load[i] for i in neg_idx]
        pos_displacements = [displacement[i] for i in pos_idx]
        neg_displacements = [displacement[i] for i in neg_idx]
        x_s, y_s = extend_data_edge(pos_displacements, pos_loads, 0.0, "y", "start")
        x_e, y_e = extend_data_edge(pos_displacements, pos_loads, 0.0, "y", "end")
        p_extended = [y_s] + pos_loads + [y_e]
        d_extended = [x_s] + pos_displacements + [x_e]
        d_offset = d_cum[-1] - x_s if d_cum else 0.0
        d_offsetted = [x + d_offset for x in d_extended]
        p_cum += p_extended
        d_cum += d_offsetted

    return p_cum, d_cum
