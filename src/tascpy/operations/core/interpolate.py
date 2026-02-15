from typing import Any, Dict, List, Optional, Union, Callable
import math
import numpy as np

from ...core.collection import ColumnCollection
from ...core.column import NumberColumn, Column
from ..registry import operation


# ---------------------------------------------------------
# Pure Functions
# ---------------------------------------------------------

def _interpolate_core(
    base_values: np.ndarray,
    numeric_data: Dict[str, np.ndarray],
    other_data: Dict[str, np.ndarray],
    new_axis: np.ndarray,
    method: str = "linear"
) -> Dict[str, np.ndarray]:
    """
    Pure function for interpolation.
    
    Args:
        base_values: Original x-axis values (must be 1D array).
        numeric_data: Dictionary of numeric arrays to interpolate (linear).
        other_data: Dictionary of non-numeric arrays to interpolate (nearest).
        new_axis: New x-axis values.
        method: Interpolation method for numeric data (currently only 'linear').
        
    Returns:
        Dictionary containing all resampled data (numeric + other).
    """
    resampled_data = {}
    
    # Check monotonicity for np.interp (it requires sorted x)
    # Using a heuristic: if not sorted, we sort.
    # Step is typically sorted. If not, np.interp results might be garbage.
    # Sorting is O(N log N).
    
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
        # np.interp handles extrapolation linearly if left/right not provided?
        # No, defaults to constant (fp[0], fp[-1]).
        # Original implementation did linear extrapolation.
        # np.interp does NOT extrapolation linearly by default.
        # We need to handle extrapolation manually or use scipy.interpolate.interp1d(fill_value="extrapolate")
        # Trying to avoid scipy dependency in core if possible.
        
        # Linear Extrapolation with numpy:
        # Calculate slope at ends?
        
        # For simplicity and performance, standard np.interp is often accepted, 
        # but if requirement matches pure python one (extrapolation), we need it.
        # The pure python did linear extrapolation.
        
        # Let's use a helper for extrapolation or enable it.
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
    # Find indices of nearest base_value for each new_val
    # np.searchsorted gives insertion points.
    # Closest is either idx or idx-1.
    
    if other_data:
        # Logic: find insertion index.
        idx = np.searchsorted(base_values, new_axis, side="left")
        
        # Clip types to valid range for indexing
        idx = np.clip(idx, 0, len(base_values) - 1)
        
        # Check if previous index is closer
        # Compute distances
        # Left neighbor: base_values[idx-1] (careful with 0)
        # Right neighbor: base_values[idx]
        
        # This nearest logic is tricky with just searchsorted.
        # 'abs(xi - x_value)' minimization is O(N*M).
        # Optimization:
        # idx is right neighbor (or exact).
        # dist_right = abs(base[idx] - new)
        # dist_left = abs(base[idx-1] - new)
        
        # Refine idx:
        
        # Ensure idx is within bounds for checking neighbors
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


# ---------------------------------------------------------
# Operation
# ---------------------------------------------------------

@operation(domain="core")
def interpolate(
    collection: ColumnCollection,
    base_column_name: str = "step",  # デフォルトでステップを使用
    x_values: Optional[List[float]] = None,
    point_count: Optional[int] = None,
    method: str = "linear",  # 現状はlinearのみサポート
    columns: Optional[List[str]] = None,
) -> ColumnCollection:
    """指定した列の値に基づいてデータを内挿します"""
    
    # 1. 基準軸データの取得とバリデーション
    if base_column_name == "step":
        base_values = np.array(collection.step.values)
    elif base_column_name not in collection.columns:
        raise KeyError(f"列 '{base_column_name}' が存在しません")
    else:
        column = collection[base_column_name]
        if not isinstance(column, NumberColumn):
            raise TypeError(f"列 '{base_column_name}' は数値型ではありません")
        if column.count_nones() > 0:
            raise ValueError(f"列 '{base_column_name}' にNone値が含まれています")
        base_values = np.array(column.values)

    # 2. 新しい軸（new_axis）の計算
    if x_values is None and point_count is None:
        raise ValueError("x_valuesまたはpoint_countのいずれかを指定してください")
    if x_values is not None and point_count is not None:
        raise ValueError("x_valuesとpoint_countは同時に指定できません")

    if x_values is not None:
        new_axis = np.array(x_values)
    else:
        min_val = np.min(base_values)
        max_val = np.max(base_values)
        if point_count <= 1:
            new_axis = np.array([min_val])
        else:
            new_axis = np.linspace(min_val, max_val, point_count)
    
    # 3. データの準備 (Numeric vs Other)
    target_numeric = {}
    target_other = {}
    
    all_col_names = list(collection.columns.keys())
    
    if columns is None:
        # Default: All valid NumberColumns are numeric, rest are other
        for name in all_col_names:
            col = collection[name]
            # Convert to numpy array safely
            vals = np.array(col.values)
            
            if isinstance(col, NumberColumn) and col.count_nones() == 0:
                 target_numeric[name] = vals
            else:
                 target_other[name] = vals
    else:
        # User specified columns
        for name in columns:
            if name not in collection.columns:
                raise KeyError(f"列 '{name}' が存在しません")
            col = collection[name]
            if not isinstance(col, NumberColumn):
                raise TypeError(f"列 '{name}' は数値型ではありません")
            if col.count_nones() > 0:
                raise ValueError(f"列 '{name}' にNone値が含まれています")
            target_numeric[name] = np.array(col.values)
            
        for name in all_col_names:
            if name not in columns:
                target_other[name] = np.array(collection[name].values)
                
    # Handle base_column (remove from map if present to avoid self-interpolation artifacts,
    # though technically it should interpolate to identity)
    # Actually, base_column SHOULD be interpolated to match new_axis perfectly.
    # The result should contain base_column with new_axis values.
    # We'll inject it manually later.
    
    # 4. Step handling
    # Step itself needs to be interpolated if base is not step
    # If base is step, step becomes new_axis.
    step_is_base = (base_column_name == "step")
    original_step_vals = np.array(collection.step.values)
    
    if not step_is_base:
        # Add step to numeric data if it's numeric and valid, else other
        # Step is usually numeric.
        # But wait, we want Step to be interpolated based on BASE COLUMN.
        # So treating Step as just another column data-wise is correct.
        # But we need to separate it because it goes into .step property.
        if np.issubdtype(original_step_vals.dtype, np.number) and not np.isnan(original_step_vals).any():
             target_numeric["__step__"] = original_step_vals
        else:
             target_other["__step__"] = original_step_vals

    # 5. Metadata handling (nearest)
    # Extract list-like metadata for interpolation
    meta_to_resample = {}
    meta_keys = ["date", "time"]
    for k in meta_keys:
        if k in collection.metadata and collection.metadata[k]:
            meta_to_resample[k] = np.array(collection.metadata[k])
            
    # Combine meta into other_data for processing (using prefix to avoid collision)
    for k, v in meta_to_resample.items():
        target_other[f"__meta_{k}__"] = v

    # 6. Execution
    resampled_all = _interpolate_core(
        base_values, target_numeric, target_other, new_axis, method=method
    )
    
    # 7. Reconstruction
    new_cols = {}
    new_metadata = collection.metadata.copy()
    new_metadata.update({"interpolation_method": method, "interpolation_basis": base_column_name})
    
    # Extract Step
    final_step_values = new_axis if step_is_base else resampled_all.pop("__step__", [])
    if isinstance(final_step_values, np.ndarray):
        final_step_values = final_step_values.tolist()
        
    # Extract Metadata
    for k in meta_keys:
        key = f"__meta_{k}__"
        if key in resampled_all:
             new_metadata[k] = resampled_all.pop(key).tolist()

    # Base column injection (if not step)
    if not step_is_base and base_column_name in collection.columns:
        # Override with exact new_axis values
        # If base_column was in calculation, it's in resampled_all.
        # But we want to ensure it matches new_axis exactly.
        # But wait, if we interpolated it, it should be close.
        # Let's trust pure new_axis for precision.
        resampled_all[base_column_name] = new_axis

    # Build Columns
    for name, vals in resampled_all.items():
        if name in collection.columns:
            orig_col = collection[name]
            new_col = orig_col.clone()
            new_col.values = vals.tolist()
            new_cols[name] = new_col
            
    result = collection.clone()
    result.step = result.step.__class__(values=final_step_values)
    result.columns = new_cols
    result.metadata = new_metadata
    
    return result

