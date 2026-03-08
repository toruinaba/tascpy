"""ひずみドメインの応力-ひずみ解析関数"""

from typing import Optional, Tuple
import numpy as np

from tascpy.domains.strain import StrainCollection
from tascpy.core.column import Column
from ...operations.registry import operation
from ...operations.abstraction import store_point_result
from ...functional.strain.ss_analysis import compute_stress
from ...functional.load_displacement.analysis import compute_yield_point


@operation(domain="strain")
def calculate_stress(
    collection: StrainCollection,
    load_column: str = None,
    area: float = None,
    result_column: str = "stress",
    unit: str = "MPa",
) -> StrainCollection:
    """応力を計算する (Stress = Load / Area)。

    Args:
        collection: ひずみコレクション
        load_column: 荷重データのカラム名
        area: 断面積
        result_column: 結果を格納するカラム名
        unit: 結果の単位

    Returns:
        StrainCollection: 応力カラムが追加されたコレクション

    Examples:
        >>> col = col.ops.calculate_stress(load_column="荷重", area=10.0, result_column="応力")
    """
    if load_column not in collection.columns:
        raise ValueError(f"荷重カラム '{load_column}' が見つかりません")

    load_vals = np.array(collection[load_column].values, dtype=float)
    stress_vals = compute_stress(load_vals, area)

    result = collection.clone()
    result.columns[result_column] = Column(
        ch=None,
        name=result_column,
        values=stress_vals.tolist(),
        unit=unit,
        metadata={
            "description": f"Calculated Stress (Load: {load_column}, Area: {area})",
            "source_load": load_column,
            "area": area,
        },
    )
    return result


@operation(domain="strain")
@store_point_result(name="yield_point")
def find_yield_point(
    collection: StrainCollection,
    stress_column: str = None,
    strain_column: str = None,
    lateral_strain_column: Optional[str] = None,
    method: str = "offset",
    offset_value: float = 0.002,
    range_start: float = 0.1,
    range_end: float = 0.3,
    factor: float = 0.33,
    debug_mode: bool = False,
    fail_silently: bool = False,
    result_prefix: str = "yield",
) -> StrainCollection:
    """応力-ひずみデータから降伏点（Yield Point）を検出します。

    load_displacementドメインのfind_yield_pointと同様のアルゴリズムを使用しますが、
    応力(Load相当)とひずみ(Disp相当)を入力とします。

    Args:
        collection: ひずみコレクション
        stress_column: 応力データのカラム名
        strain_column: ひずみデータのカラム名
        lateral_strain_column: 横ひずみデータのカラム名（任意）
        method: 降伏点判定手法 (\"offset\", \"general\"). Defaults to \"offset\".
        offset_value: オフセット法におけるオフセットひずみ等. Defaults to 0.002.
        range_start: 剛性計算の開始比率. Defaults to 0.1.
        range_end: 剛性計算の終了比率. Defaults to 0.3.
        factor: 特定手法での係数. Defaults to 0.33.
        debug_mode: デバッグ情報を表示するか. Defaults to False.
        fail_silently: 検出失敗時に例外を投げず無視するか. Defaults to False.
        result_prefix: 結果名の接頭辞（現在は未使用）

    Returns:
        StrainCollection: 降伏点情報が結果として追加された新しいコレクション

    Examples:
        >>> col = col.ops.find_yield_point(
        ...     stress_column="応力", strain_column="CH1", method="offset", offset_value=0.002
        ... )
        >>> yield_pt = col.results["yield_point"]
        >>> yield_pt.x, yield_pt.y  # ひずみ, 応力
    """
    if not stress_column or stress_column not in collection.columns:
        raise ValueError(f"応力カラム '{stress_column}' が見つかりません")
    if not strain_column or strain_column not in collection.columns:
        raise ValueError(f"ひずみカラム '{strain_column}' が見つかりません")

    stress = np.array(collection[stress_column].values, dtype=float)
    strain = np.array(collection[strain_column].values, dtype=float)

    lateral_strain = None
    if lateral_strain_column:
        if lateral_strain_column not in collection.columns:
            raise ValueError(f"横ひずみカラム '{lateral_strain_column}' が見つかりません")
        lateral_strain = np.array(collection[lateral_strain_column].values, dtype=float)

    # compute_yield_point はひずみ(x)と応力(y)として呼ぶ
    return compute_yield_point(
        disp_data=strain,
        load_data=stress,
        method=method,
        offset_value=offset_value,
        range_start=range_start,
        range_end=range_end,
        factor=factor,
        debug_mode=debug_mode,
        fail_silently=fail_silently,
    )


# エイリアス
yield_point = find_yield_point
