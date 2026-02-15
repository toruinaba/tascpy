from typing import Any, List, Dict, Optional, Union, Callable
import operator
import numpy as np
from ...core.collection import ColumnCollection
from ..registry import operation
from ..abstraction import filter_rows, inject_columns, inject_step_values


@operation(domain="core")
@inject_columns(num_inputs=1, cast_to_numpy=True)
def search_by_value(
    vals: Any, op_str: str, value: Any
) -> List[int]:
    """値による検索を行います
    
    指定された列の値に対して比較演算子を適用し、条件に一致する行のインデックスを返します。

    Args:
        vals: 列の値 (inject_columnsにより注入)
        op_str: 演算子文字列 (">", "<", ">=", "<=", "==", "!=")
        value: 比較する値

    Returns:
        List[int]: 条件に一致するインデックスのリスト
    """
    # 演算子マッピング
    ops = {
        ">": operator.gt,
        "<": operator.lt,
        ">=": operator.ge,
        "<=": operator.le,
        "==": operator.eq,
        "!=": operator.ne,
    }

    # 演算子の検証
    if op_str not in ops:
        raise ValueError(
            f"演算子 '{op_str}' は無効です。有効な演算子: {list(ops.keys())}"
        )

    op_func = ops[op_str]
    
    # vals は @inject_columns(cast_to_numpy=True) により NumPy 配列であることが保証される
    # None は NaN に変換されているはずだが、念のため errstate を使用
    
    with np.errstate(invalid='ignore'):
        # 比較実行
        mask = op_func(vals, value)
        
        # NaNを除外 (演算子に関わらず、NaNはFalseあるいは不定とする)
        # NaNは比較において常にFalseになるのがNumPyの仕様だが、!= の場合は True になる
        if op_str == "!=":
             mask = mask & ~np.isnan(vals)
        else:
             mask = mask & ~np.isnan(vals)
             
    return np.where(mask)[0].tolist()


@operation(domain="core")
@inject_columns(num_inputs=1, cast_to_numpy=True)
def search_by_range(
    vals: Any,
    min_value: Any,
    max_value: Any,
    inclusive: bool = True,
) -> List[int]:
    """範囲による検索を行います

    指定された列の値が特定の範囲内にある行のインデックスを返します。

    Args:
        vals: 列の値
        min_value: 最小値
        max_value: 最大値
        inclusive: 境界値を含めるかどうか

    Returns:
        List[int]: 条件に一致するインデックスのリスト
    """
    # 演算子の選択
    if inclusive:
        min_op, max_op = operator.ge, operator.le
    else:
        min_op, max_op = operator.gt, operator.lt

    with np.errstate(invalid='ignore'):
         mask = min_op(vals, min_value) & max_op(vals, max_value) & ~np.isnan(vals)
         
    return np.where(mask)[0].tolist()


@operation(domain="core")
@operation(domain="core")
@inject_step_values(cast_to_numpy=True)
def search_by_step_range(
    step_values: Union[List[Union[int, float]], np.ndarray],
    min: Union[int, float],
    max: Union[int, float],
    inclusive: bool = True,
    by_step_value: bool = True,
    tolerance: Optional[float] = None,
) -> Union[List[int], tuple]:
    """ステップ範囲による検索を行います"""
    # 演算子の選択
    if inclusive:
        min_op, max_op = operator.ge, operator.le
    else:
        min_op, max_op = operator.gt, operator.lt

    steps = step_values # cast_to_numpy guarantees array if possible

    if by_step_value:
        # ステップ値に基づくフィルタリング
         if tolerance is not None:
             if inclusive:
                 mask = (steps >= min - tolerance) & (steps <= max + tolerance)
             else:
                 mask = (steps > min + tolerance) & (steps < max - tolerance)
         else:
             mask = min_op(steps, min) & max_op(steps, max)
         
         mask = mask & ~np.isnan(steps)
         indices = np.where(mask)[0].tolist()
    else:
        # インデックスに基づくフィルタリング
        # Use length of steps
        length = len(steps)
        # Vectorized range check
        idx_arr = np.arange(length)
        mask = min_op(idx_arr, min) & max_op(idx_arr, max)
        indices = np.where(mask)[0].tolist()

    # メタデータを更新するためにタプルを返す
    metadata_update = {
        "operation": "search_by_step_range",
        "by_step_value": by_step_value,
        "min": min,
        "max": max,
        "inclusive": inclusive,
    }
    return indices, metadata_update


@operation(domain="core")
@inject_columns(columns_arg="columns", cast_to_numpy=True)
def search_by_condition(
    data: Dict[str, Any], 
    condition_func: Callable[[Dict[str, Any]], bool],
    columns: Optional[List[str]] = None
) -> List[int]:
    """条件関数による検索を行います
    
    行ごとのデータを辞書として受け取り、条件関数が True を返す行のインデックスを返します。
    columns引数を指定すると、その列のみがデータ辞書に含まれます（パフォーマンス最適化）。

    Args:
        data: 列データの辞書 (inject_columnsにより注入)
        condition_func: 行データ辞書を受け取り、boolを返す関数
        columns: 使用する列名のリスト (Noneの場合は全列)
    """
    if not data:
        return []

    indices = []
    
    # Check length from first column
    length = 0
    for arr in data.values():
        length = len(arr)
        break
    
    # 事前に data は Dict[name, array] になっている
    # 行ごとのループ
    # Note: data access data[name][i] might be slow in pure python loop. 
    # But it's generic constraint.
    
    # Optimization: Extract arrays to local var
    cols_data = data
    col_names = list(data.keys())
    
    # Iterate
    for i in range(length):
        row_data = {}
        for name in col_names:
            vals = cols_data[name]
            # Boundary check logic was: val = vals[i] if i < len(vals) else None
            # With inject_columns/ColumnCollection, lengths should be aligned mostly, 
            # but let's keep safety if arrays differ (though rare in validated collection)
            if i < len(vals):
                 val = vals[i]
            else:
                 val = None
            row_data[name] = val

        # 条件関数を適用
        if condition_func(row_data):
            indices.append(i)

    return indices


@operation(domain="core")
@inject_columns(columns_arg="columns", cast_to_numpy=True)
def search_missing_values(
    data: Dict[str, Any], columns: Optional[List[str]] = None
) -> List[int]:
    """欠損値がある行を検索します

    指定された列に欠損値（None または NaN）を含む行のインデックスを返します。
    """
    if not data:
        # No columns to check?
        return []
    
    # data is Dict[col_name, numpy_array]
    # We need to check length. Assume all same length?
    length = 0
    for arr in data.values():
        length = len(arr)
        break
        
    missing_mask = np.zeros(length, dtype=bool)
    
    for col_name, arr in data.items():
        if isinstance(arr, np.ndarray) and np.issubdtype(arr.dtype, np.number):
             is_missing = np.isnan(arr)
        else:
             # Object array or list (if not cast properly, but cast_to_numpy=True implies array)
             # If object array with None
             # But cast_to_numpy with mix types creates object array
             # Let's handle generic
             if isinstance(arr, np.ndarray):
                 if arr.dtype == object:
                     # Check None or NaN
                     is_missing = np.array([x is None or (isinstance(x, float) and np.isnan(x)) for x in arr])
                 else:
                     is_missing = np.zeros(len(arr), dtype=bool) # Int array etc
             else:
                 is_missing = np.array([x is None or (isinstance(x, float) and np.isnan(x)) for x in arr])
        
        # Broadcasting check
        if len(is_missing) < length:
             pady = np.zeros(length, dtype=bool)
             pady[:len(is_missing)] = is_missing
             is_missing = pady
             
        missing_mask |= is_missing[:length]

    return np.where(missing_mask)[0].tolist()


@operation(domain="core")
@inject_columns(num_inputs=1, cast_to_numpy=True)
def search_top_n(
    vals: Any, n: int, descending: bool = True
) -> List[int]:
    """指定した列の上位 N 件を検索します"""
    
    # NumPy最適化
    # vals guaranteed to be array (cast_to_numpy=True)
    
    valid_mask = ~np.isnan(vals)
    valid_indices = np.where(valid_mask)[0]
    valid_vals = vals[valid_mask]
    
    if len(valid_vals) == 0:
        return []
        
    sorted_valid_indices_local = np.argsort(valid_vals)
    
    if descending:
        # Largest first -> reverse
        sorted_valid_indices_local = sorted_valid_indices_local[::-1]
        
    # Map back to original indices
    sorted_original_indices = valid_indices[sorted_valid_indices_local]
    
    # Take top n
    top_n_indices = sorted_original_indices[:n]
    
    # 元の順序でソートして返す (仕様維持)
    top_n_indices.sort()
    return top_n_indices.tolist()
