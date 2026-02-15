from typing import Callable, Optional, Union, List, Any, Dict
import functools
import numpy as np
from ..core.collection import ColumnCollection
from ..core.column import detect_column_type


def inject_columns(num_inputs: int = 1):
    """
    Decorator to parse arguments and inject column data.
    
    Args:
        num_inputs: Number of positional arguments to treat as columns/values.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(collection: ColumnCollection, *args, **kwargs):
            # Extract column names/values from args
            if len(args) < num_inputs:
                pass # Rely on python arg unpacking or kwargs
            
            input_args = args[:num_inputs]
            other_args = args[num_inputs:]
            
            input_values = []
            source_columns = []
            
            # Identify columns vs constants
            for arg in input_args:
                if isinstance(arg, str) and arg in collection.columns:
                    source_columns.append(collection[arg])
                    input_values.append(collection[arg].values)
                else:
                    if isinstance(arg, str):
                         # If it looks like a column name but isn't found, raise Error
                         # This assumption is consistent with previous transform_column logic
                         raise KeyError(f"列 '{arg}' が存在しません")
                    input_values.append(arg)
            
            # Inject:
            # 1. extracted values (as a list or rewritten args)
            # 2. original collection (needed for store_result potentially?) 
            #    No, store_result wraps this, so store_result sees the return value.
            #    But we need to pass 'source_columns' to downstream or store it?
            #    Decorators stack: @outer @inner def func.
            #    exec: outer(inner(func)).
            #    inner(func) calls func.
            #    We want:
            #    @store_result
            #    @handle_missing
            #    @inject_cols
            #    def add(v1, v2): ...
            #
            #    inject_cols calls add(v1, v2). Returns result.
            #    handle_missing sees result? No, handle_missing needs to process INPUTS before add.
            #    So handle_missing wraps inject_cols?
            #    Order:
            #    @store_result (Last to run, wraps everything)
            #      @handle_missing (Modifies inputs from inject_cols? Or modifies args BEFORE inject_cols?)
            #        @inject_cols (Extracts data from collection)
            #          def func(v1, v2)
            #
            #    Flow:
            #    collection.ops.add("A", "B")
            #    -> store_result wrapper("A", "B")
            #       -> handle_missing wrapper("A", "B") ?? No, handle_missing needs VALUES.
            #       -> inject_cols wrapper("A", "B")
            #          -> extracts v1, v2.
            #          -> calls func(v1, v2).
            #
            #    Wait, if `handle_missing` needs to convert None->NaN, it must run AFTER data extraction (inject_cols) but BEFORE func.
            #    So `inject_columns` should run FIRST (outermost of the inner stack).
            #    
            #    Correct Stacking for `transform_column` facade:
            #    def transform_column(...):
            #       return composite of:
            #          @store_result
            #          @inject_columns  <-- Extracts data
            #          @handle_missing  <-- shape of func is now (v1, v2), checks v1, v2
            #          def func(v1, v2)
            #
            #    Let's trace:
            #    call add(coll, "A", "B")
            #    1. store_result.wrapper(coll, "A", "B")
            #       calls inner(coll, "A", "B")
            #       gets result (np.array)
            #       stores result to coll
            #       returns coll
            #
            #    2. inject_columns.wrapper(coll, "A", "B")
            #       extracts vA, vB
            #       calls inner(vA, vB, *others)
            #
            #    3. handle_missing.wrapper(vA, vB, *others)
            #       converts vA, vB (None->NaN or check strict)
            #       calls func(vA, vB)
            #
            #    4. func(vA, vB) returns result
            #
            #    This looks correct.
            #    However, `store_result` needs access to `source_columns` for unit inference inheritance if no unit provided.
            #    `inject_columns` finds source_columns. How to pass to `store_result`?
            #    `store_result` runs "around" `inject_columns`.
            #    Maybe `inject_columns` can attach metadata to the function object or context?
            #    Or `store_result` re-resolves columns? Re-resolving is safer/easier than shared state magic.
            
            # Pass to inner
            return func(*input_values, *other_args, **kwargs)
            
        return wrapper
    return decorator


def handle_missing_values(strategy: str = "nan"):
    """
    Decorator to handle missing values (None/NaN) in inputs.
    Expected to be placed AFTER @inject_columns (inner).
    
    Args:
        strategy: 
            'nan': Convert None to NaN (for numpy math).
            'strict': Return NaNs immediately if any input contains NaN/None.
            'pass': Do nothing.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # args are now values (arrays or scalars) from inject_columns
            
            processed_args = []
            
            if strategy == "strict":
                # Check for None or NaN in any arg
                for arg in args:
                    if arg is None: 
                        # If strict, what to return? 
                        # We need to return an array of NaNs usually, matching the shape of the data.
                        # But we don't know the shape easily if all are None.
                        # Assuming at least one array if it's a column op.
                        # But wait, `diff` implementation previously checked inputs and returned full_nan.
                        # If we return None here, `store_result` handles it?
                        # Let's say we return None, and store_result interprets it?
                        # Or return a special flag?
                        # Or better: `strict` mode logic usually implies "If any input has ANY NaN, the result is ALL NaN".
                        # But `diff` logic was: "If any input contains None, return all None".
                        # Let's check args for arrays.
                        pass
                        
                    if isinstance(arg, np.ndarray):
                        if np.isnan(arg).any():
                             # Strict Fail -> Return NaN array like arg
                             return np.full_like(arg, np.nan)
                    elif isinstance(arg, list):
                         if None in arg:
                             pass
            
            # 'nan' strategy
            if strategy == "nan":
                for arg in args:
                    if isinstance(arg, np.ndarray) and np.issubdtype(arg.dtype, np.number):
                        processed_args.append(arg.astype(float)) # Ensure float for NaN
                    elif isinstance(arg, list) or (isinstance(arg, np.ndarray) and arg.dtype == object):
                         # Convert list with None to float array with NaN
                         # Helper:
                         try:
                             # Efficient handling for mixed types?
                             # Tascpy Columns are usually lists or object arrays if they have None.
                             vals = [v if v is not None else np.nan for v in arg] if isinstance(arg, (list, np.ndarray)) else arg
                             processed_args.append(np.array(vals, dtype=float))
                         except:
                             processed_args.append(arg)
                    else:
                        processed_args.append(arg)
                
                # Call inner
                try:
                    res = func(*processed_args, **kwargs)
                except Exception as e:
                    raise e
                    
                # Convert NaNs back to None is done in store_result?
                # transform_column previous logic: "Post-process result ... if handle_none=='nan' ... convert"
                # So handle_missing should ideally inverse this? 
                # Or should store_result handle normalization?
                # Let's let store_result handle final cleanup.
                return res

            elif strategy == "strict":
                # Check args for NaN/None
                # If found, return NaN array immediately without calling func
                
                # Find shape reference
                shape_ref = None
                has_missing = False
                
                converted_args = []
                
                for arg in args:
                    # Treat raw inputs (lists with None)
                    if isinstance(arg, (list, np.ndarray)):
                        if shape_ref is None: shape_ref = arg
                        
                        # Check existance of None or NaN
                        if isinstance(arg, list):
                            if None in arg: has_missing = True
                        elif isinstance(arg, np.ndarray):
                            if arg.dtype == object and None in arg: has_missing = True
                            elif np.issubdtype(arg.dtype, np.number) and np.isnan(arg).any(): has_missing = True
                    
                    converted_args.append(arg)
                
                if has_missing:
                    # Return all-NaN array of shape
                    if shape_ref is not None:
                         return np.full(len(shape_ref), np.nan)
                    return np.nan # Scalar case?

                # Proceed
                return func(*args, **kwargs)

            else:
                return func(*args, **kwargs)
                
        return wrapper
    return decorator


def store_result(
    result_naming: Union[str, Callable[..., str]] = None,
    unit_inference: Optional[Callable[..., Optional[str]]] = None,
):
    """
    Decorator to store return value into ColumnCollection.
    Expected to be the OUTERMOST decorator (receiving Collection).
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(collection: ColumnCollection, *args, **kwargs):
            # Parse args to find inputs (for metadata logic)
            # Note: func here is likely `inject_columns` wrapper, so it takes (collection, *args)
            
            # Calls the chain
            res_data = func(collection, *args, **kwargs)
            
            # Prepare basics
            result_column = kwargs.get("result_column")
            in_place = kwargs.get("in_place", False)
            unit = kwargs.get("unit")
            ch = kwargs.get("ch")
            
            result_collection = collection if in_place else collection.clone()

            # Post-process (NaN -> None for list compatibility)
            # Ideally standardizing on NaN for float columns is better, but Tascpy might assume None.
            # verify_abstraction_edge_cases expects None for "none" handling.
            # Let's standardize: If output is float array with NaNs, convert to list with Nones?
            # Or depend on what `detect_column_type` expects?
            # `detect_column_type` handles numpy arrays fine.
            # Previous `transform_column` did: `if handle_none == "nan": ... convert to list with None`
            # We should probably preserve this behavior to pass tests.
            # But `handle_missing` strategy is inside inner loop. `store_result` doesn't know strategy.
            # Let's assume if it's an array and has NaNs, we convert to None for consistency?
            
            result_values = res_data
            if isinstance(res_data, np.ndarray) and np.issubdtype(res_data.dtype, np.number):
                 if np.isnan(res_data).any():
                      result_values = [None if np.isnan(v) else v for v in res_data]
            
            # Naming
            if result_column is None:
                if isinstance(result_naming, str):
                    try:
                        result_column = result_naming.format(*args)
                    except:
                        result_column = f"result_{len(collection.columns)}"
                elif callable(result_naming):
                    result_column = result_naming(func.__name__, *args, **kwargs)
                else:
                    # Fallback if func is wrapper? funcs usually retain __name__ via wraps
                    result_column = f"{func.__name__}({args[0]})"
            
            # Metadata / Add Column
            if result_column in result_collection.columns:
                result_collection.columns[result_column].values = result_values
                if unit is not None:
                     result_collection.columns[result_column].unit = unit
                if ch is not None:
                     result_collection.columns[result_column].ch = ch
            else:
                # Infer unit
                if unit is None:
                    if unit_inference is not None:
                        # unit_inference needs collection and original args
                        unit = unit_inference(collection, *args, **kwargs)
                    else:
                        # Try inherit from first arg column
                        # Need to resolve arg to column again... slightly inefficient but loose coupling.
                        for arg in args:
                            if isinstance(arg, str) and arg in collection.columns:
                                unit = getattr(collection[arg], "unit", None)
                                break
                                
                new_col = detect_column_type(ch, result_column, unit, result_values)
                result_collection.add_column(result_column, new_col)
                
            return result_collection
        return wrapper
    return decorator


def transform_column(
    num_inputs: int = 1,
    result_naming: Union[str, Callable[..., str]] = None,
    unit_inference: Optional[Callable[..., Optional[str]]] = None,
    handle_none: str = "nan",  # 'nan', 'pass'
):
    """
    Facade decorator composed of store_result, handle_missing_values, and inject_columns.
    """
    def decorator(func):
        # Compose from inside out:
        # func 
        # <- handle_missing (operates on values)
        # <- inject_columns (converts coll+args -> values)
        # <- store_result (manages coll, result)
        
        # 1. Handle Missing
        missing_strategy = "nan" if handle_none == "nan" else "pass"
        f_missing = handle_missing_values(strategy=missing_strategy)(func)
        
        # 2. Inject Columns
        f_inject = inject_columns(num_inputs=num_inputs)(f_missing)
        
        # 3. Store Result
        # We need to preserve __name__ for naming logic
        functools.update_wrapper(f_inject, func)
        f_store = store_result(result_naming=result_naming, unit_inference=unit_inference)(f_inject)
        
        return f_store
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
