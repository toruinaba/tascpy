from typing import Any, Callable, Optional, Dict

def basic_naming(func_name: str, *args, **kwargs) -> str:
    """
    Standard naming: func(col)
    Assumes first arg or 'column' kwarg is the column name.
    """
    col = _get_col_name(args, kwargs)
    return f"{func_name}({col})"

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
    def namer(func_name: str, *args, **kwargs):
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
             return f"{func_name}({col})"
        except KeyError as e:
            # Fallback for missing keys
            return f"{func_name}_result"

    return namer

def infix_naming(operator: str, safe: bool = True) -> Callable:
    """
    Returns a naming function for binary operations: col1 op col2.
    
    Args:
        operator: String operator (e.g., "+", "-", "*").
        safe: If True, wraps operands in parentheses if they contain operators.
    """
    def namer(func_name: str, *args, **kwargs):
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
        return f"{func_name}_result"

    return namer

def _get_col_name(args, kwargs) -> Optional[str]:
    """Helper to extract column name from args or kwargs"""
    if len(args) > 0:
        return str(args[0])
    return str(kwargs.get("column")) if "column" in kwargs else None
