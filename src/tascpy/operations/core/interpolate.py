from typing import Any, Dict, List, Optional, Union, Callable
import math
import numpy as np

from ...core.collection import ColumnCollection
from ...core.column import NumberColumn, Column
from ...core.step import Step
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
    
    # User specified columns act as "force linear/numeric interpolation"
    # All other columns are interpolated as well, but method depends on type/specification.
    
    if columns is not None:
        for col_name in columns:
            if col_name not in collection.columns:
                raise KeyError(f"列 '{col_name}' が存在しません")
    
    # Strategy:
    # 1. Collect all columns.
    # 2. Identify numeric columns (Linear) vs Other (Nearest).
    # 3. If user specified `columns`, those MUST be numeric/linear.
    # 4. If user DID NOT specify `columns`, auto-detect all numeric columns for linear, others nearest.
    
    for name, col in collection.columns.items():
        raw_data[name] = np.array(col.values)
        
        # Check if this column should be treated as numeric (linear interp)
        is_linear_candidate = False
        
        if columns is not None:
            # User specified list
            if name in columns:
                if not isinstance(col, NumberColumn):
                     raise TypeError(f"列 '{name}' は数値型ではありません")
                if col.count_nones() > 0:
                     raise ValueError(f"列 '{name}' にNone値が含まれています")
                is_linear_candidate = True
            else:
                # Not in user list -> Nearest Neighbor (even if numeric)
                is_linear_candidate = False
        else:
            # Auto-detect
            # Check if Column is NumberColumn OR if the underlying data is numeric
            is_numeric_type = False
            if isinstance(col, NumberColumn):
                is_numeric_type = True
            elif np.issubdtype(col.values.dtype, np.number):
                is_numeric_type = True
                
            if is_numeric_type and col.count_nones() == 0:
                is_linear_candidate = True
        
        if is_linear_candidate:
            numeric_keys.append(name)

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
            meta_val = collection.metadata[k]
            # Ensure length matches step
            if len(meta_val) == len(collection.step):
                 meta_to_resample[k] = np.array(meta_val)
            
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
        resampled_all[base_column_name] = new_axis
        
    # Create Columns
    # Need to preserve original column types regarding name, unit, ch
    for name in raw_data.keys():
        if name in resampled_all:
            # Get original column to copy attributes
            orig_col = collection.columns[name]
            new_vals = resampled_all[name]
            
            # Since we interpolated, values might be float even if original was int?
            # functional_interpolate handles this?
            # NumberColumn handles types.
            
            new_col = orig_col.__class__(
                orig_col.ch, orig_col.name, orig_col.unit, new_vals
            )
            new_cols[name] = new_col
            
    # Construct new collection
    # This ensures step and columns are consistent from the start
    return collection.__class__(
        step=Step(final_step_values),
        columns=new_cols,
        metadata=new_metadata
    )




interpolate = register_functional(
    _interpolate_impl,
    domain="core",
    name="interpolate",
)
interpolate.__doc__ = """指定した列の値を基準にしてデータを内挿（リスサンプリング）します

    Args:
        collection (ColumnCollection): データコレクション
        base_column_name (str, optional): 新たな共有x軸として設定するカラム名. Defaults to "step".
        x_values (List[float], optional): 明示的な新しいx軸の配列. Defaults to None.
        point_count (int, optional): 自動生成時の内挿点数. Defaults to None.
        method (str, optional): 補間方法 ("linear", "nearest" 等). Defaults to "linear".
        columns (List[str], optional): 明示的に線形補間対象とするカラム名のリスト. 未指定時はすべて自動判定. Defaults to None.
        
    Returns:
        ColumnCollection: 内挿後のデータを持つ新しいコレクション
"""

