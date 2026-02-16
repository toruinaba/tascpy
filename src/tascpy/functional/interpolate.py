from typing import Dict
import numpy as np

def interpolate_core(
    base_values: np.ndarray,
    numeric_data: Dict[str, np.ndarray],
    other_data: Dict[str, np.ndarray],
    new_axis: np.ndarray,
    method: str = "linear"
) -> Dict[str, np.ndarray]:
    """
    Pure function for interpolation.
    resamples numeric_data and other_data based on base_values to new_axis.
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
