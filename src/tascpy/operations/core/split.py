from typing import Any, List, Dict, Optional, Union
import numpy as np
from ...core.collection import ColumnCollection
from ..registry import operation
from ..abstraction import split_result, inject_length


def _split_by_integers_indices(markers: Union[List[int], np.ndarray]) -> List[np.ndarray]:
    """Pure function to calculate split indices based on integer markers"""
    if isinstance(markers, list):
        markers = np.array(markers)
        
    unique_markers = np.unique(markers)
    # np.unique returns sorted unique elements
    
    indices_list = []
    for marker in unique_markers:
        # np.where returns tuple (indices,)
        idx = np.where(markers == marker)[0]
        indices_list.append(idx)
        
    return indices_list


def _split_at_indices_slices(length: int, indices: Union[int, List[int]]) -> List[slice]:
    """Pure function to calculate split slices based on indices"""
    if isinstance(indices, int):
        indices_list = [indices]
    else:
        indices_list = sorted(list(set(indices)))

    # validate indices
    for idx in indices_list:
        if idx < 0 or idx > length:
            raise IndexError(f"インデックス {idx} は範囲外です (0-{length})")

    # Create split points (0 and length included)
    split_points = [0] + indices_list + [length]
    # Remove duplicates and sort (though already sorted/handled)
    split_points = sorted(list(set(split_points)))

    slices = []
    for i in range(len(split_points) - 1):
        start = split_points[i]
        end = split_points[i + 1]
        # Skip empty? Original implementation did not explicitly skip, but empty range is valid.
        slices.append(slice(start, end))
        
    return slices


@operation(domain="core")
@split_result
@inject_length
def split_by_integers(
    length: int, markers: List[int]
) -> Any: # Returns List[ColumnCollection] via decorator
    """整数リストの値でデータを分割します
    
    Args:
        length: データの長さ (Decoratorにより自動注入)
        markers: 各データ値がどのグループに属するかを示す整数リスト（データと同じ長さ）
        
    Returns:
        List[ColumnCollection]: 分割後の ColumnCollection オブジェクトのリスト。
    """
    if length != len(markers):
         raise ValueError(
             f"{length}vs{len(markers)}:データリストとマーカーリストの長さは一致する必要があります."
         )
         
    return _split_by_integers_indices(markers)


@operation(domain="core")
@split_result
@inject_length
def split_at_indices(
    length: int, indices: Union[int, List[int]]
) -> Any: # Returns List[ColumnCollection] via decorator
    """指定されたインデックスでコレクションを分割します
    
    Args:
        length: データの長さ (Decoratorにより自動注入)
        indices: 分割するインデックス（intまたはList[int]）
        
    Returns:
        List[ColumnCollection]: 分割後の ColumnCollection オブジェクトのリスト
    """
    return _split_at_indices_slices(length, indices)

