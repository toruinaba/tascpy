"""行の位置（小数の index）での補間と、値の横切り"""

from __future__ import annotations

import math
from typing import Any

import numpy as np


def interpolate_at(values: Any, position: float) -> float:
    """行の位置（小数の index）での値を、前後の行の直線補間で求めます

    3.25 なら index 3 と 4 の間の 25% の位置です。整数の位置はその行の値です。
    位置が NaN、または前後の行のどちらかの値が NaN なら NaN です。

    Raises:
        ValueError: 位置が行の範囲外の場合

    Examples:
        >>> from tascpy.numeric.position import interpolate_at
        >>> interpolate_at([0.0, 10.0, 20.0], 1.5)
        15.0
        >>> interpolate_at([0.0, 10.0, float("nan")], 1.0)
        10.0
    """
    v = np.asarray(values, dtype=float)
    at = float(position)
    if math.isnan(at):
        return np.nan
    if not 0 <= at <= len(v) - 1:
        raise ValueError(f"位置 {at} は行の範囲外です (0-{len(v) - 1})")
    lower = int(math.floor(at))
    t = at - lower
    if t == 0:
        return float(v[lower])
    return float(v[lower] + t * (v[lower + 1] - v[lower]))


def interpolate_positions(values: Any, positions: Any) -> np.ndarray:
    """複数の行の位置での値（`interpolate_at` を位置ごとに適用。NaN の位置は NaN）

    Examples:
        >>> from tascpy.numeric.position import interpolate_positions
        >>> interpolate_positions([0.0, 10.0, 20.0], [0.0, 1.25, float("nan")])
        array([ 0. , 12.5,  nan])
    """
    return np.array([interpolate_at(values, p) for p in np.asarray(positions, dtype=float)], dtype=float)


def find_crossings(values: Any, level: float) -> np.ndarray:
    """値が level に等しくなる行の位置（小数の index）を、時系列順に求めます

    隣り合う有効な値（NaN を飛ばす）が level をまたぐ位置は直線補間で求め、値がちょうど level の行はその行の位置です
    （level の値が続く行は最初の行だけ）。NaN の行をはさんでまたぐ場合も、前後の有効な行の間で補間します。

    Examples:
        >>> from tascpy.numeric.position import find_crossings
        >>> find_crossings([0.0, 10.0, 20.0, 10.0, 0.0], 15.0)
        array([1.5, 2.5])
        >>> find_crossings([0.0, 10.0, 10.0, 20.0], 10.0)
        array([1.])
        >>> find_crossings([0.0, float("nan"), 20.0], 5.0)
        array([0.5])
    """
    v = np.asarray(values, dtype=float)
    valid = np.flatnonzero(~np.isnan(v))
    positions = []
    for k, i in enumerate(valid):
        if v[i] == level:
            if k == 0 or v[valid[k - 1]] != level:
                positions.append(float(i))
            continue
        if k == 0:
            continue
        j = valid[k - 1]
        if (v[j] - level) * (v[i] - level) < 0:
            t = (level - v[j]) / (v[i] - v[j])
            positions.append(float(j + t * (i - j)))
    return np.asarray(positions, dtype=float)
