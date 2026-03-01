"""座標ドメインの補間用純粋関数群"""

from typing import Dict, Any, Optional, List
import numpy as np

def inverse_distance_weighting(
    point_data: Dict[str, Any], x: float, y: float, z: Optional[float], power: float
) -> float:
    """逆距離加重法による補間を行います
    
    Args:
        point_data: 点のデータ（point, value, col_name）
        x, y, z: 補間する座標位置
        power: 重み付けパワー
        
    Returns:
        float: 補間値
    """
    px = point_data["point"]["x"]
    py = point_data["point"]["y"]
    pz = point_data["point"]["z"]
    value = point_data["value"]

    if z is not None and pz is not None:
        distance = float(np.sqrt((x - px) ** 2 + (y - py) ** 2 + (z - pz) ** 2))
    else:
        distance = float(np.sqrt((x - px) ** 2 + (y - py) ** 2))

    if distance < 1e-10:
        return float(value)

    weight = 1.0 / (distance**power)
    return float(value * weight)


def nearest_neighbor(
    point_data: Dict[str, Any], x: float, y: float, z: Optional[float], power: float
) -> float:
    """最近傍法による補間を行います
    
    Args:
        point_data: 点のデータ
        x, y, z: 補間する座標位置
        power: 使用しないパラメータ
        
    Returns:
        float: 補間値
    """
    return float(point_data["value"])


def linear_interpolation(
    point_data: Dict[str, Any], x: float, y: float, z: Optional[float], power: float
) -> float:
    """線形補間（逆距離加重法 power=1.0）
    
    Args:
        point_data: 点のデータ
        x, y, z: 補間する座標位置
        power: 使用しないパラメータ
        
    Returns:
        float: 補間値
    """
    return inverse_distance_weighting(point_data, x, y, z, 1.0)

def compute_point_interpolation_values(
    source_data: List[Dict[str, Any]],
    x: float,
    y: float,
    z: Optional[float],
    method: str,
    power: float
) -> List[float]:
    """複数のソースデータに対して指定座標での補間値を一括計算します
    
    Args:
        source_data: 点のデータリスト（point, value, col_name等を含む）
        x, y, z: 補間する座標位置
        method: 補間方法 ("inverse_distance", "nearest", "linear")
        power: 重み付けパワー
        
    Returns:
        List[float]: 各ソースに対する補間値のリスト
    """
    if method == "inverse_distance":
        interp_func = inverse_distance_weighting
    elif method == "nearest":
        interp_func = nearest_neighbor
    elif method == "linear":
        interp_func = linear_interpolation
    else:
        raise ValueError(f"サポートされていない補間方法: {method}")

    return [interp_func(p, x, y, z, power) for p in source_data]

def compute_grid_interpolation_values(
    source_point: Dict[str, Any],
    x_grid: np.ndarray,
    y_grid: np.ndarray,
    method: str,
    power: float
) -> np.ndarray:
    """指定されたグリッド上での補間値を計算します
    
    Args:
        source_point: 基点となる1つのデータ
        x_grid: X座標のグリッド配列 (1次元)
        y_grid: Y座標のグリッド配列 (1次元)
        method: 補間方法
        power: 重み付けパワー
        
    Returns:
        np.ndarray: 2次元の補間値グリッド (ny, nx)
    """
    if method == "inverse_distance":
        interp_func = inverse_distance_weighting
    elif method == "nearest":
        interp_func = nearest_neighbor
    else:
        interp_func = linear_interpolation

    ny = len(y_grid)
    nx = len(x_grid)
    grid_values = np.zeros((ny, nx))
    
    for i, y in enumerate(y_grid):
        for j, x in enumerate(x_grid):
            grid_values[i, j] = interp_func(source_point, x, y, None, power)
            
    return grid_values

def compute_spatial_interpolation_values(
    source_data: List[Dict[str, Any]],
    target_coords: List[Dict[str, Any]],
    is_3d: bool,
    method: str,
    power: float
) -> List[float]:
    """複数のソースからの補間値の平均を各ターゲット位置について計算します
    
    Args:
        source_data: 補間元となる点データのリスト
        target_coords: 補間先となる座標情報のリスト [{'x':..., 'y':..., 'z':...}]
        is_3d: 3D補間かどうか
        method: 補間方法
        power: 重み付けパワー
        
    Returns:
        List[float]: ターゲットごとの平均補間値
    """
    if method == "inverse_distance":
        interp_func = inverse_distance_weighting
    elif method == "nearest":
        interp_func = nearest_neighbor
    else:
        interp_func = linear_interpolation

    results = []
    for tgt in target_coords:
        tx = tgt.get("x")
        ty = tgt.get("y")
        tz = tgt.get("z") if is_3d else None
        
        interp_values = []
        for src in source_data:
            val = interp_func(src, tx, ty, tz, power)
            interp_values.append(val)
            
        if interp_values:
            results.append(float(np.nanmean(interp_values)))
        else:
            results.append(float(np.nan))
            
    return results

