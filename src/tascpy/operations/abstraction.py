from typing import Callable, Optional, Union, List, Any, Dict
import functools
import numpy as np
from ..core.collection import ColumnCollection
from ..core.column import detect_column_type

def transform_column(
    num_inputs: int = 1,
    result_naming: Union[str, Callable[..., str]] = None,
    unit_inference: Optional[Callable[..., Optional[str]]] = None,
    handle_none: str = "nan",  # 'nan', 'pass'
):
    """
    Decorator for column transformation operations.
    
    Args:
        num_inputs: Number of column arguments expected.
        result_naming: Format string or callable to generate result column name.
        unit_inference: Callable to infer unit result. Receives (collection, *args, **kwargs).
        handle_none: How to handle None values in input.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(collection: ColumnCollection, *args, **kwargs):
            # 1. Parse arguments assume signature: (collection, col1, col2..., result_column=None, in_place=False, unit=None, ch=None, ...)
            
            # Extract column names from args based on num_inputs
            if len(args) < num_inputs:
                pass

            input_args = args[:num_inputs]
            
            # Extract common kwargs
            result_column = kwargs.get("result_column")
            in_place = kwargs.get("in_place", False)
            unit = kwargs.get("unit")
            ch = kwargs.get("ch")
            
            # 2. Validate inputs & Expectation
            input_values = []
            source_column_objs = []
            
            for arg in input_args:
                if isinstance(arg, str) and arg in collection.columns:
                    source_column_objs.append(collection[arg])
                    vals = collection[arg].values
                    if handle_none == "nan":
                        if isinstance(vals, np.ndarray) and np.issubdtype(vals.dtype, np.number):
                            input_values.append(vals.astype(float))
                        else:
                            input_values.append(np.array([v if v is not None else np.nan for v in vals], dtype=float))
                    else:
                        input_values.append(vals)
                else:
                    if isinstance(arg, str):
                         raise KeyError(f"列 '{arg}' が存在しません")
                    input_values.append(arg)

            # 3. Prepare Result Object
            result_collection = collection if in_place else collection.clone()
            
            # 4. Execute Logic
            other_args = args[num_inputs:]
            
            try:
                res_data = func(*input_values, *other_args, **kwargs)
            except Exception as e:
                raise e

            # 5. Post-process result
            if handle_none == "nan" and isinstance(res_data, np.ndarray):
                 result_values = [None if np.isnan(v) else v for v in res_data]
            else:
                 result_values = res_data

            # 6. Determine Result Column Name
            if result_column is None:
                if isinstance(result_naming, str):
                    try:
                        result_column = result_naming.format(*args)
                    except:
                        result_column = f"result_{len(collection.columns)}"
                elif callable(result_naming):
                    result_column = result_naming(func.__name__, *args, **kwargs)
                else:
                     result_column = f"{func.__name__}({args[0]})"

            # 7. Add to Collection
            if result_column in result_collection.columns:
                result_collection.columns[result_column].values = result_values
                if unit is not None:
                     result_collection.columns[result_column].unit = unit
                if ch is not None:
                     result_collection.columns[result_column].ch = ch
            else:
                # Infer unit if not provided
                if unit is None:
                    if unit_inference is not None:
                        unit = unit_inference(collection, *args, **kwargs)
                    elif source_column_objs:
                        unit = getattr(source_column_objs[0], "unit", None)
                
                new_col = detect_column_type(ch, result_column, unit, result_values)
                result_collection.add_column(result_column, new_col)
                
            return result_collection

        return wrapper
    return decorator


def handle_zero_division(
    numerator_idx: int = 0,
    denominator_idx: int = 1,
    default_behavior: str = "error"
):
    """
    Decorator to handle zero division checks and post-processing.
    Intended to be used inside @transform_column.
    
    Args:
        numerator_idx: Index of numerator argument in args.
        denominator_idx: Index of denominator argument in args.
        default_behavior: Default handling mode ('error', 'none', 'inf').
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            mode = kwargs.get("handle_zero_division", default_behavior)
            valid_modes = ["error", "none", "inf"]
            if mode not in valid_modes:
                 raise ValueError(f"handle_zero_division must be one of {valid_modes}")

            v1 = args[numerator_idx]
            v2 = args[denominator_idx]

            # 1. Pre-computation checks (Error mode)
            if mode == "error":
                if np.isscalar(v2):
                    if v2 == 0:
                        raise ValueError("ゼロによる除算が発生しました")
                else:
                    # Check for 0 in denominator where numerator is valid
                    # Assuming v1, v2 are numpy arrays (guaranteed by transform_column if inputs present)
                    
                    # Convert to array if not already (safeguard)
                    v2_arr = np.array(v2) if not isinstance(v2, np.ndarray) else v2
                    v1_arr = np.array(v1) if not isinstance(v1, np.ndarray) else v1
                    
                    if np.issubdtype(v2_arr.dtype, np.number):
                        # Use a mask for efficiency
                        # Zero div is only an error if denominator is 0.
                        # Usually we care if 0/0 or X/0.
                        # Strict mode: any 0 in denominator is error? 
                        # Or only if numerator is valid?
                        # Original logic: `(v2_arr == 0) & (~np.isnan(v1_arr))`
                        # But wait, v1 might be scalar.
                        
                        is_zero = (v2_arr == 0)
                        if np.any(is_zero):
                            # Check numerator validity at those positions
                            if np.isscalar(v1_arr):
                                if not np.isnan(v1_arr):
                                     raise ValueError("ゼロによる除算が発生しました")
                            else:
                                if np.any(~np.isnan(v1_arr[is_zero])):
                                     raise ValueError("ゼロによる除算が発生しました")

            # 2. Execution with suppressed warnings
            with np.errstate(divide='ignore', invalid='ignore'):
                result = func(*args, **kwargs)

            # 3. Post-processing
            if mode == "none":
                # Replace inf/-inf with nan
                if np.isscalar(result):
                    if np.isinf(result):
                        return np.nan
                else:
                    # result might be read-only if it's a view? 
                    # transform_column usually creates new arrays or simple logic returns new array.
                    if isinstance(result, np.ndarray):
                        # Ensure writable
                        if not result.flags.writeable:
                            result = result.copy()
                        result[np.isinf(result)] = np.nan
            
            return result
        return wrapper
    return decorator


def aggregate_column(
    column_arg_index: int = 0
):
    """
    Decorator for aggregation operations (Collection -> Scalar).
    Handles input validation and None filtering.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(collection: ColumnCollection, *args, **kwargs):
            # Identify the column name arg
            if len(args) > column_arg_index:
                col_name = args[column_arg_index]
            else:
                # Start kwargs check? simpler to assume positional for now
                pass
                
            if isinstance(col_name, str) and col_name in collection.columns:
                pass
            elif isinstance(col_name, str):
                 raise KeyError(f"列 '{col_name}' が存在しません")
            
            return func(collection, *args, **kwargs)
        return wrapper
    return decorator
