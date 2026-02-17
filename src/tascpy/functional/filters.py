
from typing import Any, List, Union, Optional
import numpy as np
from . import stats as functional_stats

def remove_outliers_mask(
    vals: Any,
    window_size: int = 3,
    threshold: float = 0.5,
    edge_handling: str = "asymmetric",
    min_abs_value: float = 1e-10,
    scale_factor: float = 1.0,
) -> List[bool]:
    """
    Generate mask to remove outliers.
    Returns True for kept values (non-outliers), False for outliers.
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
    """
    Filter values by condition.
    Returns boolean mask (True to keep).
    """
    # vals is numpy array or list
    return [condition(val) for val in vals]

def remove_steps_mask(
    step_values: Union[List[Any], np.ndarray],
    steps: List[Any], 
    tolerance: Optional[float] = None
) -> List[bool]:
    """
    Generate mask to remove specific steps.
    Returns True for kept steps.
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
