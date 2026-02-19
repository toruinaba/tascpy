from typing import Callable, Optional, Union, List, Any, Dict
import functools
import numpy as np
from ..core.collection import ColumnCollection
from ..core.column import detect_column_type
from ..core.step import Step


def inject_columns(
    num_inputs: int = 1, 
    cast_to_numpy: bool = True,
    columns_arg: str = None,
    columns_arg_pos: int = None,
    include_step: bool = False
):
    """
    Decorator to parse arguments and inject column data.
    
    Args:
        num_inputs: Number of positional arguments to treat as columns/values.
        cast_to_numpy: If True, converts injected values to numpy arrays (if they are lists).
        columns_arg: If specified, looks for this argument (list of column names) and replaces it 
                     with a dictionary {col_name: values}. If the argument is None, it may default 
                     to all columns if the inner function supports it.
        include_step: If True, injects the collection's step values as the first argument.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(collection: Union[ColumnCollection, Any], *args, **kwargs):
            # Check if operating on a ColumnCollection or raw data
            if not isinstance(collection, ColumnCollection):
                # Raw data mode: Assume arguments are already values
                all_args = (collection,) + args
                
                # Apply cast_to_numpy if needed for raw inputs?
                # Usually raw inputs are passed as is, but if we want to reduce boilerplate
                # we should cast them here too.
                if cast_to_numpy:
                    new_args = []
                    for arg in all_args:
                        if isinstance(arg, list):
                            new_args.append(np.array(arg))
                        else:
                            new_args.append(arg)
                    return func(*new_args, **kwargs)
                
                return func(*all_args, **kwargs)

            # --- ColumnCollection Mode ---
            
            # Prepare Step Injection
            step_values = None
            if include_step:
                step_val = collection.step.values
                if cast_to_numpy and isinstance(step_val, list):
                    step_values = np.array(step_val)
                else:
                    step_values = step_val

            # 1. Handle Multi-Column Injection (if columns_arg is set)
            if columns_arg:
                # Find the target columns list
                target_cols = kwargs.get(columns_arg)
                
                # If not in kwargs, check positional args? 
                # Ideally mixed usage is tricky. Let's assume kwargs for clarity or 
                # specific position if num_inputs used differently.
                # For `filter_out_none(col, columns=...)`, it's clear.
                
                # If target_cols is None, input might be explicit None to mean "all".
                # We need to resolve this.
                if target_cols is None:
                    # Check if it was passed positionally?
                    if columns_arg_pos is not None:
                        # Map positional arg to kwargs if present
                        if len(args) > columns_arg_pos:
                             # We need to extract it, but args is tuple.
                             target_cols = args[columns_arg_pos]
                             
                             # We don't remove it from args yet. It will be ignored since we consumed it.

                # Extract dict
                cols_to_extract = target_cols if target_cols is not None else collection.columns.keys()
                
                extracted_data = {}
                for name in cols_to_extract:
                    if name not in collection.columns:
                        raise KeyError(f"列 '{name}' が存在しません")
                    val = collection[name].values
                    if cast_to_numpy and isinstance(val, list):
                        extracted_data[name] = np.array(val)
                    else:
                        extracted_data[name] = val
                
                # We inject this dict. But where? 
                # If the pure function signature is `func(data_dict, mode)`, 
                # then we replace `collection` with `extracted_data`?
                # And we drop `columns` arg since data is already filtered?
                
                # Pure func: filter_out_none(data_dict: Dict, mode: str)
                # Call: filter_out_none(collection, columns=['A'])
                
                # So we pass `extracted_data` as the first argument (replacing collection).
                # And we ensure `columns_arg` is NOT passed to the inner function, 
                # OR the inner function expects it.
                
                # Let's assume the pure function signature becomes:
                # def filter_out_none(data: Dict[str, Any], columns: Optional[List[str]] = None, ...)
                # But if we inject data, `columns` arg becomes redundant for data access, 
                # though maybe needed for metadata?
                
                # Simplest for now: Inject as first arg.
                # If columns_arg was in kwargs, remove it?
                new_kwargs = kwargs.copy()
                if columns_arg in new_kwargs:
                    del new_kwargs[columns_arg]
                    
                # NOTE: We ignore `num_inputs` if `columns_arg` is used? 
                # Or do we support both? E.g. search(col, "A", val) -> num_inputs=1 ('A'->val)
                # filter_out_none(col, columns=["A"]) -> columns_arg="columns".
                
                final_args = list(args)
                if include_step:
                     # func(steps, extracted_data, ...)
                     # If we found target_cols in args, we should probably REMOVE it from final_args
                     # to avoid passing it to inner function (which expects injected data now)
                     _final_args_list = list(final_args)
                     if columns_arg_pos is not None and columns_arg not in kwargs and len(_final_args_list) > columns_arg_pos:
                          # Assuming columns_arg_pos is index in *args (excluding collection)
                          _final_args_list.pop(columns_arg_pos)
                     
                     return func(step_values, extracted_data, *_final_args_list, **new_kwargs)
                else:
                     _final_args_list = list(final_args)
                     if columns_arg_pos is not None and columns_arg not in kwargs and len(_final_args_list) > columns_arg_pos:
                          _final_args_list.pop(columns_arg_pos)
                          
                     return func(extracted_data, *_final_args_list, **new_kwargs)


            # Resolve input arguments
            args_list = list(args)
            input_values = []
            
            # Prepend step if requested
            if include_step:
                input_values.append(step_values)

            for i in range(num_inputs):
                val_source = None
                
                # 1. Try positional
                if len(args_list) > 0:
                     val_source = args_list.pop(0)
                
                # 2. Start fallback strategies for specific standard args
                # We assume the first input maps to "column" if not provided positionally
                elif i == 0 and "column" in kwargs:
                     val_source = kwargs.pop("column")
                     
                if val_source is None:
                     # Wait, if we haven't found it, do we prefer to send nothing?
                     # The inner function likely expects a value.
                     # If we send nothing, func() raises TypeError.
                     # Proceeding allows catching it later or optional args.
                     pass 
                
                if val_source is not None:
                    if isinstance(val_source, str) and val_source in collection.columns:
                        val = collection[val_source].values
                        if cast_to_numpy and isinstance(val, list):
                            input_values.append(np.array(val))
                        else:
                            input_values.append(val)
                    elif isinstance(val_source, str):
                        raise KeyError(f"列 '{val_source}' が存在しません")
                    else:
                        input_values.append(val_source)
            
            return func(*input_values, *args_list, **kwargs)
            
        return wrapper
    return decorator


def inject_step_values(func=None, *, cast_to_numpy: bool = True):
    """
    Decorator to inject the collection's step values as the first argument.
    Used for operations that depend on the step (like time or index), e.g., select.
    
    Can be used as @inject_step_values or @inject_step_values(cast_to_numpy=False).
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(collection: Union[ColumnCollection, Any], *args, **kwargs):
            # Check raw input
            if not isinstance(collection, ColumnCollection):
                # Assume collection IS the step_values
                steps = collection
                if cast_to_numpy and isinstance(steps, list):
                    steps = np.array(steps)
                return f(steps, *args, **kwargs)

            # Apply filter_rows pattern: collection is first arg.
            # We extract step.values
            step_values = collection.step.values
            if cast_to_numpy and isinstance(step_values, list):
                step_values = np.array(step_values)
            
            return f(step_values, *args, **kwargs)
        return wrapper

    if func is None:
        return decorator
    else:
        return decorator(func)


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
            
            # 'nan' strategy
            if strategy == "nan":
                for arg in args:
                    if isinstance(arg, np.ndarray) and np.issubdtype(arg.dtype, np.number):
                        processed_args.append(arg.astype(float)) # Ensure float for NaN
                    elif isinstance(arg, np.ndarray) and arg.dtype == object:
                        # Attempt to cast object array to float/nan
                        try:
                            vals = [v if v is not None else np.nan for v in arg]
                            processed_args.append(np.array(vals, dtype=float))
                        except:
                            processed_args.append(arg)
                    elif isinstance(arg, list):
                         # Convert list with None to float array with NaN
                         try:
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
                            if arg.dtype == object:
                                if None in arg: 
                                    has_missing = True
                                else:
                                    # vector check for nan in object/float mix
                                    # safe check
                                    is_nan = np.vectorize(lambda x: isinstance(x, float) and np.isnan(x))(arg)
                                    if is_nan.any(): has_missing = True
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
    func: Optional[Callable] = None,
    *,
    result_naming: Union[str, Callable[..., str]] = None,
    unit_inference: Optional[Callable[..., Optional[str]]] = None,
    inject_metadata: Optional[Callable[[tuple, dict, Any], Dict[str, Any]]] = None,
):
    """
    Decorator to store return value into ColumnCollection.
    Expected to be the OUTERMOST decorator (receiving Collection).
    """
    def decorator(target_func):
        @functools.wraps(target_func)
        def wrapper(collection: Union[ColumnCollection, Any], *args, **kwargs):
            # Pass through if not collection
            if not isinstance(collection, ColumnCollection):
                 all_args = (collection,) + args
                 return target_func(*all_args, **kwargs)

            # Extract and consume metadata arguments
            # We copy kwargs to avoid side effects if func modifies it, 
            # and to pass cleaned kwargs to func.
            func_kwargs = kwargs.copy()
            result_column = func_kwargs.pop("result_column", None)
            in_place = func_kwargs.pop("in_place", False)
            unit = func_kwargs.pop("unit", None)
            ch = func_kwargs.pop("ch", None)

            # Calls the chain with cleaned kwargs
            res_data = target_func(collection, *args, **func_kwargs)
            
            # Check for (values, metadata) tuple
            metadata_update = {}
            if isinstance(res_data, tuple) and len(res_data) == 2:
                 # Heuristic: Check if second element is dict
                 if isinstance(res_data[1], dict):
                      res_data, metadata_update = res_data
            
            result_collection = collection if in_place else collection.clone()
            
            # Apply metadata update
            if metadata_update:
                 result_collection.metadata.update(metadata_update)

            # Post-process (NaN -> None for list compatibility)
            result_values = res_data
            if isinstance(res_data, np.ndarray) and np.issubdtype(res_data.dtype, np.number):
                 if np.isnan(res_data).any():
                      result_values = [None if np.isnan(v) else v for v in res_data]
            
            # Naming
            if result_column is None:
                if isinstance(result_naming, str):
                    try:
                        result_column = result_naming.format(*args, **kwargs)
                    except:
                        result_column = f"result_{len(collection.columns)}"
                elif callable(result_naming):
                    result_column = result_naming(func.__name__ if func else target_func.__name__, *args, **kwargs)
                else:
                    # Fallback if func is wrapper? funcs usually retain __name__ via wraps
                    if len(args) > 0:
                        result_column = f"{target_func.__name__}({args[0]})"
                    else:
                        result_column = f"{target_func.__name__}_result"
            
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
                        for arg in args:
                            if isinstance(arg, str) and arg in collection.columns:
                                unit = getattr(collection[arg], "unit", None)
                                break
                                
                new_col = detect_column_type(ch, result_column, unit, result_values)
                result_collection.add_column(result_column, new_col)

            # Metadata Injection
            if inject_metadata is not None:
                try:
                    # Pass original args/kwargs and the raw result result_values (or the processed one?)
                    # Usually we want to know what happened.
                    # let's pass (args, kwargs, result_values)
                    # Note: args are tuple of user inputs excluding collection.
                    extra_meta = inject_metadata(args, kwargs, result_values)
                    if extra_meta and isinstance(extra_meta, dict):
                         result_collection.metadata.update(extra_meta)
                except Exception as e:
                    # Metadata injection shouldn't crash the op? Or should it? 
                    # Let's warn and continue or raise? User code -> Raise.
                    raise e
            
            return result_collection
        return wrapper

    if func is not None:
        return decorator(func)
    return decorator


def transform_column(
    num_inputs: int = 1,
    result_naming: Union[str, Callable[..., str]] = None,
    unit_inference: Optional[Callable[..., Optional[str]]] = None,
    handle_none: str = "nan",  # 'nan', 'pass'
    inject_metadata: Optional[Callable[[tuple, dict, Any], Dict[str, Any]]] = None,
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
        f_store = store_result(
            result_naming=result_naming, 
            unit_inference=unit_inference,
            inject_metadata=inject_metadata
        )(f_inject)
        
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
                    # Convert to array if not already (safeguard)
                    v2_arr = np.array(v2) if not isinstance(v2, np.ndarray) else v2
                    v1_arr = np.array(v1) if not isinstance(v1, np.ndarray) else v1
                    
                    if np.issubdtype(v2_arr.dtype, np.number):
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
        def wrapper(collection: Union[ColumnCollection, Any], *args, **kwargs):
            # Pass through if not collection
            if not isinstance(collection, ColumnCollection):
                 all_args = (collection,) + args
                 return func(*all_args, **kwargs)
        
            # Identify the column name arg
            if len(args) > column_arg_index:
                col_name = args[column_arg_index]
            else:
                pass
                
            if isinstance(col_name, str) and col_name in collection.columns:
                pass
            elif isinstance(col_name, str):
                 raise KeyError(f"列 '{col_name}' が存在しません")
            
            return func(collection, *args, **kwargs)
        return wrapper
    return decorator


def select_columns(
    arg_name: str = "columns"
):
    """
    Decorator to filter columns of the collection before operation.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(collection: Union[ColumnCollection, Any], *args, **kwargs):
            # Pass through if not collection
            if not isinstance(collection, ColumnCollection):
                 all_args = (collection,) + args
                 return func(*all_args, **kwargs)

            target_columns = kwargs.get(arg_name)
            
            if target_columns is None and len(args) > 0:
                 if args[0] is None or (isinstance(args[0], list) and (len(args[0])==0 or isinstance(args[0][0], str))):
                     target_columns = args[0]

            if target_columns is not None:
                # Validation
                for col_name in target_columns:
                    if col_name not in collection.columns:
                        raise KeyError(f"列 '{col_name}' が存在しません")
                
                # Clone with subset
                filtered_columns = {
                    name: collection.columns[name].clone() 
                    for name in target_columns
                }
                
                working_collection = collection.clone()
                working_collection.columns = filtered_columns
            else:
                working_collection = collection 
                
            return func(working_collection, *args, **kwargs)
        return wrapper
    return decorator


def filter_rows(func):
    """
    Decorator that expects the function to return indices (list/array) or boolean mask.
    It takes those indices and returns a filtered ColumnCollection.
    """
    @functools.wraps(func)
    def wrapper(collection: Union[ColumnCollection, Any], *args, **kwargs):
        # Pass through if not collection
        if not isinstance(collection, ColumnCollection):
             all_args = (collection,) + args
             return func(*all_args, **kwargs)

        # Run the function to get indices
        result = func(collection, *args, **kwargs)
        
        # Result might be just indices, or tuple (indices, metadata_update)
        metadata_update = {}
        if isinstance(result, tuple):
            indices, metadata_update = result
        else:
            indices = result
            
        if indices is None:
             res_collection = collection.clone()
        else:
             res_collection = collection.clone() # Start with a clone to modify
             
             if len(indices) == 0:
                 # Empty result
                 res_collection.step.values = []
                 for name in res_collection.columns:
                     res_collection.columns[name].values = []
             else:
                 # Filter step
                 # Ensure we work with numpy arrays for indexing
                 current_steps = np.array(collection.step.values)
                 
                 try:
                     filtered_steps = current_steps[indices]
                 except IndexError:
                     raise IndexError("指定されたインデックスが範囲外です")
                     
                 if isinstance(collection.step.values, list):
                     filtered_steps = filtered_steps.tolist()
                 
                 # Assign back to step (setter handles validation now!)
                 # Validation might fail if we set step before columns, or columns before step?
                 # Setter checks against existing columns.
                 # If we update columns first, they become short, then update step.
                 # Or update step first?
                 # If we update step first, it checks against OLD columns (length mismatch).
                 # If we update columns first, valid?
                 # Wait, setter checks: "New step length ... does not match existing columns length"
                 # So if we update step to shorter, but columns are still long -> Error.
                 # If we update columns to shorter, existing step is long -> Invariant broken temporarily?
                 # `collection.columns[name].values = ...` does NOT trigger collection validation usually.
                 # But `Column` itself doesn't know about collection.
                 # So we can update columns one by one. invariants are checked at boundaries?
                 # No, `add_column` checks. Direct assignment `col.values = ...` is bypass.
                 # But we need to use `res_collection.step = ...`.
                 # To safely update all, we might need to clear columns first?
                 # Or manually set `_step`.
                 
                 # Strategy: Update columns first (bypassing collection-level checks), then update step?
                 # `res_collection.step = ...` check will fail if columns are different length.
                 # If we update all columns to new length, then `res_collection.step = ...` will succeed.
                 
                 # Filter columns
                 filtered_cols = {}
                 for name, col in collection.columns.items():
                     cur_vals = np.array(col.values)
                     new_vals = cur_vals[indices]
                         
                     if isinstance(col.values, list):
                         new_vals = new_vals.tolist()
                         
                     # Direct modification of values in cloned collection's columns
                     # We need to ensure we don't trigger checks yet.
                     # But `res_collection.columns` is a dict.
                     # `res_collection.columns[name]` gives Column object.
                     # `col.values = ...` is safe.
                     
                     # We create NEW column objects to be safe
                     new_col = col.__class__(col.ch, col.name, col.unit, new_vals, col.metadata)
                     res_collection.columns[name] = new_col

                 # Now all columns are short.
                 # Set step.
                 # But `res_collection.step` setter checks against `res_collection.columns`.
                 # Since we updated all columns in `res_collection`, they are now short.
                 # So setting short step should be valid!
                 
                 res_collection.step = Step(values=filtered_steps)

        # Update metadata
        if metadata_update:
            res_collection.metadata.update(metadata_update)
            
        return res_collection

    return wrapper



def inject_plot_data(
    x_arg: str = "x_column",
    y_arg: str = "y_column",
    positional_order: Optional[List[str]] = None,
):
    """
    Decorator to extract plot data from ColumnCollection and inject into function.
    Injects: x_values, y_values, x_label, y_label, title
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(collection: Union[ColumnCollection, Any] = None, *args, **kwargs):
            # 1. If x_values and y_values are provided in kwargs, bypass extraction
            # This allows calling plot(x_values=..., y_values=...) directly
            if "x_values" in kwargs and "y_values" in kwargs:
                # If collection was passed (e.g. None or some object), do we pass it? 
                # If plot() does not take collection, we should NOT pass it.
                # But if we are in pass-through mode...
                # Actually, check if func accepts 'collection'? No, we know plot() is pure.
                # If x_values/y_values are passed, we assume we are calling the pure function directly.
                return func(*args, **kwargs)

            # 2. Pass through if not collection (and data not fully provided)
            # This handles plot(arr1, arr2) case where collection=arr1
            if not isinstance(collection, ColumnCollection):
                 # If collection is None (default), and we didn't satisfy condition 1,
                 # it implies missing arguments. But let's pass it through and let func fail or handle.
                 # However, if func is plot(x_values, ...), func(None, ...) maps None to x_values.
                 # If valid usage, this is fine.
                 return func(collection, *args, **kwargs)

            # Extract Column Names
            # Priority: 1. kwargs, 2. args (positional)
            
            x_column = None
            y_column = None
            
            # Check kwargs first
            if x_arg in kwargs:
                x_column = kwargs.pop(x_arg)
            
            if y_arg in kwargs:
                y_column = kwargs.pop(y_arg)
                
            # Check args if not found in kwargs using mutable list
            mutable_args = list(args)
            
            # Determine processing order for positional args
            # Default: x then y
            if positional_order is None:
                order = [x_arg, y_arg]
            else:
                order = positional_order
                
            for arg_name in order:
                if len(mutable_args) == 0:
                     break
                     
                if arg_name == x_arg:
                    if x_column is None:
                        x_column = mutable_args.pop(0)
                        
                elif arg_name == y_arg:
                    if y_column is None:
                        y_column = mutable_args.pop(0)

            # Update args to passed-through args
            args = tuple(mutable_args)
            
            # Extract Data & Metadata
            # X Axis
            x_values, x_name, x_unit = extract_axis_data(collection, x_column, "Step")

            # Y Axis
            y_values, y_name, y_unit = extract_axis_data(collection, y_column, "Step")
            
            # Construct Labels
            x_label = f"{x_name} [{x_unit}]" if x_unit else x_name
            y_label = f"{y_name} [{y_unit}]" if y_unit else y_name
            
            # Construct Default Title (can be overridden by kwargs if needed, but usually passed as arg)
            # We construct it here to standardize
            plot_type = kwargs.get("plot_type", "scatter")
            default_title = f"{plot_type.capitalize()} plot of {y_name} vs {x_name}"
            
            # Inject
            return func(
                x_values=x_values,
                y_values=y_values,
                x_label=x_label,
                y_label=y_label,
                title=default_title,
                *args,
                **kwargs
            )
        return wrapper
    return decorator


def inject_length(func):
    """
    Decorator to inject the collection length as the first argument.
    Usage:
        @split_result
        @inject_length
        def my_split(length: int, ...):
            ...
    </details>
    """
    @functools.wraps(func)
    def wrapper(collection: Union[ColumnCollection, Any], *args, **kwargs):
        # If collection is ColumnCollection, extract length
        if isinstance(collection, ColumnCollection):
             length = len(collection)
             return func(length, *args, **kwargs)
        
        # If collection is already int (testing or manual usage)
        if isinstance(collection, int):
             return func(collection, *args, **kwargs)
             
        # If collection is list/array? (maybe just len() it?)
        try:
             length = len(collection)
             return func(length, *args, **kwargs)
        except TypeError:
             # Fallback or raise?
             # If we can't determine length, pass as is? 
             # No, the function expects int.
             raise TypeError(f"Expected ColumnCollection or length(int), got {type(collection)}")

    return wrapper
def split_result(func):
    """
    Decorator that expects the function to return a list of Step (or lengths/indices) or similar split info,
    and returns a list of ColumnCollections.
    """
    @functools.wraps(func)
    def wrapper(collection: Union[ColumnCollection, Any], *args, **kwargs):
        if not isinstance(collection, ColumnCollection):
             return func(collection, *args, **kwargs)

        # Call inner function
        # Expecting it to return List of Indices/Slices
        split_defs = func(collection, *args, **kwargs)
        
        # Check if tuple (defs, metadata)
        metadata_update = {}
        if isinstance(split_defs, tuple) and len(split_defs) == 2 and isinstance(split_defs[1], dict):
             split_defs, metadata_update = split_defs

        # Optimization: Pre-convert to numpy if needed? 
        # But we don't want to mutate original collection here.
        # Let's trust pure func or handle it inside.
        
        results = []
        
        # Post-process results
        for item in split_defs:
            if isinstance(item, slice):
                # Apply slice
                res = collection[item]
                results.append(res)
            elif isinstance(item, (list, np.ndarray)):
                 # Apply indices
                 # We need to use filter_rows logic here?
                 # Or just delegate to collection slicing by index if supported?
                 # Collection supports integer slicing but not list of integers (yet?)
                 # Actually, filter_rows is what implements list-of-indices slicing logic.
                 # We should expose that logic or reuse filter_rows wrapper logic?
                 
                 # Reusing logic from filter_rows wrapper:
                 # But we can't call a decorated dummy.
                 
                 # Let's implement a helper method `_subset_by_indices` in collection?
                 # Or do it here manually.
                 
                 # Simplified manual implementation for now:
                 indices = np.array(item)
                 
                 # Step
                 step_vals = np.array(collection.step.values)
                 
                 try:
                     new_step = step_vals[indices].tolist()
                 except IndexError:
                     raise IndexError("指定されたインデックスが範囲外です")
                 
                 # Columns
                 new_cols = {}
                 for name, col in collection.columns.items():
                     c_vals = np.array(col.values)
                     new_vals = c_vals[indices].tolist()
                     new_cols[name] = col.__class__(col.ch, col.name, col.unit, new_vals)
                     
                 res = collection.clone()
                 res.step.values = new_step
                 res.columns = new_cols
                 results.append(res)
            else:
                 # Maybe already a Collection?
                 if isinstance(item, ColumnCollection):
                      results.append(item)
                 else:
                      raise TypeError(f"Unsupported split result type: {type(item)}")

        # Update metadata if any
        if metadata_update:
             for res in results:
                  res.metadata.update(metadata_update)

        return results
    return wrapper


def extract_axis_data(
    collection: ColumnCollection, 
    column_name: Optional[str] = None, 
    default_name: str = "Step"
) -> tuple:
    """
    コレクションから軸データ（値、名前、単位）を抽出するヘルパー関数
    
    Args:
        collection: 対象のColumnCollection
        column_name: 列名（Noneの場合はStepを使用）
        default_name: 列名がNoneの場合に使用する名前
        
    Returns:
        (values, name, unit): 値の配列、名前、単位
    """
    if column_name is None:
        values = collection.step.values
        name = default_name
        unit = ""
    else:
        if column_name not in collection.columns:
            raise KeyError(f"列 '{column_name}' は存在しません")
        col = collection.columns[column_name]
        values = col.values
        name = col.name
        unit = col.unit
    return values, name, unit
