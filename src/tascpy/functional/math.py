
from typing import Union, Optional, List, Dict, Any, Set
import numpy as np
import ast
import math

def evaluate_expression(
    data: Dict[str, Union[np.ndarray, List[Any]]],
    expression: str,
) -> List[Optional[float]]:
    """
    Evaluate a mathematical expression using columns in data.
    Returns a list of values (with None for invalid/missing/error).
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
