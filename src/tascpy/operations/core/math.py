from typing import Union, Optional, List, Dict, Any, Set
from ...core.collection import ColumnCollection
from ...core.column import Column, NumberColumn, detect_column_type
from ..registry import operation
from ..abstraction import (
    transform_column, 
    handle_zero_division,
    store_result,
    handle_missing_values,
    inject_columns
)
import re
import ast
import math
import inspect
import numpy as np
from ...functional import arithmetic
from ...functional import math as functional_math
from ..registry import operation, register_functional


def _safe_add_naming(func_name, col1, col2, **kwargs):
    return f"{col1}+{col2}"

def _safe_sub_naming(func_name, col1, col2, **kwargs):
    return f"{col1}-{col2}"

def _safe_mul_naming(func_name, col1, col2, **kwargs):
    # Add parentheses if needed for precedence
    c1_str = str(col1)
    if any(op in c1_str for op in ["+", "-"]):
        c1_str = f"({c1_str})"
    return f"{c1_str}*{col2}"

def _safe_div_naming(func_name, col1, col2, **kwargs):
    c1_str = str(col1)
    if any(op in c1_str for op in ["+", "-"]):
        c1_str = f"({c1_str})"
    return f"{c1_str}/{col2}"


add = register_functional(
    arithmetic.add,
    domain="core",
    name="add",
    transform_column={"num_inputs": 2, "result_naming": _safe_add_naming},
)

subtract = register_functional(
    arithmetic.subtract,
    domain="core",
    name="subtract",
    transform_column={"num_inputs": 2, "result_naming": _safe_sub_naming},
)

multiply = register_functional(
    arithmetic.multiply,
    domain="core",
    name="multiply",
    transform_column={"num_inputs": 2, "result_naming": _safe_mul_naming},
)

divide = register_functional(
    arithmetic.divide,
    domain="core",
    name="divide",
    transform_column={"num_inputs": 2, "result_naming": _safe_div_naming},
    extra_decorators=[handle_zero_division(numerator_idx=0, denominator_idx=1)]
)

# 微分と積分の関数を定義

def _diff_naming(func_name, y_col, x_col, **kwargs):
    return f"d({y_col})/d({x_col})"

def _diff_unit_inference(collection, y_col, x_col, **kwargs):
    y_obj = collection[y_col] if isinstance(y_col, str) and y_col in collection.columns else None
    x_obj = collection[x_col] if isinstance(x_col, str) and x_col in collection.columns else None
    
    y_unit = getattr(y_obj, "unit", "") or ""
    x_unit = getattr(x_obj, "unit", "") or ""
    return f"{y_unit}/{x_unit}" if y_unit or x_unit else None

def _integrate_naming(func_name, y_col, x_col, **kwargs):
    return f"∫{y_col}·d{x_col}"

def _integrate_unit_inference(collection, y_col, x_col, **kwargs):
    y_obj = collection[y_col] if isinstance(y_col, str) and y_col in collection.columns else None
    x_obj = collection[x_col] if isinstance(x_col, str) and x_col in collection.columns else None
    
    y_unit = getattr(y_obj, "unit", "") or ""
    x_unit = getattr(x_obj, "unit", "") or ""
    return f"{y_unit}·{x_unit}" if y_unit or x_unit else None


diff = register_functional(
    arithmetic.diff,
    domain="core",
    name="diff",
    store_result={"result_naming": _diff_naming, "unit_inference": _diff_unit_inference},
    inject_columns={"num_inputs": 2},
    extra_decorators=[handle_missing_values(strategy="strict")],
    signature_override={
        "y": ("y_values", np.ndarray),
        "x": ("x_values", np.ndarray),
        "method": (str, "central")
    }
)


integrate = register_functional(
    arithmetic.integrate,
    domain="core",
    name="integrate",
    store_result={"result_naming": _integrate_naming, "unit_inference": _integrate_unit_inference},
    inject_columns={"num_inputs": 2},
    extra_decorators=[handle_missing_values(strategy="strict")],
    signature_override={
        "y": ("y_values", np.ndarray),
        "x": ("x_values", np.ndarray),
        "method": (str, "trapezoid"),
        "initial_value": (float, 0.0)
    }
)


def _evaluate_naming(func_name, expression, *args, **kwargs):
    return f"expression_result"

def _evaluate_unit_inference(collection, expression, **kwargs):
    try:
        # AST parsing to find variable names (simplified version of what's in evaluate)
        parsed_ast = ast.parse(expression, mode="eval")
        for node in ast.walk(parsed_ast):
            if isinstance(node, ast.Name) and node.id not in {
                "sin", "cos", "tan", "exp", "log", "sqrt", "abs", 
                "max", "min", "pow", "round", "pi", "e"
            }:
                if node.id in collection.columns:
                    return getattr(collection[node.id], "unit", None)
    except:
        pass
    return None

def _evaluate_adapter(
    collection: ColumnCollection,
    expression: str,
    **kwargs
) -> Union[List[Optional[float]], np.ndarray]:
    
    # Prepare data dictionary for pure function
    # Extract all columns
    data_map = {}
    
    # Add columns
    for name, col in collection.columns.items():
        data_map[name] = col.values
        
    # Add results if accessible via keys? 
    # Let's iterate over results too if available.
    if hasattr(collection, "_results"):
         for name, res in collection._results.items():
            # AnalysisResult might need unpacking or might not be compatible.
            # Only include if it looks like data
            # For now ignore results to match original behavior (which filtered by collection.columns)
            pass
             
    return functional_math.evaluate_expression(data_map, expression)


evaluate = register_functional(
    _evaluate_adapter,
    domain="core",
    name="evaluate",
    store_result={
        "result_naming": _evaluate_naming,
        "unit_inference": _evaluate_unit_inference
    },
    signature_override={
        "collection": ("collection", ColumnCollection),
        "expression": (str, inspect.Parameter.empty)
    }
)
