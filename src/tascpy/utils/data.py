# src/tascpy/utils/data.py
from typing import List, TypeVar, Union, Optional, Any, Tuple, Dict, Callable

T = TypeVar('T')
    
def filter_none_values(data: List[Optional[T]]) -> List[T]:
    """
    リストから None 値をフィルタリングします。
    
    データ処理時に None 値を除外する場合に有用です。計測データや
    結果の整形時にギャップを除外するのに使用できます。
    
    Args:
        data: None を含む可能性のあるデータリスト
    
    Returns:
        None 値を除外したリスト
    
    Examples:
        >>> from tascpy.utils.data import filter_none_values
        >>> data = [1, None, 3, None, 5]
        >>> filter_none_values(data)
        [1, 3, 5]
        
        Channel クラスでの使用例:
        
        >>> from tascpy.utils.data import filter_none_values
        >>> def removed_data(self):
        ...     return filter_none_values(self.data)
        
        インデックスと値のペアを保持する場合:
        
        >>> data = [10, None, 30, None, 50]
        >>> indices = [0, 1, 2, 3, 4]
        >>> valid_indices = [i for i, x in enumerate(data) if x is not None]
        >>> valid_data = filter_none_values(data)
        >>> list(zip(valid_indices, valid_data))
        [(0, 10), (2, 30), (4, 50)]
    """
    return [x for x in data if x is not None]


def filter_with_indices(data: List[Optional[T]]) -> Tuple[List[T], List[int]]:
    """
    リストから None 値をフィルタリングし、有効な値とそのインデックスを返します。
    
    Args:
        data: None を含む可能性のあるデータリスト
    
    Returns:
        有効な値のリストとそれらのインデックスのタプル
        
    Examples:
        >>> from tascpy.utils.data import filter_with_indices
        >>> data = [1, None, 3, None, 5]
        >>> values, indices = filter_with_indices(data)
        >>> values
        [1, 3, 5]
        >>> indices
        [0, 2, 4]
    """
    valid_values = []
    indices = []
    for i, value in enumerate(data):
        if value is not None:
            valid_values.append(value)
            indices.append(i)
    return valid_values, indices


def filter_by_condition(data: List[T], condition: Callable[[T], bool]) -> List[T]:
    """
    指定された条件に基づいてデータをフィルタリングします。
    
    Args:
        data: フィルタリング対象のデータリスト
        condition: フィルタリング条件を表す関数
        
    Returns:
        条件を満たす要素のみを含むリスト
        
    Examples:
        >>> from tascpy.utils.data import filter_by_condition
        >>> data = [1, 2, 3, 4, 5]
        >>> filter_by_condition(data, lambda x: x > 3)
        [4, 5]
        
        >>> # 正の値のみをフィルタリング
        >>> mixed_data = [-2, 0, 3, -1, 5]
        >>> filter_by_condition(mixed_data, lambda x: x > 0)
        [3, 5]
    """
    return [x for x in data if condition(x)]


def replace_none_values(data: List[Optional[T]], replacement: T) -> List[T]:
    """
    None 値を指定された値に置換します。
    
    Args:
        data: None を含む可能性のあるデータリスト
        replacement: None の代わりに使用する値
        
    Returns:
        None 値が置換された新しいリスト
        
    Examples:
        >>> from tascpy.utils.data import replace_none_values
        >>> data = [1, None, 3, None, 5]
        >>> replace_none_values(data, 0)
        [1, 0, 3, 0, 5]
    """
    return [x if x is not None else replacement for x in data]


def remove_consecutive_duplicates(data: List[T]) -> List[T]:
    """
    連続する重複データを削除し、各値の最初の出現のみを残します。
    
    連続するデータポイントが同じ値を持つ場合に、その重複を1つだけ残します。
    データ圧縮や、一定値が連続するセグメントの処理に有用です。
    
    Args:
        data: 処理対象のデータリスト
    
    Returns:
        連続する重複が削除されたリスト
    
    Examples:
        >>> from tascpy.utils.data import remove_consecutive_duplicates
        >>> data = [1, 1, 2, 2, 2, 3, 4, 4, 1]
        >>> remove_consecutive_duplicates(data)
        [1, 2, 3, 4, 1]
        
        >>> # None値を含むデータの処理
        >>> data = [1, None, None, 2, 2, None, 3]
        >>> remove_consecutive_duplicates(data)
        [1, None, 2, None, 3]
        
        >>> # 空リストの処理
        >>> remove_consecutive_duplicates([])
        []
        
        >>> # 浮動小数点数の処理
        >>> data = [1.0, 1.0, 2.5, 2.5, 2.5, 3.0]
        >>> remove_consecutive_duplicates(data)
        [1.0, 2.5, 3.0]
    """
    if not data:
        return []
    
    result = [data[0]]
    
    for i in range(1, len(data)):
        if data[i] != data[i-1]:
            result.append(data[i])
    
    return result


def find_extrema(data: List[Union[float, int]], find_max: bool = True) -> Tuple[Union[float, int], int]:
    """
    リスト内の最大値または最小値とそのインデックスを見つけます。
    
    Args:
        data: 数値のリスト
        find_max: True の場合は最大値、False の場合は最小値を探索
        
    Returns:
        (最大値または最小値, そのインデックス) のタプル
        
    Raises:
        ValueError: リストが空の場合
        
    Examples:
        >>> from tascpy.utils.data import find_extrema
        >>> data = [5, 3, 9, 1, 7]
        >>> find_extrema(data)  # 最大値を検索
        (9, 2)
        >>> find_extrema(data, find_max=False)  # 最小値を検索
        (1, 3)
    """
    if not data:
        raise ValueError("データリストが空です")
    
    filtered_data = filter_none_values(data)
    if not filtered_data:
        raise ValueError("有効なデータが存在しません")
    
    if find_max:
        extrema = max(filtered_data)
    else:
        extrema = min(filtered_data)
    
    return extrema, data.index(extrema)


def interpolate_missing_data(data: List[Optional[float]], method: str = 'linear') -> List[float]:
    """
    欠損値(None)を含むデータリストの補間を行います。
    
    Args:
        data: 欠損値(None)を含むデータリスト
        method: 補間方法。'linear'(線形補間), 'nearest'(最近傍補間), 
                'zero'(ゼロ次補間)のいずれかを指定。デフォルトは'linear'
    
    Returns:
        補間されたデータリスト
    
    Raises:
        ValueError: 無効な補間方法が指定された場合や、
                   全ての値がNoneの場合
    
    Examples:
        >>> from tascpy.utils.data import interpolate_missing_data
        >>> data = [1.0, None, 3.0, None, 5.0]
        >>> interpolate_missing_data(data)
        [1.0, 2.0, 3.0, 4.0, 5.0]
        
        >>> # 異なる補間方法を使用する例
        >>> data = [1.0, None, None, 4.0]
        >>> interpolate_missing_data(data, method='nearest')
        [1.0, 1.0, 1.0, 4.0]
        
        >>> # ゼロ次補間の例
        >>> data = [1.0, None, None, 4.0]
        >>> interpolate_missing_data(data, method='zero')
        [1.0, 1.0, 1.0, 4.0]
        
        >>> # 先頭や末尾のNoneも補間
        >>> data = [None, 2.0, None, 4.0, None]
        >>> interpolate_missing_data(data)
        [2.0, 2.0, 3.0, 4.0, 4.0]
    """
    import numpy as np
    
    # 有効なインデックスと値を抽出
    valid_indices = []
    valid_values = []
    for i, value in enumerate(data):
        if value is not None:
            valid_indices.append(i)
            valid_values.append(value)
    
    # 全てNoneの場合はエラー
    if not valid_indices:
        raise ValueError("全ての値がNoneです。補間するデータがありません。")
    
    # データが1つしかない場合、全てその値で埋める
    if len(valid_indices) == 1:
        return [valid_values[0]] * len(data)
    
    # 有効なメソッドかチェック
    valid_methods = ['linear', 'nearest', 'zero']
    if method not in valid_methods:
        raise ValueError(f"無効な補間方法です。次のいずれかを指定してください: {', '.join(valid_methods)}")
    
    # 全インデックスの配列を作成
    all_indices = np.arange(len(data))
    
    # 結果の初期化
    result = np.zeros(len(data))
    
    # 補間を実行
    if method == 'linear':
        # np.interpを使用した線形補間
        result = np.interp(
            all_indices, 
            valid_indices, 
            valid_values,
            left=valid_values[0],    # 範囲外左側の値
            right=valid_values[-1]   # 範囲外右側の値
        )
    elif method == 'nearest':
        # 最近傍補間（NumPy実装）
        for i in range(len(data)):
            if i in valid_indices:
                # 有効な値はそのまま使用
                result[i] = data[i]
            else:
                # 最も近い有効な値を見つける
                distances = np.abs(np.array(valid_indices) - i)
                nearest_idx = np.argmin(distances)
                result[i] = valid_values[nearest_idx]
    elif method == 'zero':
        # ゼロ次補間（ステップ関数）
        # 各点に対して、それより前にある最も近い有効な値を使用
        for i in range(len(data)):
            if i in valid_indices:
                result[i] = data[i]
            else:
                # iより小さい有効なインデックスの中で最大のものを探す
                valid_before = [idx for idx in valid_indices if idx < i]
                if valid_before:  # 前に有効な値がある
                    idx = max(valid_before)
                    result[i] = data[idx]
                else:  # 前に有効な値がない場合は次の有効な値を使う
                    valid_after = [idx for idx in valid_indices if idx > i]
                    if valid_after:
                        idx = min(valid_after)
                        result[i] = data[idx]
    
    # リストに変換して返す
    return result.tolist()


def resample_data(data: List[float], original_steps: List[int], new_steps: List[int]) -> List[float]:
    """
    データを新しいステップでリサンプリングします。線形補間を使用して値を計算します。
    
    Args:
        data: 元のデータ値のリスト
        original_steps: 元データに対応するステップ値のリスト
        new_steps: リサンプリングしたい新しいステップ値のリスト
    
    Returns:
        新しいステップに対応するリサンプリングされたデータのリスト
    
    Raises:
        ValueError: データとステップの長さが一致しない場合、またはステップが昇順でない場合
        
    Examples:
        >>> from tascpy.utils.data import resample_data
        >>> # 等間隔データを高密度化する例
        >>> data = [10, 20, 30, 40]
        >>> original_steps = [1, 2, 3, 4]
        >>> new_steps = [1, 1.5, 2, 2.5, 3, 3.5, 4]
        >>> resample_data(data, original_steps, new_steps)
        [10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0]
        
        >>> # 不規則間隔のデータを等間隔化する例
        >>> data = [5, 8, 15, 25]
        >>> original_steps = [1, 3, 7, 12]
        >>> new_steps = [2, 4, 6, 8, 10]
        >>> resample_data(data, original_steps, new_steps)
        [6.5, 10.0, 13.5, 17.5, 21.5]
        
        >>> # ダウンサンプリングの例
        >>> data = [10, 15, 20, 25, 30, 35, 40]
        >>> original_steps = [1, 2, 3, 4, 5, 6, 7]
        >>> new_steps = [1, 3, 5, 7]
        >>> resample_data(data, original_steps, new_steps)
        [10.0, 20.0, 30.0, 40.0]
        
        >>> # 測定範囲外の推定
        >>> data = [10, 20, 30, 40]
        >>> original_steps = [2, 4, 6, 8]
        >>> new_steps = [1, 3, 5, 7, 9]
        >>> resample_data(data, original_steps, new_steps)
        [5.0, 15.0, 25.0, 35.0, 45.0]
        
        >>> # Channel クラスでの使用例
        >>> # あるチャンネルのデータを別のチャンネルのステップに合わせる
        >>> ch1_data = [10, 15, 20, 25]
        >>> ch1_steps = [1, 2, 3, 4]
        >>> ch2_steps = [0.5, 1.5, 2.5, 3.5, 4.5]
        >>> resampled_ch1 = resample_data(ch1_data, ch1_steps, ch2_steps)
        >>> resampled_ch1
        [7.5, 12.5, 17.5, 22.5, 27.5]
    """
    import numpy as np
    
    # 入力検証
    if len(data) != len(original_steps):
        raise ValueError("データとステップの長さが一致しません。")
    
    if len(data) == 0:
        return []
    
    # ステップが昇順であることを確認
    if not all(original_steps[i] <= original_steps[i+1] for i in range(len(original_steps)-1)):
        raise ValueError("元のステップは昇順である必要があります。")
    
    if not all(new_steps[i] <= new_steps[i+1] for i in range(len(new_steps)-1)):
        raise ValueError("新しいステップは昇順である必要があります。")
    
    # データにNoneが含まれる場合は処理
    valid_data = []
    valid_steps = []
    for i, value in enumerate(data):
        if value is not None:
            valid_data.append(value)
            valid_steps.append(original_steps[i])
    
    if not valid_data:
        raise ValueError("有効なデータ点がありません。")
    
    # NumPyのinterp関数を使用して線形補間
    resampled_data = np.interp(
        new_steps,
        valid_steps,
        valid_data,
        left=None,  # 範囲外の値を指定しなければ、左端は最初の値で外挿
        right=None  # 右端は最後の値で外挿
    )
    
    return resampled_data.tolist()


def smooth_data(data: List[float], window_size: int = 3) -> List[float]:
    """
    移動平均によるデータのスムージングを行います。
    
    指定されたウィンドウサイズで各データポイントの周囲を平均化し、
    ノイズを軽減してデータの傾向をより明確にします。
    
    Args:
        data: スムージング対象のデータリスト
        window_size: スムージングウィンドウのサイズ（デフォルト: 3）
    
    Returns:
        スムージングされたデータのリスト
    
    Raises:
        ValueError: 無効なパラメータが指定された場合
        
    Examples:
        >>> from tascpy.utils.data import smooth_data
        >>> data = [1, 3, 2, 5, 8, 7, 10]
        >>> smooth_data(data, window_size=3)
        [1.0, 2.0, 3.33, 5.0, 6.67, 8.33, 10.0]
        
        >>> # より大きいウィンドウを使用した例
        >>> smooth_data(data, window_size=5)
        [1.0, 2.0, 3.8, 5.0, 6.4, 7.0, 10.0]
        
        >>> # None値を含むデータの処理
        >>> data_with_none = [1, None, 3, 4, None, 6]
        >>> smooth_data(data_with_none, window_size=3)
        [1.0, 2.0, 2.67, 3.5, 4.33, 6.0]
    """
    if not data:
        return []
        
    if window_size < 1:
        raise ValueError("ウィンドウサイズは1以上である必要があります")
        
    if window_size > len(data):
        raise ValueError("ウィンドウサイズがデータ長より大きくなっています")
    
    # Noneの値を処理
    valid_data = []
    for x in data:
        if x is not None:
            valid_data.append(x)
        else:
            # None値の補間（前後の有効な値の平均）
            if valid_data:  # 前に有効な値がある場合
                if len(valid_data) > 0:
                    valid_data.append(valid_data[-1])  # 最後の有効な値を使用
                else:
                    valid_data.append(0)  # デフォルト値
            else:
                # 先頭がNoneの場合、後で修正する
                valid_data.append(None)
    
    # 先頭のNoneを最初の有効な値で置換
    for i in range(len(valid_data)):
        if valid_data[i] is not None:
            first_valid = valid_data[i]
            break
    else:
        return [0] * len(data)  # すべてNoneの場合
        
    for i in range(len(valid_data)):
        if valid_data[i] is None:
            valid_data[i] = first_valid
    
    result = []
    half_window = window_size // 2
    
    # 移動平均を計算
    for i in range(len(data)):
        # 平均を計算する範囲を決定
        start = max(0, i - half_window)
        end = min(len(valid_data), i + half_window + 1)
        
        # 現在の範囲のデータを収集
        window_data = valid_data[start:end]
        
        # 平均値を計算
        window_avg = sum(window_data) / len(window_data)
        result.append(round(window_avg, 2))
    
    return result


def diff_step(data: List[float]) -> list:
    if not data:
        raise ValueError("Input list cannot be empty")
        
    result = [data[0]]  # First value is the initial y value
    
    # Calculate differences between consecutive steps
    for i in range(1, len(data)):
        diff = data[i] - data[i-1]
        result.append(diff)
    
    return result


def diff_xy(x: list, y: list, method: str = 'central') -> list:
    """Calculate differential coefficient from x, y coordinates.
    
    Args:
        x (list): x coordinates
        y (list): y coordinates 
        method (str): Differentiation method ('central', 'forward', or 'backward')
        
    Returns:
        list: Differential coefficients
    """
    if len(x) != len(y):
        raise ValueError("Length of x and y must be same")
    if len(x) < 2:
        raise ValueError("Data length must be at least 2 points")
        
    result = []
    n = len(x)
    
    if method == 'central':
        # Forward difference for first point
        result.append((y[1] - y[0]) / (x[1] - x[0]))
        
        # Central difference for middle points
        for i in range(1, n-1):
            result.append((y[i+1] - y[i-1]) / (x[i+1] - x[i-1]))
            
        # Backward difference for last point
        result.append((y[-1] - y[-2]) / (x[-1] - x[-2]))
        
    elif method == 'forward':
        # Forward difference for all points except last
        for i in range(n-1):
            result.append((y[i+1] - y[i]) / (x[i+1] - x[i]))
        # Repeat last coefficient for last point    
        result.append(result[-1])
        
    elif method == 'backward':
        # Repeat first coefficient for first point
        result.append((y[1] - y[0]) / (x[1] - x[0]))
        # Backward difference for remaining points
        for i in range(1, n):
            result.append((y[i] - y[i-1]) / (x[i] - x[i-1]))
            
    else:
        raise ValueError("Invalid method. Use 'central', 'forward', or 'backward'")
        
    return result


def integrate_xy(x: list, y: list, initial_value: float = 0.0) -> list:
    """Calculate integral of y with respect to x using trapezoidal rule.
    
    Args:
        x (list): x coordinates
        y (list): y coordinates
        initial_value (float): Initial value of integral (default = 0.0)
        
    Returns:
        list: Integral values at each x point
        
    Raises:
        ValueError: If input lists have different lengths or too short
    """
    if len(x) != len(y):
        raise ValueError("Length of x and y must be same")
    if len(x) < 2:
        raise ValueError("Data length must be at least 2 points")
    
    result = [initial_value]  # Start with initial value
    integral = initial_value
    
    # Trapezoidal rule integration
    for i in range(1, len(x)):
        dx = x[i] - x[i-1]
        dy_avg = (y[i] + y[i-1]) / 2
        integral += dx * dy_avg
        result.append(integral)
    
    return result
