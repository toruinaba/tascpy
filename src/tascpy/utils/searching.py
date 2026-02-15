from typing import Any, Optional, Union
import numpy as np

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
