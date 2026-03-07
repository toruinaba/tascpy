import numpy as np
from typing import Tuple, Optional

def compute_stress(load_vals: np.ndarray, area: float) -> np.ndarray:
    """応力を計算する純粋関数

    Args:
        load_vals: 荷重配列
        area: 断面積

    Returns:
        np.ndarray: 応力配列
        
    Examples:
        >>> from tascpy.analytics.functional.strain.ss_analysis import compute_stress
        >>> import numpy as np
        >>> compute_stress(np.array([1000, 2000]), 10.0)
        array([100., 200.])
    """
    return load_vals / area

