"""荷重-変位ドメイン専用の抽象化機能"""

import functools

def resolve_ld_columns(func):
    """
    荷重-変位コレクションから自動的に列名を取得し、
    位置引数の先頭に設定するデコレータ（inject_columnsが処理するため）。
    """
    @functools.wraps(func)
    def wrapper(collection, *args, **kwargs):
        new_args = list(args)
        if len(new_args) < 1:
            disp_col = collection.displacement_column
            load_col = collection.load_column
            # inject_columnsはシグネチャの順序(disp, load)を期待している
            new_args = [disp_col, load_col] + new_args
        elif len(new_args) < 2:
            load_col = collection.load_column
            new_args = [new_args[0], load_col] + new_args[1:]
        
        return func(collection, *new_args, **kwargs)
    return wrapper

def resolve_load_column(func):
    """
    荷重-変位コレクションから自動的に荷重列名を取得し、
    位置引数の先頭に設定するデコレータ（inject_columnsが処理するため）。
    """
    @functools.wraps(func)
    def wrapper(collection, *args, **kwargs):
        new_args = list(args)
        if len(new_args) < 1:
            load_col = collection.load_column
            new_args = [load_col] + new_args
        
        return func(collection, *new_args, **kwargs)
    return wrapper

def resolve_ld_and_cycle_columns(func):
    """
    荷重-変位コレクションから荷重、変位、およびサイクル列データを取得し、
    関数に (loads, disps, markers, *args, **kwargs) として渡すデコレータ。
    """
    @functools.wraps(func)
    def wrapper(
        collection,
        cycle_marker_column=None,
        *args,
        **kwargs
    ):
        import numpy as np
        from tascpy.plugins.load_displacement import cycle_count
        
        ld_info = collection.metadata.get("load_displacement_domain", {})
        marker_col = cycle_marker_column or ld_info.get("cycle_marker_column", "cycle_marker")
        
        loads = collection.load_data
        disps = collection.displacement_data
        
        try:
            if marker_col in collection.columns:
                markers = np.array(collection[marker_col].values)
            else:
                 # fallback to searching
                 found_marker = next((c for c in collection.columns if "cycle" in c.lower()), None)
                 if found_marker:
                     markers = np.array(collection[found_marker].values)
                 else:
                     raise KeyError
        except KeyError:
            markers = np.array(cycle_count(loads.tolist()))
            
        # register_functional wrappers expect data directly if num_inputs isn't used
        # However, extra_decorators apply INSIDE transform_column but OUTSIDE the pure function?
        # Actually, in register_functional, extra_decorators are applied directly to the pure function (inner-most).
        # So the wrapper here receives exactly what the pure function expects + collection if it was an outer operation.
        # But wait - if this is an extra_decorator, it receives (loads, disps, markers, ...). 
        # But register_functional passes arguments down. 
        # Let's check how extra_decorators are applied:
        # wrapped_func = func  -> extra = extra(wrapped_func)
        # So this wrapper becomes the innermost function.
        # It gets called by the abstraction layer. 
        # If it's used as an `extra_decorator` for a functional op, the abstraction layer (store_result etc)
        # STILL passes `collection` as the first argument!
        # Because we didn't use `inject_columns` to strip it out!
        # YES. So we MUST strip `collection` here before passing to the pure func.
        return func(loads, disps, markers, *args, **kwargs)
    return wrapper
