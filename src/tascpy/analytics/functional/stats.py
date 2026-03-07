from typing import Union, Optional, List, Any, Tuple
import numpy as np

# --- Transformations ---

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

def detect_outliers(
    vals: Union[np.ndarray, List[float]],
    window_size: int = 3,
    threshold: float = 0.5,
    edge_handling: str = "asymmetric",
    min_abs_value: float = 1e-10,
    scale_factor: float = 1.0,
) -> List[int]:
    """移動平均を使用して外れ値を検出します。

    移動平均からの偏差率が閾値を超える場合を外れ値とみなします。

    Args:
        vals (Union[np.ndarray, List[float]]): 入力値の配列またはリスト。
        window_size (int, optional): 移動平均のウィンドウサイズ。デフォルトは 3。
        threshold (float, optional): 外れ値判定の閾値（偏差率）。デフォルトは 0.5。
        edge_handling (str, optional): 境界処理の方法。デフォルトは "asymmetric"。
        min_abs_value (float, optional): 最小絶対値（ゼロ除算防止）。デフォルトは 1e-10。
        scale_factor (float, optional): 基準値（標準偏差等）のスケーリング係数。デフォルトは 1.0。

    Returns:
        List[int]: 外れ値フラグのリスト（0: 正常, 1: 外れ値）。

    Raises:
        ValueError: 無効な引数、または有効なデータが存在しない場合。
    """
    if edge_handling not in ["symmetric", "asymmetric"]:
        raise ValueError(f"無効なエッジ処理方法です: {edge_handling}")

    if window_size < 1:
        raise ValueError("ウィンドウサイズは1以上である必要があります")

    if len(vals) < window_size:
        raise ValueError("データ長がウィンドウサイズより小さいです")

    # Helper to clean data
    data = vals
    if isinstance(data, np.ndarray) and np.issubdtype(data.dtype, np.number):
        valid_arr = data[~np.isnan(data)]
    else:
        valid_arr = np.array([x for x in data if x is not None and (not isinstance(x, float) or not np.isnan(x))], dtype=float)

    if len(valid_arr) == 0:
        raise ValueError(f"有効なデータがありません")

    data_std = np.std(valid_arr)
    # Use max from python defaults or numpy? Logic used builtins.max
    reference_value = float(max(data_std * scale_factor, min_abs_value))

    ma_values = moving_average(
        data, window_size=window_size, edge_handling=edge_handling
    )
    
    # Convert to float array (handling None/NaN)
    if isinstance(data, np.ndarray) and np.issubdtype(data.dtype, np.number):
        data_arr = data.astype(float)
    else:
        data_arr = np.array([x if x is not None else np.nan for x in data], dtype=float)
        
    if isinstance(ma_values, np.ndarray) and np.issubdtype(ma_values.dtype, np. number):
        ma_arr = ma_values.astype(float)
    else:
        ma_arr = np.array([x if x is not None else np.nan for x in ma_values], dtype=float)

    diff = np.abs(data_arr - ma_arr)
    denominator = np.maximum(np.abs(ma_arr), reference_value)
    
    with np.errstate(divide='ignore', invalid='ignore'):
        ratio = diff / denominator
        
    is_outlier = (ratio > threshold) & (diff > min_abs_value)
    
    # Return as list of 0/1 flags
    outlier_flags = np.where(is_outlier, 1, 0).tolist()

    return outlier_flags

def gaussian_filter(
    vals: Union[np.ndarray, List[float]],
    sigma: float = 1.0,
    window_size: Optional[int] = None,
) -> Any:
    """ガウシアンフィルタを適用して平滑化を行います。

    欠損値は無視して畳み込み計算を行います。

    Args:
        vals (Union[np.ndarray, List[float]]): 入力値の配列またはリスト。
        sigma (float, optional): ガウス分布の標準偏差。デフォルトは 1.0。
        window_size (Optional[int], optional): フィルタのウィンドウサイズ。指定しない場合は sigma から自動計算されます。

    Returns:
        Any: 平滑化後の配列（NumPy配列）。

    Raises:
        ValueError: ウィンドウサイズが1未満の場合。
        
    Examples:
        >>> from tascpy.analytics.functional.stats import gaussian_filter
        >>> import numpy as np
        >>> arr = np.array([0, 10, 0, 0, 0])
        >>> smoothed = gaussian_filter(arr, sigma=1.0)
    """
    if window_size is None:
        radius = int(4.0 * sigma + 0.5)
        window_size = 2 * radius + 1
    
    if window_size < 1:
        raise ValueError("ウィンドウサイズは1以上である必要があります")

    data = vals
    if isinstance(data, np.ndarray) and np.issubdtype(data.dtype, np.number):
        data_arr = data.astype(float)
    else:
        data_arr = np.array([x if x is not None else np.nan for x in data], dtype=float)

    radius = window_size // 2
    x = np.arange(-radius, radius + 1)
    kernel = np.exp(-(x**2) / (2 * sigma**2))
    kernel = kernel / np.sum(kernel)

    valid_mask = ~np.isnan(data_arr)
    filled_data = np.where(valid_mask, data_arr, 0.0)
    
    numerator = np.convolve(filled_data, kernel, mode='same')
    denominator = np.convolve(valid_mask.astype(float), kernel, mode='same')
    
    with np.errstate(divide='ignore', invalid='ignore'):
        smoothed = numerator / denominator
    
    smoothed[denominator == 0] = np.nan
    
    return smoothed


