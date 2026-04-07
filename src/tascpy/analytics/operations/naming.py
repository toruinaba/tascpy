import math
from typing import Callable, Optional, Dict, Any

def log_naming(func_name: str, *args, **kwargs) -> str:
    """
    Naming for log functions.
    Handles 'base' argument (as positional arg index 1 or kwarg).
    """
    col = _get_col_name(args, kwargs)
    
    # Extract base
    base = kwargs.get("base", math.e)
    if len(args) > 1:
        base = args[1]
        
    if base == math.e:
        return f"log({col})"
    elif base == 10:
        return f"log10({col})"
    else:
        return f"log{base}({col})"

def callable_naming(callable_arg: str, name_arg: str = "func_name", default: str = "result") -> Callable:
    """
    Returns a naming function that uses a callable argument's name or a specific name argument.
    
    Args:
        callable_arg: Name of the argument (kwarg) that holds the callable (e.g. "combine_func").
        name_arg: Name of the argument (kwarg) that might hold an explicit name (e.g. "func_name").
        default: Default suffix if no name can be determined.
    """
    def namer(operation_name: str, *args, **kwargs):
        # 1. Check explicit name arg (e.g. func_name="my_add")
        if name_arg in kwargs and kwargs[name_arg]:
             return kwargs[name_arg]
             
        # 2. Check callable argument
        # We need to find the callable. It might be in kwargs or args.
        # But we don't know the position for args easily without more info.
        # In custom_combine case: (v1, v2, combine_func, func_name)
        # combine_func is 3rd arg (index 2) usually if positional.
        # But for generic usage, we might rely on kwargs if possible, or simple heuristic.
        
        # Taking a simpler approach: check kwargs first.
        func_obj = kwargs.get(callable_arg)
        
        # If not in kwargs, and we need to check args?
        # This helper might need to know the position of callable_arg if it's positional.
        if func_obj and hasattr(func_obj, "__name__") and func_obj.__name__ != "<lambda>":
            return func_obj.__name__
            
        return f"{operation_name}_{default}"

    return namer

def basic_naming(operation_name: str, *args, **kwargs) -> str:
    """
    Standard naming: func(col)
    Assumes first arg or 'column' kwarg is the column name.
    """
    col = _get_col_name(args, kwargs)
    return f"{operation_name}({col})"

def format_naming(pattern: str, defaults: Optional[Dict[str, Any]] = None, arg_names: Optional[list] = None) -> Callable:
    """
    Returns a naming function that formats a string pattern.
    
    Args:
        pattern: Format string (e.g., "ma{window_size}({0})").
                 Positional placeholders {0}, {1} map to args.
                 Named placeholders {param} map to kwargs.
        defaults: Default values for kwargs if missing.
        arg_names: List of argument names to map positional args to kwargs.
                   e.g. ["column", "exponent"] maps args[0] to params["column"], args[1] to params["exponent"].
    """
    def namer(operation_name: str, *args, **kwargs):
        # Merge defaults
        params = {}
        if defaults:
            params.update(defaults)
        params.update(kwargs)
        
        # Map positional args to names if provided
        if arg_names:
            for i, name in enumerate(arg_names):
                if i < len(args):
                    params[name] = args[i]
        
        try:
            return pattern.format(*args, **params)
        except IndexError:
            # Fallback if pattern expects more args than provided
            # e.g. {0} but no args
             col = _get_col_name(args, kwargs) or "unknown"
             return f"{operation_name}({col})"
        except KeyError as e:
            # Fallback for missing keys
            return f"{operation_name}_result"

    return namer

def infix_naming(operator: str, safe: bool = True) -> Callable:
    """
    Returns a naming function for binary operations: col1 op col2.
    
    Args:
        operator: String operator (e.g., "+", "-", "*").
        safe: If True, wraps operands in parentheses if they contain operators.
    """
    def namer(operation_name: str, *args, **kwargs):
        if len(args) >= 2:
            col1 = str(args[0])
            col2 = str(args[1])
            
            if safe:
                if any(op in col1 for op in ["+", "-"]):
                    col1 = f"({col1})"
                if any(op in col2 for op in ["+", "-"]):
                    col2 = f"({col2})"
            
            return f"{col1}{operator}{col2}"
        elif len(args) == 1:
            # Unary naming fallback (e.g. -col)? or just return standard
            col = args[0]
            return f"{operator}{col}"
        return f"{operation_name}_result"

    return namer

def _get_col_name(args, kwargs) -> Optional[str]:
    """Helper to extract column name from args or kwargs"""
    if len(args) > 0:
        return str(args[0])
    return str(kwargs.get("column")) if "column" in kwargs else None
