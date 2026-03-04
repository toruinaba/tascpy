
from typing import Union, Optional, List, Dict, Any, Set
import numpy as np
import ast
import math

def evaluate_expression(
    data: Dict[str, Union[np.ndarray, List[Any]]],
    expression: str,
) -> List[Optional[float]]:
    """データ列を使用して数式を評価します。

    NumPyによるベクトル化評価を試み、失敗した場合はPythonのeval関数による行ごとの評価にフォールバックします。
    安全のため、使用できる関数や操作は制限されています。

    Args:
        data (Dict[str, Union[np.ndarray, List[Any]]]): 評価に使用するデータの辞書（キー: カラム名, 値: データ列）。
        expression (str): 評価する数式文字列（例: "col1 + col2 * 2"）。

    Returns:
        List[Optional[float]]: 計算結果のリスト（無効値やエラーはNone）。

    Raises:
        ValueError: 式の構文エラー、安全でない操作、未定義の関数使用、または評価中のエラーが発生した場合。
        KeyError: 式に含まれるカラム名がデータに存在しない場合。
        
    Examples:
        >>> from tascpy.analytics.functional.math import evaluate_expression
        >>> import numpy as np
        >>> data = {"A": np.array([1, 2]), "B": np.array([3, 4])}
        >>> evaluate_expression(data, "A + B * 2")
        [7.0, 10.0]
    """
    # ASTを使用して式の構文検証
    try:
        parsed_ast = ast.parse(expression, mode="eval")

        # 安全でない操作や関数呼び出しをチェック
        for node in ast.walk(parsed_ast):
            # 属性アクセス（例：os.system）をブロック
            if isinstance(node, ast.Attribute):
                raise ValueError(
                    f"式に安全でない属性アクセスが含まれています: {expression}"
                )

            # 関数呼び出しが安全かチェック（数学関数以外をブロック）
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                func_name = node.func.id
                safe_funcs = {
                    "sin",
                    "cos",
                    "tan",
                    "exp",
                    "log",
                    "sqrt",
                    "abs",
                    "max",
                    "min",
                    "pow",
                    "round",
                    
                }
                if func_name not in safe_funcs:
                    raise ValueError(
                        f"許可されていない関数が使用されています: {func_name}"
                    )

    except SyntaxError as e:
        line_no = getattr(e, "lineno", "不明")
        col_offset = getattr(e, "offset", "不明")
        raise ValueError(f"式の構文エラー (行:{line_no}, 列:{col_offset}): {str(e)}")

    # 式からカラム名を抽出
    column_names = []
    # Note: pi and e are constants, not columns.
    constants = {"pi", "e"}
    
    for node in ast.walk(parsed_ast):
        if isinstance(node, ast.Name) and node.id not in {
            "sin", "cos", "tan", "exp", "log", "sqrt", "abs",
            "max", "min", "pow", "round"
        } and node.id not in constants:
            column_names.append(node.id)

    # 重複を削除し、データに存在するカラム名のみをフィルタリング
    # Verify all referenced columns exist (except safe functions and constants)
    column_names = list(set(column_names))
    
    # Check for missing columns
    available_columns = set(data.keys())
    missing_columns = set(column_names) - available_columns
    
    if missing_columns:
        # 類似したカラム名の提案 logic omitted for pure function simplicity? 
        # Or keep it? Let's keep a simple error message.
        # The operation wrapper can do suggestion logic if it inspects the expression BEFORE calling this?
        # No, duplicate logic is bad. 
        # Let's keep simple error here.
        raise KeyError(f"式に存在しないカラム名が含まれています: {', '.join(missing_columns)}")

    # 評価に使用する変数名のみを抽出
    used_cols = column_names

    # NumPyによるベクトル化評価を試みる
    try:
        # 名前空間の構築
        namespace = {
            "sin": np.sin,
            "cos": np.cos,
            "tan": np.tan,
            "exp": np.exp,
            "log": np.log,
            "sqrt": np.sqrt,
            "abs": np.abs,
            "max": np.maximum,
            "min": np.minimum,
            "pow": np.power,
            "round": np.round,
            "pi": np.pi,
            "e": np.e,
        }
        
        # データの準備（None -> NaN）
        # data values might be lists or arrays.
        length = 0
        for col_name in used_cols:
            vals = data[col_name]
            if length == 0:
                length = len(vals)
            
            if isinstance(vals, np.ndarray) and np.issubdtype(vals.dtype, np.number):
                arr = vals.astype(float)
            else:
                # Handle None in list
                arr = np.array([v if v is not None else np.nan for v in vals], dtype=float)
            namespace[col_name] = arr
            
        if length == 0 and not used_cols:
             # Constant expression? Need length from somewhere? 
             # Or just return scalar?
             # If no columns used, we can't infer length easily unless passed.
             # But 'evaluate' operates on a collection, so it implies 1 result per row.
             # If completely constant "1 + 1", we might need length.
             # For now assume at least one column or we can't vectorize over rows properly without knowing count.
             # Return scalar if no columns?
             pass

        # 評価実行
        with np.errstate(all='ignore'):
            res = eval(expression, {"__builtins__": {}}, namespace)
            
        # 結果がNumPy配列でなければ（スカラー等）、配列にブロードキャスト
        # If scalar and we know length, broadcast.
        if np.isscalar(res):
            # If no columns used "1+1", we need length.
            # But the pure function interface takes 'data'.
            # If 'data' is empty (no columns used), we don't know length.
            # Maybe pass length explicitly?
            # For now focus on column usage.
            # If used_cols was empty, length is 0 from loop above.
            if length > 0:
                 res = np.full(length, res)
            else:
                 # If no columns, return single value list? Or raise?
                 # If passed empty data dict but expected len N.. 
                 # Let's handle generic case in fallback or assume data has columns.
                 pass

        if isinstance(res, np.ndarray):
             # 結果をリストに変換 (NaN -> None)
             # Handle 0-d array
             if res.ndim == 0:
                 if length > 0:
                      res = np.full(length, res)
                 else:
                      return [res.item() if not np.isnan(res) else None]

             result_values = [None if np.isnan(v) else v for v in res.tolist()]
             return result_values
        elif isinstance(res, (int, float)):
             return [res if not np.isnan(res) else None] # Constant result?
        else:
             raise ValueError("Vectorized evaluation returned non-array")

    except Exception:
        # ベクトル評価に失敗した場合は、従来の行ごとの評価にフォールバック
        try:
            # Need length
            length = 0
            if data:
                 length = len(next(iter(data.values())))
            
            result_values = []
            
            # 数学関数（スカラー用）
            math_funcs = {
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "exp": math.exp,
                "log": math.log,
                "sqrt": math.sqrt,
                "abs": abs,
                "max": max,
                "min": min,
                "pow": math.pow,
                "round": round,
                "pi": math.pi,
                "e": math.e,
            }
    
            # 各行に対して式を評価
            cols_data = {col: data[col] for col in used_cols}
            
            for i in range(length):
                row_data = {}
                is_row_valid = True
                
                # 値の取得とNoneチェック
                for col in used_cols:
                    if i < len(cols_data[col]):
                        val = cols_data[col][i]
                    else:
                        val = None
                        
                    if val is None:
                        is_row_valid = False
                        break
                    row_data[col] = val
                    
                if not is_row_valid:
                     result_values.append(None)
                     continue
    
                eval_namespace = dict(row_data)
                eval_namespace.update(math_funcs)
    
                restricted_globals = {"__builtins__": {}}
                try:
                     row_result = eval(expression, restricted_globals, eval_namespace)
                     result_values.append(row_result)
                except (ValueError, TypeError, ZeroDivisionError):
                     result_values.append(None)
            
            return result_values
        
        except Exception as e:
             raise ValueError(f"式の評価中にエラーが発生しました: {str(e)}")

# --- 変換操作 (transform.pyから統合) ---

def sin(values: np.ndarray, degrees: bool = False) -> np.ndarray:
    """正弦(sin)を計算します。

    Args:
        values (np.ndarray): 入力値の配列。
        degrees (bool, optional): 入力が度数法(degree)かどうか。Trueの場合はラジアンに変換してから計算します。デフォルトは False（ラジアン）。

    Returns:
        np.ndarray: 計算結果の配列。
    """
    if degrees:
        values = np.radians(values)
    return np.sin(values)

def cos(values: np.ndarray, degrees: bool = False) -> np.ndarray:
    """余弦(cos)を計算します。

    Args:
        values (np.ndarray): 入力値の配列。
        degrees (bool, optional): 入力が度数法(degree)かどうか。Trueの場合はラジアンに変換してから計算します。デフォルトは False（ラジアン）。

    Returns:
        np.ndarray: 計算結果の配列。
    """
    if degrees:
        values = np.radians(values)
    return np.cos(values)

def tan(values: np.ndarray, degrees: bool = False) -> np.ndarray:
    """正接(tan)を計算します。

    Args:
        values (np.ndarray): 入力値の配列。
        degrees (bool, optional): 入力が度数法(degree)かどうか。Trueの場合はラジアンに変換してから計算します。デフォルトは False（ラジアン）。

    Returns:
        np.ndarray: 計算結果の配列。
    """
    if degrees:
        values = np.radians(values)
    return np.tan(values)

def exp(values: np.ndarray) -> np.ndarray:
    """指数関数(exp)を計算します。

    Args:
        values (np.ndarray): 入力値の配列。

    Returns:
        np.ndarray: 計算結果の配列。
    """
    return np.exp(values)

def log(values: np.ndarray, base: float = math.e) -> np.ndarray:
    """対数(log)を計算します。

    0以下の値はNaNになります。

    Args:
        values (np.ndarray): 入力値の配列。
        base (float, optional): 対数の底。デフォルトは e（自然対数）。

    Returns:
        np.ndarray: 計算結果の配列。
    """
    # Ensure values are float
    values = values.astype(float)
    
    with np.errstate(divide='ignore', invalid='ignore'):
        if base == math.e:
            res_arr = np.log(values)
        elif base == 10:
            res_arr = np.log10(values)
        else:
            res_arr = np.log(values) / np.log(base)
            
    # Mask <=0 to NaN (consistent with original implementation)
    # Note: np.log(-1) is NaN, but np.log(0) is -inf. 
    # Original explicitly set <=0 to NaN.
    mask_le_zero = (values <= 0)
    res_arr[mask_le_zero] = np.nan
    
    return res_arr

def sqrt(values: np.ndarray) -> np.ndarray:
    """平方根(sqrt)を計算します。

    負の値はNaNになります。

    Args:
        values (np.ndarray): 入力値の配列。

    Returns:
        np.ndarray: 計算結果の配列。
    """
    with np.errstate(invalid='ignore'):
         return np.sqrt(values)

def power(values: np.ndarray, exponent: float) -> np.ndarray:
    """累乗(power)を計算します。

    Args:
        values (np.ndarray): 基数の配列。
        exponent (float): 指数。

    Returns:
        np.ndarray: 計算結果の配列。
    """
    with np.errstate(invalid='ignore'):
        return np.power(values, exponent)

def abs_values(values: np.ndarray) -> np.ndarray:
    """絶対値(absolute value)を計算します。

    Args:
        values (np.ndarray): 入力値の配列。

    Returns:
        np.ndarray: 計算結果の配列。
    """
    return np.abs(values)

def round_values(values: np.ndarray, decimals: int = 0) -> np.ndarray:
    """値を指定された桁数で丸めます。

    Args:
        values (np.ndarray): 入力値の配列。
        decimals (int, optional): 丸める小数点以下の桁数。デフォルトは 0。

    Returns:
        np.ndarray: 計算結果の配列。
    """
    return np.round(values, decimals)

def normalize(values: np.ndarray, method: str = "minmax") -> np.ndarray:
    """値を正規化します。

    Args:
        values (np.ndarray): 入力値の配列。
        method (str, optional): 正規化方法。
            'minmax': 最小値を0、最大値を1にスケーリング。
            'zscore': 平均を0、標準偏差を1に標準化。デフォルトは "minmax"。

    Returns:
        np.ndarray: 正規化された配列。

    Raises:
        ValueError: 指定されたメソッドが無効な場合。
        
    Examples:
        >>> from tascpy.analytics.functional.math import normalize
        >>> import numpy as np
        >>> normalize(np.array([0, 5, 10]), method="minmax")
        array([0. , 0.5, 1. ])
    """
    values = values.astype(float)
    result_arr = np.full(len(values), np.nan)
    
    valid_mask = ~np.isnan(values)
    if not np.any(valid_mask):
         return result_arr
         
    valid_arr = values[valid_mask]

    if method == "minmax":
        min_val = np.min(valid_arr)
        max_val = np.max(valid_arr)

        if max_val == min_val:
            result_arr[valid_mask] = 0.5
        else:
            # We want result corresponding to original shape
            # values[valid_mask] -> normalized
            norm_vals = (valid_arr - min_val) / (max_val - min_val)
            result_arr[valid_mask] = norm_vals

    elif method == "zscore":
        mean = np.mean(valid_arr)
        variance = np.var(valid_arr)
        
        if variance < 1e-10:
             result_arr[valid_mask] = 0.0
        else:
             std_dev = np.sqrt(variance)
             norm_vals = (valid_arr - mean) / std_dev
             result_arr[valid_mask] = norm_vals
             
    else:
        raise ValueError(f"methodは['minmax', 'zscore']のいずれかを指定してください")
            
    return result_arr



# --- Arithmetic Operations (from arithmetic.py) ---


def add(
    v1: Union[np.ndarray, float], 
    v2: Union[np.ndarray, float], 
) -> np.ndarray:
    """2つの値または配列を加算します。

    Args:
        v1 (Union[np.ndarray, float]): 最初の値または配列。
        v2 (Union[np.ndarray, float]): 2番目の値または配列。

    Returns:
        np.ndarray: 加算結果。
    """
    return np.add(v1, v2)

def subtract(
    v1: Union[np.ndarray, float], 
    v2: Union[np.ndarray, float], 
) -> np.ndarray:
    """v1 から v2 を減算します。

    Args:
        v1 (Union[np.ndarray, float]): 最初の値または配列。
        v2 (Union[np.ndarray, float]): 引く値または配列。

    Returns:
        np.ndarray: 減算結果。
    """
    return np.subtract(v1, v2)

def multiply(
    v1: Union[np.ndarray, float], 
    v2: Union[np.ndarray, float], 
) -> np.ndarray:
    """2つの値または配列を乗算します。

    Args:
        v1 (Union[np.ndarray, float]): 最初の値または配列。
        v2 (Union[np.ndarray, float]): 2番目の値または配列。

    Returns:
        np.ndarray: 乗算結果。
    """
    return np.multiply(v1, v2)

def divide(
    v1: Union[np.ndarray, float], 
    v2: Union[np.ndarray, float], 
    **kwargs
) -> np.ndarray:
    """v1 を v2 で除算します。

    Args:
        v1 (Union[np.ndarray, float]): 分子となる値または配列。
        v2 (Union[np.ndarray, float]): 分母となる値または配列。
        **kwargs: 任意の追加引数。

    Returns:
        np.ndarray: 除算結果。
    """
    return np.divide(v1, v2)

def diff(
    y: Union[np.ndarray, List[float]], 
    x: Union[np.ndarray, List[float]], 
    method: str = "central"
) -> np.ndarray:
    """x, y座標から微分係数を計算します。

    Args:
        y (Union[np.ndarray, List[float]]): y座標の配列。
        x (Union[np.ndarray, List[float]]): x座標の配列。
        method (str, optional): 微分方法 ('central', 'forward', 'backward')。デフォルトは "central"。

    Returns:
        np.ndarray: 計算された微分係数の配列。

    Raises:
        ValueError: xとyの長さが異なる場合、またはデータ点が2点未満の場合、または無効なメソッドが指定された場合。
    """
    # Ensure numpy arrays
    y_arr = np.asanyarray(y, dtype=float)
    x_arr = np.asanyarray(x, dtype=float)
    
    if len(x_arr) != len(y_arr):
        raise ValueError("Length of x and y must be same")
    if len(x_arr) < 2:
        raise ValueError(f"有効なデータポイントが不足しています: {len(x_arr)} (最低2点必要)")

    if method == "central":
        try:
             result = np.gradient(y_arr, x_arr)
        except Exception:
             # Fallback? Not really needed for standard gradient
             result = np.gradient(y_arr, x_arr)
             
    elif method == "forward":
        # Forward difference: (y[i+1] - y[i]) / (x[i+1] - x[i])
        dx = np.diff(x_arr)
        dy = np.diff(y_arr)
        with np.errstate(divide='ignore', invalid='ignore'):
            d = dy / dx
        # Append last element to match length
        result = np.append(d, d[-1])
        
    elif method == "backward":
        # Backward difference
        dx = np.diff(x_arr)
        dy = np.diff(y_arr)
        with np.errstate(divide='ignore', invalid='ignore'):
            d = dy / dx
        # Insert first element to match length
        result = np.insert(d, 0, d[0])
        
    else:
        raise ValueError("Invalid method. Use 'central', 'forward', or 'backward'")

    return result

def integrate(
    y: Union[np.ndarray, List[float]], 
    x: Union[np.ndarray, List[float]], 
    method: str = "trapezoid",
    initial_value: float = 0.0
) -> np.ndarray:
    """xに対するyの積分を計算します。

    Args:
        y (Union[np.ndarray, List[float]]): y座標の配列。
        x (Union[np.ndarray, List[float]]): x座標の配列。
        method (str, optional): 積分方法。現在は "trapezoid" (台形則) のみサポート。デフォルトは "trapezoid"。
        initial_value (float, optional): 積分初期値。デフォルトは 0.0。

    Returns:
        np.ndarray: 計算された積分の配列（累積和）。

    Raises:
        ValueError: サポートされていないメソッドが指定された場合、またはxとyの長さが異なる場合。
    """
    if method != "trapezoid":
        raise ValueError("現在は trapezoid 積分のみサポートしています")

    y_arr = np.asanyarray(y, dtype=float)
    x_arr = np.asanyarray(x, dtype=float)

    if len(x_arr) != len(y_arr):
        raise ValueError("Length of x and y must be same")
    if len(x_arr) < 2:
        raise ValueError(f"有効なデータポイントが不足しています: {len(x_arr)} (最低2点必要)")
        
    # Check for NaNs
    if np.isnan(y_arr).any() or np.isnan(x_arr).any():
        # Standard numpy behavior implies propagation, which is fine.
        pass

    # Sort if x is not monotonic?
    # To support integration of scattered data, we sort by x.
    # This matches original implementation behavior.
    
    # Check if sorted
    is_sorted = True
    if len(x_arr) > 1:
        if x_arr[0] < x_arr[-1]: # Simple check? No, need full check
             # If strictly increasing
             if np.any(np.diff(x_arr) < 0):
                 is_sorted = False
        else:
             # Could be decreasing or random
             is_sorted = False
             
    if not is_sorted:
        sorted_indices = np.argsort(x_arr)
        x_sorted = x_arr[sorted_indices]
        y_sorted = y_arr[sorted_indices]
    else:
        x_sorted = x_arr
        y_sorted = y_arr

    # 1. First step (0 to x[0])
    dx0 = x_sorted[0]
    first_term = dx0 * y_sorted[0]
    val0 = initial_value + first_term
    
    # 2. Subsequent steps
    dx_rest = np.diff(x_sorted)
    y_sum = y_sorted[1:] + y_sorted[:-1]
    dy_avg = y_sum / 2.0
    
    areas = dx_rest * dy_avg
    cum_areas = np.cumsum(areas)
    
    result_sorted = np.zeros(len(x_arr))
    result_sorted[0] = val0
    result_sorted[1:] = val0 + cum_areas
    
    # Unsort if needed
    if not is_sorted:
        result = np.empty_like(result_sorted)
        result[sorted_indices] = result_sorted
        return result
    else:
        return result_sorted

def average_across(*columns: np.ndarray, ignore_nan: bool = True) -> np.ndarray:
    """複数列間で、各行ごとの平均値を計算します。

    Args:
        *columns (np.ndarray): 対象となる複数列のNumPy配列
        ignore_nan (bool, optional): 欠損値（NaN）を無視して平均するかどうか。
            Trueの場合、NaNが含まれていても他の有効な値から平均を計算します。
            Falseの場合、NaNが含まれる行の結果はNaNになります。デフォルトは True。

    Returns:
        np.ndarray: 計算された行ごとの平均値を含む配列。
    """
    if not columns:
        raise ValueError("少なくとも1つの列を指定する必要があります。")
        
    # Stack arrays horizontally to form a 2D matrix
    stacked = np.column_stack(columns)
    
    # Calculate row-wise mean with or without ignoring nans
    with np.errstate(invalid='ignore'):  # Ignore empty slice warnings for all-NaN rows
        if ignore_nan:
            return np.nanmean(stacked, axis=1)
        else:
            return np.mean(stacked, axis=1)
