from typing import List, TypeVar, Callable, Any, Tuple

T = TypeVar('T')

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
    
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]


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


def split_list_by_condition(data: List[T], condition: Callable[[T], bool]) -> Tuple[List[T], List[T]]:
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


def split_list_at_indices(data: List[T], indices: List[int]) -> List[List[T]]:
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
    sorted_indices = sorted(indices)
    result = []
    
    start = 0
    for index in sorted_indices:
        result.append(data[start:index])
        start = index
    
    result.append(data[start:])
    return result


def split_list_by_threshold(data: List[float], threshold: float) -> Tuple[List[float], List[float]]:
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