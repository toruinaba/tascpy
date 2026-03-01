from typing import Dict, Optional
import numpy as np

def interpolate_core(
    base_values: np.ndarray,
    numeric_data: Dict[str, np.ndarray],
    other_data: Dict[str, np.ndarray],
    new_axis: np.ndarray,
    method: str = "linear"
) -> Dict[str, np.ndarray]:
    """補間処理のコア関数です。

    基準となる値 (base_values) に基づいて、数値データ (numeric_data) とその他のデータ (other_data) を
    新しい軸 (new_axis) にリサンプリングします。
    数値データは線形補間（外挿あり）、その他のデータは最近傍補間を使用します。

    Args:
        base_values (np.ndarray): 元の基準値の配列（x軸など）。
        numeric_data (Dict[str, np.ndarray]): リサンプリング対象の数値データ辞書。
        other_data (Dict[str, np.ndarray]): リサンプリング対象の非数値データ辞書。
        new_axis (np.ndarray): 新しい基準値の配列。
        method (str, optional): 補間方法。現在は "linear" のみが有効です。

    Returns:
        Dict[str, np.ndarray]: リサンプリングされたすべてのデータを含む辞書。
    """
    
    resampled_data = {}
    
    # Sort indices if base_values are not sorted
    # Checking is_monotonic efficiently
    is_sorted = True
    if len(base_values) > 1:
        if not (base_values[1:] >= base_values[:-1]).all():
            is_sorted = False
            
    if not is_sorted:
        # Sort based on base_values
        sort_idx = np.argsort(base_values)
        base_values = base_values[sort_idx]
        # Reorder input data
        numeric_data = {
            name: vals[sort_idx] for name, vals in numeric_data.items()
        }
        other_data = {
            name: vals[sort_idx] for name, vals in other_data.items()
        }
        
    # 1. Linear Interpolation for Numeric Data
    for name, values in numeric_data.items():
        # Custom numpy-based linear interp with extrapolation:
        
        # Use np.interp for inside range
        interp_vals = np.interp(new_axis, base_values, values, left=np.nan, right=np.nan)
        
        # Handle Nans (extrapolation) if needed
        # Identify left/right out of bounds
        left_mask = new_axis < base_values[0]
        right_mask = new_axis > base_values[-1]
        
        if np.any(left_mask):
            # Extrapolate Left
            if len(base_values) >= 2:
                x1, x2 = base_values[0], base_values[1]
                y1, y2 = values[0], values[1]
                slope = (y2 - y1) / (x2 - x1) if x2 != x1 else 0
                interp_vals[left_mask] = y1 + slope * (new_axis[left_mask] - x1)
            else:
                 interp_vals[left_mask] = values[0]

        if np.any(right_mask):
            # Extrapolate Right
            if len(base_values) >= 2:
                x1, x2 = base_values[-2], base_values[-1]
                y1, y2 = values[-2], values[-1]
                slope = (y2 - y1) / (x2 - x1) if x2 != x1 else 0
                interp_vals[right_mask] = y2 + slope * (new_axis[right_mask] - x2)
            else:
                interp_vals[right_mask] = values[-1]
        
        resampled_data[name] = interp_vals

    # 2. Nearest Neighbor Interpolation for Other Data
    if other_data:
        # Logic: find insertion index.
        idx = np.searchsorted(base_values, new_axis, side="left")
        
        # Clip types to valid range for indexing
        idx = np.clip(idx, 0, len(base_values) - 1)
        
        # Check if previous index is closer
        idx_right = idx
        idx_left = np.maximum(idx - 1, 0)
        
        dist_right = np.abs(base_values[idx_right] - new_axis)
        dist_left = np.abs(base_values[idx_left] - new_axis)
        
        # Where left is closer
        use_left = dist_left < dist_right
        final_idx = np.where(use_left, idx_left, idx_right)
        
        for name, values in other_data.items():
            resampled_data[name] = values[final_idx]

    return resampled_data


def calculate_new_axis(
    base_values: np.ndarray,
    x_values: Optional[list] = None,
    point_count: Optional[int] = None
) -> np.ndarray:
    """補間用の新しい軸を計算します。

    Args:
        base_values (np.ndarray): 現在の基準値配列。
        x_values (list, optional): 新しい軸の値のリスト。
        point_count (int, optional): 生成する点の数（等間隔）。

    Returns:
        np.ndarray: 計算された新しい軸の配列。

    Raises:
        ValueError: x_values と point_count の両方が指定されていない場合、または両方が指定されている場合。
    """
    if x_values is None and point_count is None:
        raise ValueError("x_valuesまたはpoint_countのいずれかを指定してください")
    if x_values is not None and point_count is not None:
        raise ValueError("x_valuesとpoint_countは同時に指定できません")

    if x_values is not None:
        return np.array(x_values)
    else:
        min_val = np.min(base_values)
        max_val = np.max(base_values)
        if point_count <= 1:
            return np.array([min_val])
        else:
            return np.linspace(min_val, max_val, point_count)


def partition_data(
    data: Dict[str, np.ndarray],
    numeric_keys: Optional[list] = None
) -> tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]:
    """データを数値データとその他のデータに分割します。

    Args:
        data (Dict[str, np.ndarray]): 分割対象のデータ辞書。
        numeric_keys (list, optional): 数値として扱うキーのリスト。Noneの場合は自動判定を試みます。

    Returns:
        tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]: 
            (数値データ辞書, その他のデータ辞書) のタプル。
    """
    numeric_data = {}
    other_data = {}
    
    for key, val in data.items():
        is_numeric = False
        if numeric_keys is not None:
            if key in numeric_keys:
                is_numeric = True
        else:
            # Auto-detect
            if np.issubdtype(val.dtype, np.number):
                # Check for object arrays that might be numeric? 
                # Ideally, val should already be cast if possible.
                is_numeric = True
                
        if is_numeric:
            numeric_data[key] = val
        else:
            other_data[key] = val
            
    return numeric_data, other_data
