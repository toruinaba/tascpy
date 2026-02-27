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
