# src/tascpy/utils/data.py
from typing import List, TypeVar, Union, Optional, Any, Tuple, Dict, Callable
import numpy as np

T = TypeVar("T")


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


    return [x for x in data if condition(x)]


def moving_average(
    data: List[float], window_size: int = 3, edge_handling="asymmetric"
) -> List[float]:
    # 入力をNumPy配列に変換 (NoneはNaNとして扱う)
    # 既に数値型のNumPy配列であればそのまま使用
    if isinstance(data, np.ndarray) and np.issubdtype(data.dtype, np.number):
        data_arr = data.astype(float)
    else:
        # data内にNoneが含まれる可能性があるため、安全に変換
        # dataがリストの場合や、オブジェクト配列の場合
        if any(x is None for x in data):
            data_arr = np.array([x if x is not None else np.nan for x in data], dtype=float)
        else:
            try:
                data_arr = np.array(data, dtype=float)
            except (ValueError, TypeError):
                 # 変換できない場合（文字列などが混入）はNaNにするかエラーにするか
                 # 元の実装に合わせてNaNにする安全策
                 data_arr = np.array([x if isinstance(x, (int, float)) and x is not None else np.nan for x in data], dtype=float)
        
    if len(data_arr) == 0:
        return []

    half_window = window_size // 2
    n = len(data_arr)
    result = np.full(n, np.nan)

    if edge_handling == "symmetric":
        # numpy.convolveを使用（mode='same'はゼロパディングまたは境界処理が簡易的）
        # symmetricの要件（端のデータ数が減る平均）を満たすために、カスタム実装が必要
        # あるいはpandasのrolling(min_periods=1, center=True)相当
        
        # NumPyでの実装:
        # カーネルを作成
        kernel = np.ones(window_size)
        
        # データの畳み込み（NaNを0として扱う）
        # ただし、単純なconvolveではNaNの伝播や、端の分母（要素数）の計算が難しい
        # 以下の手順で計算:
        # 1. 有効な値のみの配列と、有効な箇所を示すマスク(0/1)を用意
        # 2. 値の畳み込み / マスクの畳み込み = 平均
        
        valid_mask = ~np.isnan(data_arr)
        filled_data = np.where(valid_mask, data_arr, 0.0)
        
        # 分子: データの和
        # 'same'モードで中央揃え
        numerator = np.convolve(filled_data, kernel, mode='same')
        
        # 分母: 有効なデータ数
        denominator = np.convolve(valid_mask.astype(float), kernel, mode='same')
        
        # ゼロ除算回避
        with np.errstate(divide='ignore', invalid='ignore'):
            result = numerator / denominator
            
        # denominatorが0の場所はNaNにする（既に0/0=NaNだが、念のため）
        result[denominator == 0] = np.nan
        
    else:  # asymmetric
        # asymmetric: 左端は window[0:i+hw+1], 右端は window[i-hw:]
        # これは center=True だが、windowがデータをはみ出した部分をカットする挙動
        # 実は上記のsymmetricの実装（np.convolve mode='same'）は
        # データの外側を0とみなして計算している（padding）
        # 一方、分母の計算もpadding部分を除外している（valid_maskの畳み込み）
        # したがって、上記のsymmetric実装は、実質的に
        # "ウィンドウ範囲内の有効なデータの平均" を計算している。
        #
        # 元のPython実装の "symmetric" は:
        # start = max(0, i - half_window)
        # end = min(len(data), i + half_window + 1)
        # window = data[start:end]
        # -> これはまさに上記のconvolve実装と同じ（範囲内の平均）
        #
        # 元のPython実装の "asymmetric" は:
        # 左端: data[0 : i + half_window + 1] -> 右側だけ伸びる、左は0固定
        # 右端: data[i - half_window :] -> 左側だけ伸びる、右は末尾固定
        # 中央: data[i - half_window : i + half_window + 1] -> 通常
        #
        # よく見ると、asymmetricの実装は
        # left edge: window from 0 to i+hw -> center is not i?
        # i=0, hw=1 (w=3): window=0:2 (len 2). center 0. range [-1, 1] truncated to [0, 1].
        # これはsymmetricと同じロジックに見える。
        # 元のコードを確認:
        # symmetric: start=max(0, i-hw), end=min(len, i+hw+1). Slice data[start:end].
        # asymmetric:
        #   i < hw: data[0 : i+hw+1] -> start=0, end=i+hw+1. Same as symmetric (since i-hw < 0 implies max(0, ..)=0)
        #   i >= len-hw: data[i-hw:] -> start=i-hw, end=len. Same as symmetric?
        #   else: data[i-hw:i+hw+1]. Same as symmetric.
        #
        # 結論：元のコードの symmetric と asymmetric は、実は同じロジックになっている可能性がある。
        # 確認：
        # symmetric: start = max(0, 0-1) = 0. end = min(L, 0+1+1) = 2. data[0:2].
        # asymmetric (i=0 < hw=1): data[0 : 0+1+1] = data[0:2].
        # 全く同じ。
        # なので、symmetric/asymmetricの区別なく、上記のconvolve実装で良い。
        
        # 再実装（共通）
        kernel = np.ones(window_size)
        valid_mask = ~np.isnan(data_arr)
        filled_data = np.where(valid_mask, data_arr, 0.0)
        
        numerator = np.convolve(filled_data, kernel, mode='same')
        denominator = np.convolve(valid_mask.astype(float), kernel, mode='same')
        
        with np.errstate(divide='ignore', invalid='ignore'):
            result = numerator / denominator
            
        result[denominator == 0] = np.nan

    # 結果をリストに戻す（Noneを含む）
    return [None if np.isnan(x) else x for x in result]


    return [None if np.isnan(x) else x for x in result]


def detect_outliers_ratio(
    data: List[float],
    window_size: int = 3,
    threshold: float = 0.5,
    edge_handling: str = "asymmetric",
    min_abs_value: float = 1e-10,
    scale_factor: float = 1.0,
) -> List[Tuple[int, float]]:
    """
    移動平均との差分比率を用いた異常値検出。より安定した検出のため、
    データのスケールを考慮し、小さな値での誤検出を防ぎます。
    """
    if len(data) < window_size:
        raise ValueError("データ長がウィンドウサイズより小さいです")

    # NumPy配列に変換
    if isinstance(data, np.ndarray) and np.issubdtype(data.dtype, np.number):
        data_arr = data.astype(float)
    elif any(x is None for x in data):
        data_arr = np.array([x if x is not None else np.nan for x in data], dtype=float)
    else:
        data_arr = np.array(data, dtype=float)

    # データの特性を把握（NaNを除外して計算）
    valid_data = data_arr[~np.isnan(data_arr)]
    if len(valid_data) == 0:
         return []
         
    data_mean = np.mean(valid_data)
    data_std = np.std(valid_data)
    reference_value = max(data_std * scale_factor, min_abs_value)

    # 移動平均を計算（戻り値はリストなので配列に再変換）
    # 内部実装はNumPy化されているので高速
    ma_list = moving_average(
        data, window_size=window_size, edge_handling=edge_handling
    )
    # ma_listにはNoneが含まれる可能性がある
    ma_arr = np.array([x if x is not None else np.nan for x in ma_list], dtype=float)

    # ベクトル演算で異常値を検出
    # diff = abs(value - avg)
    diff = np.abs(data_arr - ma_arr)
    
    # denominator = max(abs(avg), reference_value)
    denominator = np.maximum(np.abs(ma_arr), reference_value)
    
    # ratio = diff / denominator
    with np.errstate(divide='ignore', invalid='ignore'):
        ratio = diff / denominator
    
    # 条件判定
    # ratio > threshold AND diff > min_abs_value
    # NaNの場所はFalseになるようにする
    is_outlier = (ratio > threshold) & (diff > min_abs_value)
    
    # 結果の抽出
    # np.whereでインデックスを取得
    outlier_indices = np.where(is_outlier)[0]
    outliers = []
    for idx in outlier_indices:
        outliers.append((int(idx), data[int(idx)]))

    return outliers


def diff_step(data: List[float]) -> list:
    if not data:
        raise ValueError("Input list cannot be empty")

    data_arr = np.array(data)
    if len(data_arr) == 0:
        raise ValueError("Input list cannot be empty")
        
    result = np.empty_like(data_arr)
    result[0] = data_arr[0]
    result[1:] = np.diff(data_arr)
    
    return result.tolist()


def diff_xy(x: list, y: list, method: str = "central") -> list:
    """Calculate differential coefficient from x, y coordinates.
    """
    if len(x) != len(y):
        raise ValueError("Length of x and y must be same")
    if len(x) < 2:
        raise ValueError("Data length must be at least 2 points")

    if isinstance(x, np.ndarray) and np.issubdtype(x.dtype, np.number):
        x_arr = x.astype(float)
    else:
        x_arr = np.array(x, dtype=float)
        
    if isinstance(y, np.ndarray) and np.issubdtype(y.dtype, np.number):
        y_arr = y.astype(float)
    else:
        y_arr = np.array(y, dtype=float)
    
    # Check for NaNs
    if np.any(np.isnan(x_arr)) or np.any(np.isnan(y_arr)):
        # 元の実装（Noneを含む場合はNoneを返す、あるいはmathの場合）に合わせるなら
        # math.py側でNoneフィルタリングをしているので、ここではNaNが含まれない前提か、
        # あるいはNaNを含む場合は結果もNaNにするか。
        # NumPyのgradientはNaNを含むとNaN伝播する。
        pass

    if method == "central":
        # numpy.gradientを使用
        # np.gradient(y, x) は内部点では中心差分、境界では片側差分を使用する
        # これは元の実装の挙動と一致する
        try:
             result = np.gradient(y_arr, x_arr)
        except Exception:
            # 重複するX座標などでゼロ除算が発生する場合のフォールバックなどが必要かも
            # しかし元の実装もゼロ除算チェックはしていない
             result = np.gradient(y_arr, x_arr)
             
    elif method == "forward":
        # Forward difference: (y[i+1] - y[i]) / (x[i+1] - x[i])
        dx = np.diff(x_arr)
        dy = np.diff(y_arr)
        # 0除算対策（念のため）
        with np.errstate(divide='ignore', invalid='ignore'):
            d = dy / dx
            
        # サイズを合わせるため、最後の要素を繰り返す
        result = np.append(d, d[-1])
        
    elif method == "backward":
        # Backward difference: (y[i] - y[i-1]) / (x[i] - x[i-1])
        dx = np.diff(x_arr)
        dy = np.diff(y_arr)
        with np.errstate(divide='ignore', invalid='ignore'):
            d = dy / dx
            
        # サイズを合わせるため、最初の要素を繰り返す（前方に挿入）
        result = np.insert(d, 0, d[0])
        
    else:
        raise ValueError("Invalid method. Use 'central', 'forward', or 'backward'")

    return result.tolist()


def integrate_xy(x: list, y: list, initial_value: float = 0.0) -> list:
    """Calculate integral of y with respect to x using trapezoidal rule.
    """
    if len(x) != len(y):
        raise ValueError("Length of x and y must be same")
    if len(x) < 2:
        raise ValueError("Data length must be at least 2 points")

    if isinstance(x, np.ndarray) and np.issubdtype(x.dtype, np.number):
        x_arr = x.astype(float)
    else:
        x_arr = np.array(x, dtype=float)
        
    if isinstance(y, np.ndarray) and np.issubdtype(y.dtype, np.number):
        y_arr = y.astype(float)
    else:
        y_arr = np.array(y, dtype=float)

    # Check for NaNs (equivalent to None check in original)
    if np.any(np.isnan(y_arr)):
        # None値を含む場合、最初の値だけ計算し、残りはNoneとする仕様を再現
        result = np.full(len(x), np.nan) # 元はNoneだが、float配列ならNaN
        
        if not np.isnan(y_arr[0]) and not np.isnan(x_arr[0]):
             dx = x_arr[0] - 0
             first_step = dx * y_arr[0]
             result[0] = initial_value + first_step
             
        # リストに戻すときにNaNをNoneにする
        return [None if np.isnan(v) else v for v in result]

    # dx calculation
    # NOTE: Original implementation uses dx = x[0] - 0 for the first point
    # This implies the integration starts from 0 to x[0] assuming constant y[0]
    
    # 1. First step integration (0 to x[0])
    dx0 = x_arr[0]
    first_term = dx0 * y_arr[0]
    val0 = initial_value + first_term
    
    # 2. Subsequent steps using trapezoidal rule
    # dx[i] = x[i] - x[i-1] for i > 0
    dx_rest = np.diff(x_arr)
    
    # dy_avg[i] = (y[i] + y[i-1]) / 2
    # y[1:] + y[:-1]
    y_sum = y_arr[1:] + y_arr[:-1]
    dy_avg = y_sum / 2.0
    
    # areas
    areas = dx_rest * dy_avg
    
    # cumulative sum
    cum_areas = np.cumsum(areas)
    
    # Result construction
    result = np.zeros(len(x))
    result[0] = val0
    result[1:] = val0 + cum_areas
    
    return result.tolist()
