from typing import Any, Dict, List, Optional, Union, Callable
import math
import numpy as np

from ...core.collection import ColumnCollection
from ...core.column import NumberColumn, Column
from ..registry import register_functional
from ...functional import interpolate as functional_interpolate


# ---------------------------------------------------------
# Pure Functions
# ---------------------------------------------------------




# ---------------------------------------------------------
# Operation
# ---------------------------------------------------------



def _interpolate_impl(
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
    new_axis = functional_interpolate.calculate_new_axis(
        base_values, x_values, point_count
    )
    
    # 3. データの準備 (Numeric vs Other)
    # Extract all data first
    raw_data = {}
    numeric_keys = []
    
    if columns is None:
        # Default: All valid NumberColumns are numeric candidates
        for name, col in collection.columns.items():
            raw_data[name] = np.array(col.values)
            if isinstance(col, NumberColumn) and col.count_nones() == 0:
                numeric_keys.append(name)
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
            numeric_keys.append(name)
            
        for name, col in collection.columns.items():
            raw_data[name] = np.array(col.values)

    target_numeric, target_other = functional_interpolate.partition_data(
        raw_data, numeric_keys
    )
                
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
    resampled_all = functional_interpolate.interpolate_core(
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


interpolate = register_functional(
    _interpolate_impl,
    domain="core",
    name="interpolate",
)

