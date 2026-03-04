from typing import Callable, Optional, Union, List, Any, Dict
import functools
import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import detect_column_type, NumberColumn
from tascpy.core.step import Step
from tascpy.core.result import XYSeriesResult, PointResult, ScalarResult


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
                    If set to -1, it treats all remaining positional arguments as columns.
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

            # Determine actual number of inputs to process
            actual_num_inputs = len(args_list) if num_inputs == -1 else num_inputs

            for i in range(actual_num_inputs):
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


def store_xy_result(
    func: Optional[Callable] = None,
    *,
    name: str = "curve",
    x_suffix: str = "_x",
    y_suffix: str = "_y",
    inject_metadata: Optional[Callable[[tuple, dict, Any], Dict[str, Any]]] = None,
):
    """
    Decorator to store a generic 2D series result.
    The wrapped function is expected to return (x_values, y_values) or a tuple containing them.
    """
    def decorator(target_func):
        @functools.wraps(target_func)
        def wrapper(collection: Union[ColumnCollection, Any], *args, **kwargs):
            if not isinstance(collection, ColumnCollection):
                return target_func(collection, *args, **kwargs)

            func_kwargs = kwargs.copy()
            res_data = target_func(collection, *args, **func_kwargs)
            
            # Unpack results: func might return (x, y) or (x, y, meta) etc.
            x_vals, y_vals = res_data[0], res_data[1]
            extra_meta = res_data[2] if len(res_data) > 2 else {}

            result_collection = collection.clone()
            
            x_col = NumberColumn(ch=None, name=f"{name}{x_suffix}", unit="", values=x_vals)
            y_col = NumberColumn(ch=None, name=f"{name}{y_suffix}", unit="", values=y_vals)

            curve = XYSeriesResult(
                name=name,
                x=x_col,
                y=y_col,
                metadata=extra_meta
            )
            
            result_collection.add_result(curve)

            if inject_metadata:
                try:
                    meta = inject_metadata(args, kwargs, res_data)
                    if meta:
                        result_collection.metadata.update(meta)
                except Exception as e:
                    raise e
                    
            return result_collection
        return wrapper

    if func is not None:
        return decorator(func)
    return decorator


def store_point_result(
    func: Optional[Callable] = None,
    *,
    name: str = "point",
    inject_metadata: Optional[Callable[[tuple, dict, Any], Dict[str, Any]]] = None,
):
    """
    Decorator to store a PointResult.
    The wrapped function is expected to return (is_valid, x_value, y_value, metadata) or similar.
    We just need x and y.
    """
    def decorator(target_func):
        @functools.wraps(target_func)
        def wrapper(collection: Union[ColumnCollection, Any], *args, **kwargs):
            if not isinstance(collection, ColumnCollection):
                return target_func(collection, *args, **kwargs)

            func_kwargs = kwargs.copy()
            res_data = target_func(collection, *args, **func_kwargs)
            
            # Assuming returns are (bool, x, y, meta) like yield point, or just (x, y)
            if isinstance(res_data, tuple) and len(res_data) >= 3 and isinstance(res_data[0], bool):
                # (is_valid, x, y, meta)
                is_valid = res_data[0]
                x_val = res_data[1]
                y_val = res_data[2]
                extra_meta = res_data[3] if len(res_data) > 3 else {}
                extra_meta["is_valid"] = is_valid
            else:
                x_val, y_val = res_data[0], res_data[1]
                extra_meta = res_data[2] if len(res_data) > 2 else {}

            result_collection = collection.clone()

            point = PointResult(
                name=name,
                x=x_val,
                y=y_val,
                metadata=extra_meta
            )
            
            result_collection.add_result(point)

            if inject_metadata:
                try:
                    meta = inject_metadata(args, kwargs, res_data)
                    if meta:
                        result_collection.metadata.update(meta)
                except Exception as e:
                    raise e
                    
            return result_collection
        return wrapper

    if func is not None:
        return decorator(func)
    return decorator


def store_multiple_results(
    func: Optional[Callable] = None,
    *,
    results: List[Dict[str, Any]],
    inject_metadata: Optional[Callable[[tuple, dict, Any], Dict[str, Any]]] = None,
):
    """
    単一の実行結果（タプル等）から複数の結果（ScalarResultやPointResultなど）を
    抽出してコレクションに追加するデコレータ。

    Args:
        results: 各結果の抽出・作成設定のリスト
            例:
            [
                {"type": "scalar", "name": "{result_prefix}_E", "index": 0, "unit_arg": "unit"},
                {"type": "point", "name": "{result_prefix}_yield", "x_index": 1, "y_index": 2}
            ]
    """
    def decorator(target_func):
        @functools.wraps(target_func)
        def wrapper(collection: Union[ColumnCollection, Any], *args, **kwargs):
            if not isinstance(collection, ColumnCollection):
                return target_func(collection, *args, **kwargs)

            func_kwargs = kwargs.copy()
            # プレフィックス等の共通フォーマット引数を取得
            result_prefix = func_kwargs.pop("result_prefix", "result")
            
            res_data = target_func(collection, *args, **func_kwargs)
            
            # 関数の戻り値がタプルでない場合はタプル化
            if not isinstance(res_data, tuple):
                res_data = (res_data,)
                
            result_collection = collection.clone()
            
            # メタデータの動的生成
            extra_meta = {}
            if inject_metadata:
                try:
                    extra_meta = inject_metadata(args, kwargs, res_data) or {}
                except Exception as e:
                    raise e
            
            for config in results:
                res_type = config.get("type", "scalar")
                
                # 名前をフォーマット (引数の値を埋め込めるようにする)
                raw_name = config.get("name", "result")
                try:
                    format_args = {"result_prefix": result_prefix}
                    format_args.update(kwargs)
                    name = raw_name.format(**format_args)
                except KeyError:
                    name = raw_name
                
                meta = config.get("metadata", {}).copy()
                meta.update(extra_meta)
                
                # NaN チェック用のヘルパー
                def is_valid_val(v):
                    if isinstance(v, (int, float, np.number)):
                        return not np.isnan(v)
                    return v is not None

                if res_type == "scalar":
                    idx = config.get("index", 0)
                    if idx < len(res_data):
                        val = res_data[idx]
                        if is_valid_val(val):
                            s_res = ScalarResult(
                                name=name,
                                value=val,
                                unit=config.get("unit"),
                                metadata=meta
                            )
                            result_collection.add_result(s_res)
                            
                elif res_type == "point":
                    x_idx = config.get("x_index", 0)
                    y_idx = config.get("y_index", 1)
                    if x_idx < len(res_data) and y_idx < len(res_data):
                        x_val = res_data[x_idx]
                        y_val = res_data[y_idx]
                        if is_valid_val(x_val) and is_valid_val(y_val):
                            p_res = PointResult(
                                name=name,
                                x=x_val,
                                y=y_val,
                                x_unit=config.get("x_unit") or config.get("unit"),
                                y_unit=config.get("y_unit") or config.get("unit"),
                                metadata=meta
                            )
                            result_collection.add_result(p_res)

            return result_collection
        return wrapper

    if func is not None:
        return decorator(func)
    return decorator


def process_by_group(
    func: Optional[Callable] = None,
    *,
    group_column_arg: str = "group_column",
    default_group_column: Optional[str] = None,
    output_columns: List[Dict[str, Any]],
    collection_cls: Optional[type] = None
):
    """
    コレクションを指定カラムでグループ化し、各グループサブコレクションに対して
    純粋関数を実行し、その結果（スカラー群）を新しいコレクションとして結合するデコレータ。
    
    Args:
        group_column_arg: グループ化に使うカラム名を受け取るkwargsのキー名
        default_group_column: defaultのグループカラム名
        output_columns: 出力するカラムの定義リスト
            例:
            [
                {"name": "cycle", "index": 0},
                {"name": "energy", "index": 1, "unit": "J"}
            ]
        collection_cls: 返り値のコレクションクラス (None なら入力と同じ)
    """
    def decorator(target_func):
        @functools.wraps(target_func)
        def wrapper(collection: Union[ColumnCollection, Any], *args, **kwargs):
            if not isinstance(collection, ColumnCollection):
                return target_func(collection, *args, **kwargs)
                
            group_col_name = kwargs.pop(group_column_arg, default_group_column)
            
            if group_col_name is None:
                # サイクル列名の自動検出のフォールバック
                for col_name in collection.columns:
                    if "cycle" in col_name.lower():
                        group_col_name = col_name
                        break
            
            groups = []
            if group_col_name and group_col_name in collection.columns:
                group_vals = collection[group_col_name].values
                # 順序を保ったUnique抽出
                unique_keys = []
                for v in group_vals:
                    # np.nanではない、ハッシュ可能であることなどを確認
                    try:
                        if v not in unique_keys and not (isinstance(v, float) and np.isnan(v)):
                            unique_keys.append(v)
                    except:
                        pass
                
                indices_dict = {k: [] for k in unique_keys}
                for i, v in enumerate(group_vals):
                    try:
                        if v in indices_dict:
                            indices_dict[v].append(i)
                    except:
                        pass
                        
                for k in unique_keys:
                    idxs = indices_dict[k]
                    sub_col = collection.clone()
                    sub_col.step.values = [collection.step.values[i] for i in idxs]
                    for name, col in collection.columns.items():
                        new_col = col.__class__(col.ch, col.name, col.unit, [col.values[i] for i in idxs], dict(col.metadata))
                        sub_col.columns[name] = new_col
                    groups.append((k, sub_col))
            else:
                groups = [(1, collection)]
            
            # 各グループに対して処理
            results_accum = [[] for _ in range(len(output_columns))]
            step_accum = []
            
            for i, (group_key, sub_col) in enumerate(groups):
                # 関数実行
                res = target_func(sub_col, *args, **kwargs)
                if not isinstance(res, tuple):
                    res = (res,)
                
                step_accum.append(group_key)
                
                # 結果のアサイン
                for j, out_config in enumerate(output_columns):
                    idx = out_config.get("index", j)
                    source_val = res[idx] if idx < len(res) else None
                    results_accum[j].append(source_val)
            
            # 結果コレクションの生成
            cls_to_use = collection_cls if collection_cls else collection.__class__
            meta = collection.metadata.copy()
            meta["grouped_by"] = group_col_name
            
            new_coll = cls_to_use(
                step=step_accum,
                columns={},
                metadata=meta
            )
            
            for j, out_config in enumerate(output_columns):
                name = out_config.get("name", f"result_{j}")
                unit = out_config.get("unit")
                
                if unit is None and "inherit_unit_from" in out_config:
                    src_col = out_config["inherit_unit_from"]
                    actual_src_col = src_col
                    if src_col == "__load__":
                         try:
                             actual_src_col = collection.load_column
                         except: pass
                    elif src_col == "__disp__":
                         try:
                             actual_src_col = collection.displacement_column
                         except: pass
                         
                    if actual_src_col and actual_src_col in collection.columns:
                        unit = collection[actual_src_col].unit
                
                col_meta = out_config.get("metadata", {}).copy()
                
                # Columnの生成と追加
                from tascpy.core.column import detect_column_type
                new_col = detect_column_type(None, name, unit, results_accum[j])
                new_col.metadata.update(col_meta)
                new_coll.add_column(name, new_col)
                
            # Add dynamic kwargs if LoadDisplacementCollection
            if cls_to_use.__name__ == "LoadDisplacementCollection":
                # Find best candidates for load/displacement columns
                load_c = next((c.get("name") for c in output_columns if "load" in c.get("name", "").lower()), None)
                disp_c = next((c.get("name") for c in output_columns if "disp" in c.get("name", "").lower()), None)
                if load_c:
                     new_coll.load_column = load_c
                if disp_c:
                     new_coll.displacement_column = disp_c
                
            return new_coll
            
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
