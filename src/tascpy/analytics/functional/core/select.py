
from typing import List, Optional, Dict, Any, Union, Tuple, TypeVar, Callable
import numpy as np

def select_indices(
    step_values: Union[List[Union[int, float]], np.ndarray],
    indices: Optional[List[int]] = None,
    steps: Optional[List[Union[int, float]]] = None,
    by_step_value: bool = True,
    tolerance: Optional[float] = None,
) -> Tuple[List[int], Dict[str, Any]]:
    """指定されたステップまたはインデックスに基づいてデータを選択するためのインデックスを計算します。

    Args:
        step_values (Union[List[Union[int, float]], np.ndarray]): ステップ値のリストまたは配列。
        indices (Optional[List[int]], optional): 直接指定するインデックスのリスト。デフォルトは None。
        steps (Optional[List[Union[int, float]]], optional): 選択するステップ値またはインデックスのリスト。デフォルトは None。
        by_step_value (bool, optional): `steps` をステップ値として扱うかどうか。Falseの場合はインデックスとして扱います。デフォルトは True。
        tolerance (float, optional): ステップ値一致判定の許容誤差。指定された場合、許容誤差内の最も近い値を選択します。デフォルトは None。

    Returns:
        Tuple[List[int], Dict[str, Any]]: 
            (選択されたインデックスのリスト, 実行結果のメタデータ辞書) のタプル。

    Raises:
        ValueError: indices と steps の両方が指定された場合。
        
    Examples:
        >>> from tascpy.analytics.functional.select import select_indices
        >>> import numpy as np
        >>> steps_arr = np.array([0.0, 0.5, 1.0, 1.5])
        >>> indices, meta = select_indices(steps_arr, steps=[0.5, 1.0])
        >>> indices
        [1, 2]
    """
    # indicesとstepsの両方が指定された場合はエラー
    if indices is not None and steps is not None:
        raise ValueError("indicesとstepsは同時に指定できません")

    # データ長
    length = len(step_values)

    # ステップ値からインデックスへの変換処理
    final_indices = indices
    found_steps = []
    missing_steps = []
    metadata_update = {
        "operation": "select",
    }

    if steps is not None:
        metadata_update["operation"] = "select_step"
        final_indices = []  # stepsから変換されるインデックス

        if by_step_value:
            # ステップ値からインデックスに変換
            # step_values might be list or array
            is_array = isinstance(step_values, np.ndarray)
            
            for target_step in steps:
                idx = None
                if is_array:
                    # NumPy optimized search
                    if tolerance is None:
                         indices_found = np.where(step_values == target_step)[0]
                         if len(indices_found) > 0:
                             idx = int(indices_found[0])
                    else:
                         # With tolerance
                         diff = np.abs(step_values - target_step)
                         nearest_idx = np.argmin(diff)
                         if diff[nearest_idx] <= tolerance:
                             idx = int(nearest_idx)
                elif isinstance(step_values, list):
                     # List search
                     if tolerance is None:
                         try:
                              idx = step_values.index(target_step)
                         except ValueError:
                              pass
                     else:
                          for i, v in enumerate(step_values):
                              if abs(v - target_step) <= tolerance:
                                  idx = i
                                  break
                else:
                    # Generic / Numpy search fallback
                    arr_vals = np.array(step_values) if not isinstance(step_values, np.ndarray) else step_values
                    
                    if tolerance is None:
                         indices_found = np.where(arr_vals == target_step)[0]
                         if len(indices_found) > 0:
                             idx = int(indices_found[0])
                    else:
                         # With tolerance
                         diff = np.abs(arr_vals - target_step)
                         nearest_idx = np.argmin(diff)
                         if diff[nearest_idx] <= tolerance:
                             idx = int(nearest_idx)
                
                if idx is not None:
                    final_indices.append(idx)
                    found_steps.append(step_values[idx])
                else:
                    missing_steps.append(target_step)
        else:
            # 直接インデックスとして使用
            for idx in steps:
                if 0 <= idx < length:
                    final_indices.append(idx)
                    # Note: Original code accessed step_values[idx] here, assume it's safe if 0<=idx<length
                    try:
                        found_steps.append(step_values[idx])
                    except IndexError:
                         pass # Should be covered by length check but just in case
                else:
                    missing_steps.append(idx)
                    
        metadata_update.update({
            "selected_steps": found_steps,
            "missing_steps": missing_steps,
            "by_step_value": by_step_value,
        })
    
    return final_indices, metadata_update

def fetch_near_step(
    values: np.ndarray, value: float
) -> List[int]:
    """指定された値に最も近い要素のインデックスを検索します。

    Args:
        values (np.ndarray): 検索対象の数値配列。
        value (float): ターゲット値。

    Returns:
        List[int]: 最も近い値のインデックスを含むリスト（要素数1）。

    Raises:
        TypeError: values が数値型でない場合。
        ValueError: 有効なデータが見つからない場合（全てNaNなど）。
        
    Examples:
        >>> from tascpy.analytics.functional.select import fetch_near_step
        >>> import numpy as np
        >>> arr = np.array([0.0, 0.4, 0.9, 1.5])
        >>> fetch_near_step(arr, 1.0)
        [2]
    """
    # 数値型変換とチェック
    # Handle list input if necessary (though type hint says ndarray)
    if isinstance(values, list):
         values = np.array(values)
    
    if not np.issubdtype(values.dtype, np.number):
         try:
             values = values.astype(float)
         except ValueError:
             raise TypeError(f"検索対象列は数値型ではありません")

    # 絶対差分
    diff = np.abs(values - value)
    
    # NaNが含まれる場合は無視
    try:
        idx = np.nanargmin(diff)
    except ValueError:
        raise ValueError("有効なデータが見つかりません")

    return [int(idx)]

# --- 分割操作 (split.pyから統合) ---

def split_by_integers(
    length: int, 
    markers: Union[List[int], np.ndarray],
) -> List[np.ndarray]:
    """整数マーカーに基づいて分割インデックスを計算します。

    ユニークなマーカー値ごとに、そのマーカーに対応するインデックスの配列をリストとして返します。

    Args:
        length (int): データ長。
        markers (Union[List[int], np.ndarray]): 各要素に対応する整数マーカーのリストまたは配列。長さは `length` と一致する必要があります。

    Returns:
        List[np.ndarray]: 各マーカーに対応するインデックス配列のリスト。

    Raises:
        ValueError: データ長とマーカーリストの長さが一致しない場合。
        
    Examples:
        >>> from tascpy.analytics.functional.select import split_by_integers
        >>> import numpy as np
        >>> markers = np.array([1, 1, 2, 2, 3])
        >>> split_by_integers(5, markers)
        [array([0, 1]), array([2, 3]), array([4])]
    """
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
    """指定されたインデックスで分割するためのスライスを計算します。

    Args:
        length (int): データの長さ。
        indices (Union[int, List[int]]): 分割点となるインデックス（またはそのリスト）。

    Returns:
        List[slice]: 分割された各セグメントを表すスライスのリスト。

    Raises:
        IndexError: インデックスが範囲外 (0-length) の場合。
        
    Examples:
        >>> from tascpy.analytics.functional.select import split_at_indices
        >>> split_at_indices(10, [3, 7])
        [slice(0, 3, None), slice(3, 7, None), slice(7, 10, None)]
    """
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


# --- List Split operations (from utils.split.py) ---


T = TypeVar("T")


def split_list_by_chunks(data: List[T], chunk_size: int) -> List[List[T]]:
    """
    リストを指定サイズのチャンクに均等に分割します。

    Args:
        data: 分割対象のデータリスト
        chunk_size: 各チャンクのサイズ

    Returns:
        chunk_size サイズのリストを要素とするリスト
        （最後のチャンクは chunk_size より小さい場合があります）

    Raises:
        ValueError: chunk_size が 1 未満の場合

    Examples:
        >>> from tascpy.utils.split import split_list_by_chunks
        >>> data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> split_list_by_chunks(data, 3)
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        >>> split_list_by_chunks(data, 4)
        [[1, 2, 3, 4], [5, 6, 7, 8], [9]]
    """
    if chunk_size < 1:
        raise ValueError("チャンクサイズは1以上である必要があります")

    return [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]


def split_list_by_count(data: List[T], count: int) -> List[List[T]]:
    """
    リストを指定された数の部分リストに分割します。

    Args:
        data: 分割対象のデータリスト
        count: 分割後のリスト数

    Returns:
        count 個のリストからなるリスト
        （各部分リストのサイズはほぼ均等になります）

    Raises:
        ValueError: count が 1 未満の場合

    Examples:
        >>> from tascpy.utils.split import split_list_by_count
        >>> data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        >>> split_list_by_count(data, 3)
        [[1, 2, 3, 4], [5, 6, 7], [8, 9, 10]]
    """
    if count < 1:
        raise ValueError("分割数は1以上である必要があります")

    chunk_size = len(data) // count
    remainder = len(data) % count

    result = []
    start = 0
    for i in range(count):
        end = start + chunk_size + (1 if i < remainder else 0)
        result.append(data[start:end])
        start = end

    return result


def split_list_by_condition(
    data: List[T], condition: Callable[[T], bool]
) -> Tuple[List[T], List[T]]:
    """
    条件関数に基づいてリストを2つのグループに分割します。

    Args:
        data: 分割対象のデータリスト
        condition: 分割条件を表す関数

    Returns:
        (条件を満たす要素のリスト, 条件を満たさない要素のリスト) のタプル

    Examples:
        >>> from tascpy.utils.split import split_list_by_condition
        >>> data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        >>> split_list_by_condition(data, lambda x: x % 2 == 0)  # 偶数と奇数に分割
        ([2, 4, 6, 8, 10], [1, 3, 5, 7, 9])
    """
    satisfied = []
    not_satisfied = []

    for item in data:
        if condition(item):
            satisfied.append(item)
        else:
            not_satisfied.append(item)

    return satisfied, not_satisfied


def split_list_at_indices(
    data: List[T], indices: Union[int, List[int]]
) -> List[List[T]]:
    """
    指定されたインデックスでリストを分割します。

    Args:
        data: 分割対象のデータリスト
        indices: 分割位置を示すインデックスのリスト

    Returns:
        分割後のリストを要素とするリスト

    Examples:
        >>> from tascpy.utils.split import split_list_at_indices
        >>> data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        >>> split_list_at_indices(data, [3, 7])
        [[1, 2, 3], [4, 5, 6, 7], [8, 9, 10]]
    """
    if isinstance(indices, int):
        indices = [indices]
    sorted_indices = sorted(indices)
    result = []

    start = 0
    for index in sorted_indices:
        result.append(data[start:index])
        start = index

    result.append(data[start:])
    return result


def split_list_by_threshold(
    data: List[float], threshold: float
) -> Tuple[List[float], List[float]]:
    """
    値がしきい値を超えるかどうかに基づいてリストを分割します。

    Args:
        data: 分割対象の数値データリスト
        threshold: 分割のしきい値

    Returns:
        (threshold以上の値のリスト, threshold未満の値のリスト) のタプル

    Examples:
        >>> from tascpy.utils.split import split_list_by_threshold
        >>> data = [1.5, 3.2, 5.7, 2.9, 6.1, 4.0]
        >>> split_list_by_threshold(data, 4.0)
        ([5.7, 6.1, 4.0], [1.5, 3.2, 2.9])
    """
    return split_list_by_condition(data, lambda x: x >= threshold)


def split_list_by_integers(data: List[T], markers: List[int]) -> List[List[T]]:
    """
    整数リストの値に基づいてデータリストを分割します。マーカー値が同じ要素は同じグループに振り分けられます。

    Args:
        data: 分割対象のデータリスト
        markers: 各要素がどのグループに属するかを示す整数リスト（dataと同じ長さ）

    Returns:
        分割後のリストを要素とするリスト。各サブリストは同じマーカー値を持つ要素で構成されます。
        サブリストはマーカー値に基づいて昇順に並べられます。

    Raises:
        ValueError: データとマーカーの長さが一致しない場合

    Examples:
        >>> from tascpy.utils.split import split_list_by_integers
        >>> data = ['a', 'b', 'c', 'd', 'e', 'f']
        >>> markers = [2, 1, 2, 3, 1, 3]
        >>> split_list_by_integers(data, markers)
        [['b', 'e'], ['a', 'c'], ['d', 'f']]
    """
    if len(data) != len(markers):
        raise ValueError("データリストとマーカーリストの長さは一致する必要があります")

    # Create a dictionary to group elements by marker value
    groups = {}
    for item, marker in zip(data, markers):
        if marker not in groups:
            groups[marker] = []
        groups[marker].append(item)

    # Return the grouped elements in order of marker values
    return [groups[key] for key in sorted(groups.keys())]
