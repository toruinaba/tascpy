"""座標ドメインの補間用純粋関数群"""

from typing import Dict, Any, Optional
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
