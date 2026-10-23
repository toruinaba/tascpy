from typing import Any, Dict, Tuple

import numpy as np


def prepare_outlier_data(
    x_values: Any,
    y_values: Any,
    flags: Any,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, int]:
    """外れ値フラグ（0: 正常, 1: 外れ値）に基づいてデータを正常値と外れ値に分けます。

    Returns:
        (正常値 x, 正常値 y, 外れ値 x, 外れ値 y, 外れ値の数)
    """
    flags_arr = np.asarray(flags)
    x_arr = np.asarray(x_values)
    y_arr = np.asarray(y_values)
    normal = flags_arr == 0
    outlier = flags_arr == 1
    return x_arr[normal], y_arr[normal], x_arr[outlier], y_arr[outlier], int(outlier.sum())


def prepare_const_x_data(y_data: Dict[str, Any], x_values: Any) -> Tuple[np.ndarray, np.ndarray]:
    """{列のラベル: 値} と各列の位置から、描画用の (x 配列, y 配列) を作ります（欠損は NaN）。

    Raises:
        ValueError: x_values と y_data の数が一致しない場合
    """
    x_arr = np.asarray(x_values, dtype=float)
    if len(x_arr) != len(y_data):
        raise ValueError(f"x_values の長さ ({len(x_arr)}) と列の数 ({len(y_data)}) が一致しません")
    y_arr = np.array([np.nan if v is None else float(v) for v in y_data.values()], dtype=float)
    return x_arr, y_arr
