
from typing import Union, Optional, List, Dict, Any, Mapping, Set
import numpy as np
import ast
import math

_EXPR_FUNCTIONS = {
    "log": np.log, "sqrt": np.sqrt, "abs": np.abs, "max": np.maximum, "min": np.minimum,
    "pow": np.power, "round": np.round,
}
_EXPR_CONSTANTS = {"pi": np.pi, "e": np.e}
_EXPR_NODES = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare, ast.IfExp, ast.Call, ast.Name,
    ast.Load, ast.Constant, ast.operator, ast.unaryop, ast.boolop, ast.cmpop,
)


class _Vectorize(ast.NodeTransformer):
    """配列で評価できない構文（三項演算子・and/or/not・連続比較）を numpy の関数呼び出しに置き換える"""

    @staticmethod
    def _call(name: str, *args: ast.expr) -> ast.Call:
        return ast.Call(func=ast.Name(id=name, ctx=ast.Load()), args=list(args), keywords=[])

    def visit_IfExp(self, node: ast.IfExp) -> ast.AST:
        self.generic_visit(node)
        return self._call("__where", node.test, node.body, node.orelse)

    def visit_BoolOp(self, node: ast.BoolOp) -> ast.AST:
        self.generic_visit(node)
        name = "__and" if isinstance(node.op, ast.And) else "__or"
        result = node.values[0]
        for value in node.values[1:]:
            result = self._call(name, result, value)
        return result

    def visit_UnaryOp(self, node: ast.UnaryOp) -> ast.AST:
        self.generic_visit(node)
        return self._call("__not", node.operand) if isinstance(node.op, ast.Not) else node

    def visit_Compare(self, node: ast.Compare) -> ast.AST:
        self.generic_visit(node)
        operands = [node.left, *node.comparators]
        parts = [ast.Compare(left=l, ops=[op], comparators=[r]) for l, op, r in zip(operands, node.ops, operands[1:])]
        result: ast.expr = parts[0]
        for part in parts[1:]:
            result = self._call("__and", result, part)
        return result


def evaluate_expression(
    data: Mapping[str, Union[np.ndarray, List[Any]]],
    expression: str,
) -> np.ndarray:
    """列名を変数とした数式を、numpy で要素ごとに評価します。

    使える構文は四則演算・べき乗・比較・and / or / not・三項演算子（a if 条件 else b）と、
    関数 log, sqrt, abs, max, min, pow, round、定数 pi, e です。属性アクセスなどそれ以外の構文は使えません。
    欠損 (NaN / None) を含む行や、計算結果が無限大・未定義になる行は NaN になります。

    Args:
        data: {列名: 値の配列}
        expression: 数式（例: "A + B * 2", "A if A > 3 else 0"）

    Returns:
        np.ndarray: 計算結果の配列

    Raises:
        ValueError: 構文エラー、使えない構文・関数、または数値に変換できない列を使った場合
        KeyError: 式に含まれる列名が data にない場合

    Examples:
        >>> import numpy as np
        >>> from tascpy.analytics.functional.core.math import evaluate_expression
        >>> evaluate_expression({"A": np.array([1, 2]), "B": np.array([3, 4])}, "A + B * 2")
        array([ 7., 10.])
        >>> evaluate_expression({"A": np.array([1.0, 5.0])}, "A if A > 3 else 0")
        array([0., 5.])
    """
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as e:
        raise ValueError(f"式の構文エラー (行:{e.lineno}, 列:{e.offset}): {e.msg}") from e

    names = set()
    for node in ast.walk(tree):
        if not isinstance(node, _EXPR_NODES):
            raise ValueError(f"式に使えない構文が含まれています ({type(node).__name__}): {expression}")
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in _EXPR_FUNCTIONS or node.keywords:
                raise ValueError(f"許可されていない関数呼び出しです: {ast.unparse(node.func)}")
        elif isinstance(node, ast.Name) and node.id not in _EXPR_FUNCTIONS and node.id not in _EXPR_CONSTANTS:
            names.add(node.id)

    missing = names - set(data)
    if missing:
        raise KeyError(f"式に存在しないカラム名が含まれています: {', '.join(sorted(missing))}")

    namespace: Dict[str, Any] = {
        **_EXPR_FUNCTIONS, **_EXPR_CONSTANTS,
        "__where": np.where, "__and": np.logical_and, "__or": np.logical_or, "__not": np.logical_not,
    }
    for name in names:
        try:
            namespace[name] = np.asarray(data[name], dtype=float)
        except (TypeError, ValueError) as e:
            raise ValueError(f"列 '{name}' は数値に変換できません") from e

    code = compile(ast.fix_missing_locations(_Vectorize().visit(tree)), "<expression>", "eval")
    with np.errstate(all="ignore"):
        result = np.asarray(eval(code, {"__builtins__": {}}, namespace), dtype=float)

    length = len(next(iter(data.values()))) if data else 1
    if result.ndim == 0:
        result = np.full(length, float(result))
    missing = np.zeros(len(result), dtype=bool)
    for name in names:
        missing |= np.isnan(namespace[name])
    return np.where(np.isfinite(result) & ~missing, result, np.nan)


# --- 変換操作 (transform.pyから統合) ---

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
) -> np.ndarray:
    """v1 を v2 で除算します。

    Args:
        v1 (Union[np.ndarray, float]): 分子となる値または配列。
        v2 (Union[np.ndarray, float]): 分母となる値または配列。

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
    """x に対する y の累積積分 ∫y dx を、データの並び順に沿って台形則で計算します。

    x が増減する場合（荷重-変位の往復など）も並べ替えず、経路に沿って積分します。
    先頭の値は initial_value です。

    Args:
        y (Union[np.ndarray, List[float]]): y の配列。
        x (Union[np.ndarray, List[float]]): x の配列。
        method (str, optional): 積分方法。"trapezoid"（台形則）のみ。
        initial_value (float, optional): 積分の初期値。デフォルトは 0.0。

    Returns:
        np.ndarray: 累積積分の配列（欠損を含む区間以降は NaN）。

    Raises:
        ValueError: サポートされていないメソッドの場合、x と y の長さが異なる場合、2点未満の場合。

    Examples:
        >>> import numpy as np
        >>> from tascpy.analytics.functional.core.math import integrate
        >>> integrate(y=[1.0, 1.0, 1.0], x=[10.0, 11.0, 12.0])
        array([0., 1., 2.])
        >>> integrate(y=[0.0, 2.0, 2.0], x=[0.0, 1.0, 0.0])
        array([ 0.,  1., -1.])
    """
    if method != "trapezoid":
        raise ValueError("現在は trapezoid 積分のみサポートしています")

    y_arr = np.asarray(y, dtype=float)
    x_arr = np.asarray(x, dtype=float)
    if len(x_arr) != len(y_arr):
        raise ValueError("x と y の長さが一致しません")
    if len(x_arr) < 2:
        raise ValueError(f"有効なデータポイントが不足しています: {len(x_arr)} (最低2点必要)")

    areas = np.diff(x_arr) * (y_arr[1:] + y_arr[:-1]) / 2.0
    return initial_value + np.concatenate([[0.0], np.cumsum(areas)])
