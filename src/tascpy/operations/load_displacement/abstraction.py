"""荷重-変位ドメイン専用の抽象化機能"""

import functools
from .utils import get_displacement_column, get_load_column

def resolve_ld_columns(func):
    """
    荷重-変位コレクションから自動的に列名を取得し、
    位置引数の先頭に設定するデコレータ（inject_columnsが処理するため）。
    """
    @functools.wraps(func)
    def wrapper(collection, *args, **kwargs):
        new_args = list(args)
        if len(new_args) < 1:
            disp_col = get_displacement_column(collection)
            load_col = get_load_column(collection)
            # inject_columnsはシグネチャの順序(disp, load)を期待している
            new_args = [disp_col, load_col] + new_args
        elif len(new_args) < 2:
            load_col = get_load_column(collection)
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
            load_col = get_load_column(collection)
            new_args = [load_col] + new_args
        
        return func(collection, *new_args, **kwargs)
    return wrapper
