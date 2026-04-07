from typing import Tuple, Dict, Any, List
import numpy as np


def prepare_outlier_data(
    x_values: np.ndarray,
    y_values: np.ndarray,
    flags: List[int],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, int]:
    """異常値フラグに基づいてデータを正常値と異常値に分割します。

    Args:
        x_values (np.ndarray): x軸のデータ配列。
        y_values (np.ndarray): y軸のデータ配列。
        flags (List[int]): 異常値フラグのリスト（0: 正常, 1: 異常）。

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, int]: 
            (正常値x, 正常値y, 異常値x, 異常値y, 異常値カウント) のタプル。
    """
    flags_arr = np.array(flags)
    x_arr = np.array(x_values)
    y_arr = np.array(y_values)
    
    normal_mask = (flags_arr == 0)
    outlier_mask = (flags_arr == 1)
    
    outlier_count = np.sum(outlier_mask)
    
    x_normal = x_arr[normal_mask]
    y_normal = y_arr[normal_mask]
    x_outlier = x_arr[outlier_mask]
    y_outlier = y_arr[outlier_mask]
    
    return x_normal, y_normal, x_outlier, y_outlier, outlier_count


def prepare_const_x_data(
    y_data: Dict[str, Any],
    x_values: List[float],
) -> Tuple[np.ndarray, np.ndarray]:
    """yデータ列から最初の値を抽出し、x値とペアにします。

    Args:
        y_data (Dict[str, Any]): yデータの辞書。
        x_values (List[float]): x値のリスト。

    Returns:
        Tuple[np.ndarray, np.ndarray]: (x配列, y配列) のタプル。

    Raises:
        ValueError: x_valuesの長さとy_dataの長さが一致しない場合。
    """
    if len(x_values) != len(y_data):
        raise ValueError(f"x_valuesの長さ({len(x_values)})とy_columnsの長さ({len(y_data)})が一致しません")

    y_vals_list = []
    
    for col_vals in y_data.values():
        val_to_append = float('nan')
        # Check if array-like
        if hasattr(col_vals, '__len__'):
             if len(col_vals) > 0:
                 try:
                     val = col_vals[0]
                     val_to_append = float(val) if val is not None else float('nan')
                 except:
                     pass
        elif np.isscalar(col_vals):
             try:
                 val_to_append = float(col_vals)
             except:
                 pass
             
        y_vals_list.append(val_to_append)

    x_arr = np.array(x_values)
    y_arr = np.array(y_vals_list)
    
    return x_arr, y_arr
