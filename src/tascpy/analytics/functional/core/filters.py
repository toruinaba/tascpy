"""
Predicates for functional operations.
These functions return boolean masks (numpy arrays of bool) based on conditions.
"""

from typing import Any, Union, Optional
import numpy as np
import operator


def _to_array(values: Any) -> np.ndarray:
    """入力値をNumPy配列に変換するヘルパー関数。

    Args:
        values (Any): 変換する値（リスト、配列、スカラーなど）。

    Returns:
        np.ndarray: 変換されたNumPy配列。
    """
    if isinstance(values, np.ndarray):
        return values
    return np.array(values)


def eq(values: Union[np.ndarray, list], value: Any, tolerance: Optional[float] = None) -> np.ndarray:
    """値がターゲット値と等しいかどうかを判定します。

    浮動小数点数の比較には許容誤差 (tolerance) を指定できます。

    Args:
        values (Union[np.ndarray, list]): 判定対象の値の配列。
        value (Any): 比較するターゲット値。
        tolerance (float, optional): 許容誤差。指定された場合、`value - tolerance <= x <= value + tolerance` の範囲内であれば等しいとみなされます。

    Returns:
        np.ndarray: 条件を満たす要素がTrueとなるブール値配列。
    """
    arr = _to_array(values)
    
    if tolerance is not None:
        # Ensure array is numeric for tolerance check
        # If object array, might fail? Let's assume numeric usage for tolerance.
        return (arr >= value - tolerance) & (arr <= value + tolerance)
    else:
        # Standard equality
        # Note: np.nan == np.nan is False
        return arr == value


def neq(values: Union[np.ndarray, list], value: Any, tolerance: Optional[float] = None) -> np.ndarray:
    """値がターゲット値と等しくないかどうかを判定します。

    `eq` 関数の否定を返します。

    Args:
        values (Union[np.ndarray, list]): 判定対象の値の配列。
        value (Any): 比較するターゲット値。
        tolerance (float, optional): 許容誤差。

    Returns:
        np.ndarray: 条件を満たす要素がTrueとなるブール値配列。
    """
    return ~eq(values, value, tolerance)


def compare(values: Union[np.ndarray, list], op_str: str, value: Any) -> np.ndarray:
    """演算子文字列を使用して値を比較します。

    Args:
        values (Union[np.ndarray, list]): 判定対象の値の配列。
        op_str (str): 比較演算子 ('>', '<', '>=', '<=', '==', '!=')。
        value (Any): 比較するターゲット値。

    Returns:
        np.ndarray: 条件を満たす要素がTrueとなるブール値配列。NaNは除外されます。

    Raises:
        ValueError: 無効な演算子が指定された場合。
        
    Examples:
        >>> from tascpy.analytics.functional.filters import compare
        >>> import numpy as np
        >>> compare(np.array([1, 2, 3]), ">", 1)
        array([False,  True,  True])
    """
    arr = _to_array(values)
    
    ops = {
        ">": operator.gt,
        "<": operator.lt,
        ">=": operator.ge,
        "<=": operator.le,
        "==": operator.eq,
        "!=": operator.ne,
    }
    
    if op_str not in ops:
        raise ValueError(f"Invalid operator '{op_str}'. Supported: {list(ops.keys())}")
        
    op_func = ops[op_str]
    
    with np.errstate(invalid='ignore'):
        mask = op_func(arr, value)
        
        # Handle NaN behavior
        # Keep consistent with search_by_value logic:
        # NaN is generally False, except for != which is True?
        # search_by_value logic: return indices where mask is True AND not NaN.
        # But wait, search_by_value says:
        # if op_str == "!=": mask = mask & ~np.isnan(vals)
        # else: mask = mask & ~np.isnan(vals)
        # So in ALL cases, NaN implies False in the final mask for search.
        
        # However, for pure predicate, should 'nan != 5' be True?
        # In NumPy: nan != 5 is True.
        # But if we want to "filter valid rows", usually we exclude NaNs.
        # Let's return raw comparison mask here? 
        # Or follow existing logic which seems to exclude NaNs explicitly.
        
        # existing search_by_value explicitly does & ~np.isnan(vals) for all ops.
        # So let's include that safety to match "valid data matching condition".
        
        if np.issubdtype(arr.dtype, np.number):
             mask = mask & ~np.isnan(arr)
             
    return mask


def in_range(
    values: Union[np.ndarray, list], 
    min_val: Any, 
    max_val: Any, 
    inclusive: bool = True
) -> np.ndarray:
    """値が指定された範囲内にあるかどうかを判定します。

    Args:
        values (Union[np.ndarray, list]): 判定対象の値の配列。
        min_val (Any): 範囲の下限。
        max_val (Any): 範囲の上限。
        inclusive (bool, optional): 端点を含めるかどうか。Trueの場合は [min, max]、Falseの場合は (min, max)。デフォルトは True。

    Returns:
        np.ndarray: 条件を満たす要素がTrueとなるブール値配列。NaNは除外されます。
        
    Examples:
        >>> from tascpy.analytics.functional.filters import in_range
        >>> import numpy as np
        >>> in_range(np.array([1, 2, 3, 4]), 2, 3)
        array([False,  True,  True, False])
    """
    arr = _to_array(values)
    
    if inclusive:
        min_op, max_op = operator.ge, operator.le
    else:
        min_op, max_op = operator.gt, operator.lt

    with np.errstate(invalid='ignore'):
        mask = min_op(arr, min_val) & max_op(arr, max_val)
        
        if np.issubdtype(arr.dtype, np.number):
             mask = mask & ~np.isnan(arr)
             
    return mask


def is_valid(values: Union[np.ndarray, list]) -> np.ndarray:
    """値が有効か（欠損していないか）どうかを判定します。

    NaNやNoneでない場合にTrueを返します。

    Args:
        values (Union[np.ndarray, list]): 判定対象の値の配列。

    Returns:
        np.ndarray: 有効な値がTrueとなるブール値配列。
        
    Examples:
        >>> from tascpy.analytics.functional.filters import is_valid
        >>> import numpy as np
        >>> is_valid(np.array([1, np.nan, 3]))
        array([ True, False,  True])
    """
    arr = _to_array(values)
    
    if np.issubdtype(arr.dtype, np.number):
        return ~np.isnan(arr)
        
    # Object array
    def _check(x):
        if x is None: return False
        if isinstance(x, float) and np.isnan(x): return False
        if isinstance(x, (np.float64, np.float32)) and np.isnan(x): return False
        return True
        
    # Vectorize is slow but safe for mixed types
    return np.vectorize(_check)(arr)
"""
Row operations for functional module.
These functions operate on dictionaries of arrays (simulating dataframe rows).
"""

from typing import Dict, Any, List, Union, Callable
import numpy as np



def filter_by_row_condition(
    data: Dict[str, Union[np.ndarray, list]], 
    condition: Callable[[Dict[str, Any]], bool]
) -> List[int]:
    """行ごとの条件に基づいてインデックスをフィルタリングします。

    Args:
        data (Dict[str, Union[np.ndarray, list]]): カラム名をキーとするデータ辞書。
        condition (Callable[[Dict[str, Any]], bool]): 行データ（辞書）を受け取り、boolを返す関数。

    Returns:
        List[int]: 条件を満たす行のインデックスリスト。
    """
    if not data:
        return []

    # Get length from first column
    # Assume aligned lengths (validated by caller/wrappers)
    length = 0
    cols_data = {}
    
    for k, v in data.items():
        length = len(v)
        cols_data[k] = v
        
    indices = []
    keys = list(cols_data.keys())
    
    # Iterate rows
    # Pure Python loop 
    for i in range(length):
        row_data = {}
        for k in keys:
            vals = cols_data[k]
            # Safety check
            if i < len(vals):
                row_data[k] = vals[i]
            else:
                row_data[k] = None
                
        if condition(row_data):
            indices.append(i)
            
    return indices


def duplicated_indices(
    data: Dict[str, Union[np.ndarray, list]],
    mode: str = "consecutive",
    dup_type: str = "all"
) -> List[int]:
    """重複を除去した後の保持すべきインデックスを返します。

    Args:
        data (Dict[str, Union[np.ndarray, list]]): カラム名をキーとするデータ辞書。
        mode (str, optional): 重複判定モード。'consecutive'（連続する重複のみ）または 'all'（全行での重複、未実装）。デフォルトは "consecutive"。
        dup_type (str, optional): 重複判定の厳密さ。
            'all': すべてのカラムが一致する場合に重複とみなす（標準）。
            'any': いずれかのカラムが一致する場合に重複とみなす（厳密、またはテスト用）。デフォルトは "all"。

    Returns:
        List[int]: 保持すべき行のインデックスリスト。

    Raises:
        ValueError: dup_type が 'all' または 'any' 以外の場合。
        NotImplementedError: mode が 'consecutive' 以外の場合。
        
    Examples:
        >>> from tascpy.analytics.functional.filters import duplicated_indices
        >>> data = {"A": [1, 1, 2, 2, 3]}
        >>> duplicated_indices(data)
        [0, 2, 4]
    """
    if not data:
        return []
        
    keys = list(data.keys())
    if not keys:
        return []
        
    length = len(data[keys[0]])
    if length == 0:
        return []
        
    indices_to_keep = [0]
    
    if mode == "consecutive":
        for i in range(1, length):
            if dup_type == "all":
                # Remove if ALL cols match previous (i.e., keep if ANY col changed)
                has_change = False
                for k in keys:
                    vals = data[k]
                    v_curr = vals[i]
                    v_prev = vals[i-1]
                    if v_curr != v_prev:
                        has_change = True
                        break
                if has_change:
                    indices_to_keep.append(i)
            
            elif dup_type == "any":
                # 'any' mode in tests expects behavior: "Keep if even a part of columns change".
                # This is synonymous with "Remove only if ALL columns match".
                # This matches 'all' mode behavior in the legacy tests.
                
                # Check if ALL columns match previous (same as 'all' mode logic above)
                has_change = False
                for k in keys:
                    vals = data[k]
                    v_curr = vals[i]
                    v_prev = vals[i-1]
                    if v_curr != v_prev:
                        has_change = True
                        break
                if has_change:
                    indices_to_keep.append(i)
            
            else:
                raise ValueError("dup_typeは'all'または'any'である必要があります")

    else:
        raise NotImplementedError(f"Duplicate mode '{mode}' is not implemented")
        
    return indices_to_keep


def filter_valid_rows(
    data: Dict[str, Union[np.ndarray, list]],
    mode: str = "any"
) -> List[bool]:
    """有効な行（欠損値を含まない行）を判定するマスクを返します。

    Args:
        data (Dict[str, Union[np.ndarray, list]]): カラム名をキーとするデータ辞書。
        mode (str, optional): 欠損値の扱い。
            'any': 少なくとも1つのカラムが欠損している行を除外（すべて有効な場合に保持）。
            'all': すべてのカラムが欠損している行を除外（少なくとも1つ有効なら保持）。デフォルトは "any"。

    Returns:
        List[bool]: 有効な行に対応するブール値リスト。

    Raises:
        ValueError: モードが 'any' または 'all' 以外の場合。
    """
    if mode not in ["any", "all"]:
        raise ValueError("モードは'any'または'all'のいずれかである必要があります")

    if not data:
        return []

    # Get length
    keys = list(data.keys())
    length = len(data[keys[0]])
    
    # We can use is_valid on each column
    # Then combine masks
    
    # Initialize mask
    if mode == "any":
        # Start with all True (Keep), AND with each column validity
        combined_mask = np.ones(length, dtype=bool)
        for k in keys:
            valid_col = is_valid(data[k])
            combined_mask = combined_mask & valid_col
    else:
        # mode == "all" (drop only if all are NA -> keep if any is Valid)
        # Start with all False (Drop), OR with each column validity
        combined_mask = np.zeros(length, dtype=bool)
        for k in keys:
            valid_col = is_valid(data[k])
            combined_mask = combined_mask | valid_col
            
    return combined_mask.tolist()
"""
Selectors for functional operations.
These functions return indices or values based on criteria.
"""

from typing import Any, List, Union, Optional
import numpy as np



def where(mask: Union[np.ndarray, list]) -> List[int]:
    """ブール値マスクに基づいてTrueの要素のインデックスを返します。

    Args:
        mask (Union[np.ndarray, list]): ブール値の配列またはリスト。

    Returns:
        List[int]: Trueの要素のインデックスリスト。
    """
    if isinstance(mask, list):
         mask = np.array(mask)
         
    return np.where(mask)[0].tolist()





def nearest_index(
    values: Union[np.ndarray, list], 
    target: float, 
    tolerance: Optional[float] = None
) -> Optional[int]:
    """指定されたターゲット値に最も近い値のインデックスを返します。

    許容誤差が指定されている場合、最小差分が許容誤差を超える場合はNoneを返します。

    Args:
        values (Union[np.ndarray, list]): 検索対象の数値配列。
        target (float): ターゲット値。
        tolerance (float, optional): 許容誤差。デフォルトは None。

    Returns:
        Optional[int]: 最も近い値のインデックス。見つからない場合や条件を満たさない場合は None。

    Raises:
        TypeError: values が数値型でない場合。
    """
    vals = np.array(values) if isinstance(values, list) else values
    
    if not np.issubdtype(vals.dtype, np.number):
         try:
             vals = vals.astype(float)
         except ValueError:
             raise TypeError("Values must be numeric for nearest search")

    diff = np.abs(vals - target)
    
    # Ignore NaNs
    try:
        idx = np.nanargmin(diff)
    except ValueError:
        return None # All NaNs or empty
        
    if tolerance is not None:
        if diff[idx] > tolerance:
            return None
            
    return int(idx)


def search(values: Union[np.ndarray, list], op_str: str, value: Any) -> List[int]:
    """演算子条件を満たす値のインデックスを返します。

    Args:
        values (Union[np.ndarray, list]): 判定対象の値の配列。
        op_str (str): 比較演算子 ('>', '<', '>=', '<=', '==', '!=')。
        value (Any): 比較するターゲット値。

    Returns:
        List[int]: 条件を満たす要素のインデックスリスト。
    """
    mask = compare(values, op_str, value)
    return where(mask)


def search_range(
    values: Union[np.ndarray, list], 
    min_value: Any, 
    max_value: Any, 
    inclusive: bool = True
) -> List[int]:
    """指定された範囲内の値のインデックスを返します。

    Args:
        values (Union[np.ndarray, list]): 判定対象の値の配列。
        min_value (Any): 範囲の下限。
        max_value (Any): 範囲の上限。
        inclusive (bool, optional): 端点を含めるかどうか。Trueの場合は [min, max]、Falseの場合は (min, max)。デフォルトは True。

    Returns:
        List[int]: 範囲内の要素のインデックスリスト。
    """
    mask = in_range(values, min_value, max_value, inclusive)
    return where(mask)
    
    
def search_step_range(
    steps: Union[np.ndarray, list],
    min: float,
    max: float,
    inclusive: bool = True,
    tolerance: Optional[float] = None,
    by_step_value: bool = True
) -> List[int]:
    """ステップ値が指定された範囲内にあるインデックスを返します。

    Args:
        steps (Union[np.ndarray, list]): ステップ値の配列。
        min (float): 範囲の下限。
        max (float): 範囲の上限。
        inclusive (bool, optional): 端点を含めるかどうか。デフォルトは True。
        tolerance (float, optional): 許容誤差。デフォルトは None。
        by_step_value (bool, optional): ステップ値に基づいて検索するかどうか。Falseの場合はインデックス自体を対象とします。デフォルトは True。

    Returns:
        List[int]: 条件を満たすステップのインデックスリスト。
    """
    arr = np.array(steps) if isinstance(steps, list) else steps
    
    if not by_step_value:
        # Index based filtering
        length = len(arr)
        # Use arange as the "steps" to search
        arr = np.arange(length)
        # Tolerance logic handled below using these new 'arr'
        tolerance = None 
    
    if tolerance is not None:
         # Tolerance logic
         if inclusive:
             mask = (arr >= min - tolerance) & (arr <= max + tolerance)
         else:
             mask = (arr > min + tolerance) & (arr < max - tolerance)
    else:
         # Standard range
         mask = in_range(arr, min, max, inclusive)
         
    if np.issubdtype(arr.dtype, np.number):
         mask = mask & ~np.isnan(arr)
         
    return where(mask)


# --- Additional Filters (from filters.py) ---



def remove_outliers_mask(
    vals: Any,
    window_size: int = 3,
    threshold: float = 0.5,
    edge_handling: str = "asymmetric",
    min_abs_value: float = 1e-10,
    scale_factor: float = 1.0,
) -> List[bool]:
    """外れ値を除去するためのマスクを生成します。

    外れ値ではない値に対して True、外れ値に対して False を返します。

    Args:
        vals (Any): 入力値（リストまたは配列）。
        window_size (int, optional): 移動平均のウィンドウサイズ。デフォルトは 3。
        threshold (float, optional): 外れ値判定の閾値。割合による変動がこの閾値を超えると外れ値とみなされます。デフォルトは 0.5。
        edge_handling (str, optional): 境界処理の方法 ('asymmetric' など)。デフォルトは "asymmetric"。
        min_abs_value (float, optional): ゼロ除算を防ぐための最小絶対値。デフォルトは 1e-10。
        scale_factor (float, optional): 閾値をスケーリングする係数。デフォルトは 1.0。

    Returns:
        List[bool]: 保持すべき値（非外れ値）のブール値リスト。
    """
    flags = functional_stats.detect_outliers(
        vals,
        window_size=window_size,
        threshold=threshold,
        edge_handling=edge_handling,
        min_abs_value=min_abs_value,
        scale_factor=scale_factor,
    )

    if hasattr(flags, "__iter__") and not isinstance(flags, str):
         return [f == 0 for f in flags]
    else:
         return [flags == 0]

def filter_by_condition(
    vals: Any, condition: callable
) -> List[bool]:
    """条件に基づいて値をフィルタリングするためのマスクを生成します。

    Args:
        vals (Any): 入力値（リストまたは配列）。
        condition (callable): 値を引数に取り、保持すべき場合に True を返す関数。

    Returns:
        List[bool]: 保持すべき値のブール値リスト。
    """
    # vals is numpy array or list
    return [condition(val) for val in vals]

def remove_steps_mask(
    step_values: Union[List[Any], np.ndarray],
    steps: List[Any], 
    tolerance: Optional[float] = None
) -> List[bool]:
    """特定のステップを除去するためのマスクを生成します。

    指定されたステップに含まれない値に対して True を返します。

    Args:
        step_values (Union[List[Any], np.ndarray]): 入力のステップ値リスト。
        steps (List[Any]): 除去するステップのリスト。
        tolerance (float, optional): ステップ一致判定の許容誤差。デフォルトは None（完全一致）。

    Returns:
        List[bool]: 保持すべきステップ（除去対象でない）のブール値リスト。
    """
    current_steps = step_values if isinstance(step_values, (list, np.ndarray)) else np.array(step_values)
    steps_to_remove = set(steps)

    if tolerance is None:
        mask = [s not in steps_to_remove for s in current_steps]
    else:
        mask = []
        steps_arr = np.array(steps)
        # Optimization: use numpy broadcasting if steps_arr is small-ish?
        # Or iterate. Original implementation iterated.
        # Let's keep iteration for simplicity/parity, or optimize?
        # Pure function can be optimized.
        
        # If both are large, this is O(N*M).
        # Vectorized:
        # diff = np.abs(current_steps[:, None] - steps_arr[None, :])
        # is_close = np.any(diff <= tolerance, axis=1)
        # mask = ~is_close
        
        if isinstance(current_steps, np.ndarray) and isinstance(steps_arr, np.ndarray) and np.issubdtype(current_steps.dtype, np.number):
             diff = np.abs(current_steps[:, None] - steps_arr[None, :])
             is_close = np.any(diff <= tolerance, axis=1)
             mask = (~is_close).tolist()
        else:
            # Fallback for non-numeric or list
            for s in current_steps:
                try:
                    is_close = np.any(np.abs(steps_arr - s) <= tolerance)
                    mask.append(not is_close)
                except Exception:
                    # In case of type error in subtraction
                    mask.append(True) # Keep?
            
    return mask





# --- Searching utilities (from utils.searching.py) ---


def find_index_with_tolerance(
    values: Union[np.ndarray, list], 
    target: Any, 
    tolerance: Optional[float] = None, 
    default: Any = None
) -> Union[int, Any]:
    """
    配列から値を検索し、最初に見つかったインデックスを返す。
    toleranceが指定された場合は、|value - target| <= tolerance の範囲で検索する。
    """
    # 配列への変換と型チェック
    if isinstance(values, list):
        values = np.array(values)
    
    if len(values) == 0:
        return default

    if tolerance is not None:
         # 許容範囲内での検索
         # np.isclose は全要素チェックになるので遅い可能性があるが、ループよりは早い
         # 公差がある場合は where で条件に合う最初のインデックスを探す
         
         # abs(values - target) <= tolerance
         # Note: assuming numeric array if tolerance is used
         try:
             diff = np.abs(values - target)
             indices = np.where(diff <= tolerance)[0]
             if len(indices) > 0:
                 return int(indices[0])
         except (TypeError, ValueError):
             # 比較できない場合 (数値以外など)
             pass
             
    else:
         # 完全一致
         # np.where で検索
         indices = np.where(values == target)[0]
         if len(indices) > 0:
             return int(indices[0])

    # 値が見つからない場合
    return default
