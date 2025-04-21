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
    return loads[yield_index], displacements[yield_index]


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
    offset_displacements = [offset_value + d * initial_slope for d in displacements]
    differences = [offset - load for offset, load in zip(offset_displacements, loads)]
    yield_index = find_index_of_similar_value(differences, 0.0, "closestbggb")
    return loads[yield_index], displacements[yield_index]


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
