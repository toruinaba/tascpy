from typing import Optional, List, Any, Dict, Union, Tuple
import numpy as np
from ...operations.registry import operation
from ...domains.strain import StrainCollection
from ...core.column import Column
from ...core.result import ScalarResult, PointResult
from ...operations.validation import requires_column
from ...functional.strain.ss_analysis import compute_stress, compute_material_properties

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
    
    # functionalモジュールの純粋な関数を呼び出す
    stress_vals = compute_stress(load_vals, area)
    
    result = collection.clone()
    result.columns[result_column] = Column(
        ch=None,
        name=result_column,
        values=stress_vals.tolist() if isinstance(stress_vals, np.ndarray) else stress_vals,
        unit=unit,
        metadata={
            "description": f"Calculated Stress (Load: {load_column}, Area: {area})", 
            "source_load": load_column,
            "area": area
        }
    )
    
    return result

from ...operations.abstraction import store_multiple_results

@operation(domain="strain")
@store_multiple_results(
    results=[
        {
            "type": "scalar", 
            "name": "{result_prefix}_E", 
            "index": 0, 
            "metadata": {"description": "Young's Modulus"}
        },
        {
            "type": "point", 
            "name": "{result_prefix}_yield", 
            "x_index": 1, 
            "y_index": 2, 
            "metadata": {"description": "Offset Yield Strength"}
        },
        {
            "type": "scalar", 
            "name": "{result_prefix}_nu", 
            "index": 3, 
            "metadata": {"description": "Poisson's Ratio"}
        }
    ]
)
def analyze_material_properties(
    collection: StrainCollection,
    stress_column: str,
    strain_column: str,
    lateral_strain_column: Optional[str] = None,
    elastic_range: Tuple[float, float] = (0.0005, 0.0025), # Strain range for Young's Modulus
    offset: float = 0.002, # 0.2% offset
    result_prefix: str = "material"
) -> Tuple[float, float, float, float]:
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
        Tuple: E, yield_strain, yield_stress, nu
    """
    if stress_column not in collection.columns:
        raise ValueError(f"応力カラム '{stress_column}' が見つかりません")
    if strain_column not in collection.columns:
        raise ValueError(f"ひずみカラム '{strain_column}' が見つかりません")

    # データ取得
    stress = np.array(collection[stress_column].values, dtype=float)
    strain = np.array(collection[strain_column].values, dtype=float)
    
    lateral_strain = None
    if lateral_strain_column:
        if lateral_strain_column not in collection.columns:
            raise ValueError(f"横ひずみカラム '{lateral_strain_column}' が見つかりません")
        lateral_strain = np.array(collection[lateral_strain_column].values, dtype=float)
    
    # functionalモジュールの純粋な関数を呼び出してタプルを返すだけ
    return compute_material_properties(
        stress, strain, lateral_strain, elastic_range, offset
    )
