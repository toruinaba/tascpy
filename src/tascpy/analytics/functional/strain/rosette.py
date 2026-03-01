"""ひずみドメインのロゼット計算用純粋関数群"""

from typing import Tuple
import numpy as np

def compute_rosette_strains(
    e1: np.ndarray,
    e2: np.ndarray,
    e3: np.ndarray,
    r_type: str = "rectangular",
    angle_offset: float = 0.0
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """ロゼットひずみゲージの値から主ひずみを計算します。
    
    Args:
        e1: 第1ゲージのひずみ配列
        e2: 第2ゲージのひずみ配列
        e3: 第3ゲージのひずみ配列
        r_type: ロゼットタイプ ('rectangular' or 'delta')
        angle_offset: 第1ゲージの設置角度（度）
        
    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]: 
            (最大主ひずみ, 最小主ひずみ, 最大せん断ひずみ, 主ひずみ方向角度)
    """
    if r_type.lower() == "rectangular":
        ex = e1
        ey = e3
        gamma_xy = 2 * e2 - (e1 + e3)
    elif r_type.lower() == "delta":
        ex = e1
        ey = (2 * e2 + 2 * e3 - e1) / 3.0
        gamma_xy = (2.0 / np.sqrt(3.0)) * (e2 - e3)
    else:
        raise ValueError(f"Unknown rosette type: {r_type}. Supported: 'rectangular', 'delta'")

    center = (ex + ey) / 2.0
    radius = np.sqrt(((ex - ey) / 2.0) ** 2 + (gamma_xy / 2.0) ** 2)
    
    e_max = center + radius
    e_min = center - radius
    gamma_max = 2 * radius
    
    theta_rad = 0.5 * np.arctan2(gamma_xy, ex - ey)
    theta_deg = np.degrees(theta_rad)
    final_theta = theta_deg + angle_offset
    
    return e_max, e_min, gamma_max, final_theta

def compute_rosette_vectors(
    val_e1: float,
    val_e2: float,
    val_theta: float,
    scale: float = 1.0
) -> Tuple[float, float, float, float]:
    """主ひずみと角度から、スケーリングされたベクトルのXY成分を計算します。
    
    Args:
        val_e1: 最大主ひずみ
        val_e2: 最小主ひずみ
        val_theta: 主ひずみ方向の角度（度）
        scale: ベクトルのスケーリング係数

    Returns:
        Tuple[float, float, float, float]: (v1_x, v1_y, v2_x, v2_y)
    """
    theta_rad = np.radians(val_theta)
    
    # 主ひずみ1 (最大) のベクトル成分
    v1_x = val_e1 * np.cos(theta_rad) * scale
    v1_y = val_e1 * np.sin(theta_rad) * scale
    
    # 主ひずみ2 (最小) のベクトル成分 (theta + 90deg)
    v2_x = val_e2 * np.cos(theta_rad + np.pi/2) * scale
    v2_y = val_e2 * np.sin(theta_rad + np.pi/2) * scale

    return v1_x, v1_y, v2_x, v2_y

