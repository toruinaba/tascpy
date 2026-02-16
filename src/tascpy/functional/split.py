from typing import List, Union
import numpy as np

def split_by_integers(
    length: int, 
    markers: Union[List[int], np.ndarray],
) -> List[np.ndarray]:
    """Calculate split indices based on integer markers."""
    if length != len(markers):
         raise ValueError(
             f"{length}vs{len(markers)}:データリストとマーカーリストの長さは一致する必要があります."
         )

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

def split_at_indices(
    length: int,
    indices: Union[int, List[int]],
) -> List[slice]:
    """Calculate split slices based on indices."""
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
