from typing import Optional, List, Any, Dict, Union, Tuple
import numpy as np
from ...operations.registry import operation
from ...domains.strain import StrainCollection
from ...core.column import Column
from ...core.result import ScalarResult, PointResult
from ...operations.validation import requires_column

@operation(domain="strain")
def calculate_stress(
    collection: StrainCollection,
    load_column: str,
    area: float,
    result_column: str = "stress",
    unit: str = "MPa"
) -> StrainCollection:
    """応力を計算する (Stress = Load / Area)

    Args:
        collection: ひずみコレクション
        load_column: 荷重データのカラム名
        area: 断面積
        result_column: 結果を格納するカラム名
        unit: 結果の単位

    Returns:
        StrainCollection: 応力カラムが追加されたコレクション
    """
    if load_column not in collection.columns:
        raise ValueError(f"荷重カラム '{load_column}' が見つかりません")
        
    load_vals = np.array(collection[load_column].values, dtype=float)
    
    # 応力計算
    stress_vals = load_vals / area
    
    result = collection.clone()
    result.columns[result_column] = Column(
        ch=None,
        name=result_column,
        values=stress_vals,
        unit=unit,
        metadata={
            "description": f"Calculated Stress (Load: {load_column}, Area: {area})", 
            "source_load": load_column,
            "area": area
        }
    )
    
    return result

@operation(domain="strain")
def analyze_material_properties(
    collection: StrainCollection,
    stress_column: str,
    strain_column: str,
    lateral_strain_column: Optional[str] = None,
    elastic_range: Tuple[float, float] = (0.0005, 0.0025), # Strain range for Young's Modulus
    offset: float = 0.002, # 0.2% offset
    result_prefix: str = "material"
) -> StrainCollection:
    """材料特性（ヤング率、降伏点、ポアソン比）を解析する

    Args:
        collection: ひずみコレクション
        stress_column: 応力カラム名
        strain_column: ひずみ（縦）カラム名
        lateral_strain_column: 横ひずみカラム名（ポアソン比計算用、任意）
        elastic_range: ヤング率計算に使用するひずみ範囲 (start, end)
        offset: 耐力計算用のオフセットひずみ量 (デフォルト 0.002 = 0.2%)
        result_prefix: 結果名の接頭辞

    Returns:
        StrainCollection: 計算結果（ScalarResult, PointResult）が追加されたコレクション
    """
    if stress_column not in collection.columns:
        raise ValueError(f"応力カラム '{stress_column}' が見つかりません")
    if strain_column not in collection.columns:
        raise ValueError(f"ひずみカラム '{strain_column}' が見つかりません")

    # データ取得 (NaN除去)
    s_col = collection[stress_column]
    e_col = collection[strain_column]
    
    # 配列化
    stress = np.array(s_col.values, dtype=float)
    strain = np.array(e_col.values, dtype=float)
    
    # 共通の有効データインデックス
    mask = (~np.isnan(stress)) & (~np.isnan(strain))
    stress = stress[mask]
    strain = strain[mask]
    
    result_coll = collection.clone()
    
    # 1. ヤング率 (Young's Modulus)
    # 指定範囲内のデータで線形回帰
    e_start, e_end = elastic_range
    range_mask = (strain >= e_start) & (strain <= e_end)
    
    E = np.nan
    intercept = np.nan
    
    if np.sum(range_mask) > 2:
        E, intercept = np.polyfit(strain[range_mask], stress[range_mask], 1)
        
        # 結果追加
        result_coll.add_result(ScalarResult(
            name=f"{result_prefix}_E",
            value=E,
            unit=f"{s_col.unit}/{e_col.unit}" if s_col.unit and e_col.unit else s_col.unit, # Strain unitless -> Stress unit
            metadata={"description": "Young's Modulus", "range": elastic_range}
        ))
    else:
        # 計算不可
        pass

    # 2. 降伏強度 / 耐力 (Yield Strength, 0.2% offset)
    # offset line: sigma = E * (epsilon - offset)
    # sigma_offset = E * epsilon - E * offset
    # 交点を探す: stress - (E * strain - E * offset) = 0
    
    yield_stress = np.nan
    yield_strain = np.nan
    
    if not np.isnan(E):
        offset_stress = E * (strain - offset) + intercept
        diff = stress - offset_stress
        
        # 符号が変わる点を探す (弾性域以降で)
        # 探索範囲を elasticity range の後からにする
        search_start_idx = np.where(strain > e_end)[0]
        if len(search_start_idx) > 0:
            start_idx = search_start_idx[0]
            
            for i in range(start_idx, len(diff)-1):
                if diff[i] * diff[i+1] <= 0:
                    # 交点発見 (線形補間)
                    r = abs(diff[i]) / (abs(diff[i]) + abs(diff[i+1]))
                    yield_strain = strain[i] + r * (strain[i+1] - strain[i])
                    yield_stress = stress[i] + r * (stress[i+1] - stress[i])
                    break
        
        if not np.isnan(yield_stress):
             result_coll.add_result(PointResult(
                name=f"{result_prefix}_yield",
                x=yield_strain,
                y=yield_stress,
                x_unit=e_col.unit,
                y_unit=s_col.unit,
                metadata={"description": f"{offset*100}% Offset Yield Strength", "offset": offset}
            ))

    # 3. ポアソン比 (Poisson's Ratio)
    # -e_lat / e_long in elastic range
    if lateral_strain_column:
        if lateral_strain_column not in collection.columns:
             raise ValueError(f"横ひずみカラム '{lateral_strain_column}' が見つかりません")
             
        l_col = collection[lateral_strain_column]
        lat_strain = np.array(l_col.values, dtype=float)
        lat_strain = lat_strain[mask] # 同様にマスク
        
        if np.sum(range_mask) > 2:
            # 横ひずみ vs 縦ひずみの傾き = -nu
            # slope = polyfit(x=long, y=lat)
            # nu = -slope
            slope_nu, _ = np.polyfit(strain[range_mask], lat_strain[range_mask], 1)
            nu = -slope_nu
            
            result_coll.add_result(ScalarResult(
                name=f"{result_prefix}_nu",
                value=nu,
                unit=None,
                metadata={"description": "Poisson's Ratio", "range": elastic_range}
            ))

    return result_coll
