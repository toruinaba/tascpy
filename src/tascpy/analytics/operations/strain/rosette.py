"""ひずみドメインのロゼットひずみ解析関数"""

from typing import List, Optional
import numpy as np

from tascpy.domains.strain import StrainCollection
from tascpy.core.column import Column
from ...operations.registry import operation
from ...functional.strain.rosette import compute_rosette_strains


@operation(domain="strain")
def calculate_rosette_strains(
    collection: StrainCollection,
    rosette_name: Optional[str] = None,
    columns: Optional[List[str]] = None,
    rosette_type: str = "rectangular",
    orientation: float = 0.0,
    prefix: Optional[str] = None,
) -> StrainCollection:
    """ロゼットひずみ計算 (主ひずみ・主応力方向)。

    3軸ひずみゲージの値から、最大・最小主ひずみ、最大せん断ひずみ、主ひずみ方向を計算します。

    Args:
        collection: ひずみコレクション
        rosette_name: 定義済みのロゼット名（metadataから情報を取得）
        columns: ゲージのカラム名リスト [e1, e2, e3]。
                 rosette_name指定時は無視されます。
        rosette_type: ロゼットタイプ ('rectangular' or 'delta')
        orientation: 第1ゲージの設置角度（X軸基準、反時計回り、度単位）
        prefix: 結果カラム名の接頭辞。デフォルトは rosette_name または \"rosette\"

    Returns:
        StrainCollection: 計算結果（e_max, e_min, gamma_max, theta）が追加されたコレクション

    Examples:
        >>> col = col.ops.calculate_rosette_strains(
        ...     columns=["CH1", "CH2", "CH3"], rosette_type="rectangular"
        ... )
    """
    target_columns = columns
    r_type = rosette_type
    angle_offset = orientation

    if rosette_name:
        rosette_info = collection.get_rosette(rosette_name)
        if rosette_info:
            target_columns = rosette_info.get("columns", target_columns)
            r_type = rosette_info.get("type", r_type)
            angle_offset = rosette_info.get("orientation", angle_offset)
            if prefix is None:
                prefix = rosette_name

    if prefix is None:
        prefix = "rosette"

    if not target_columns or len(target_columns) != 3:
        raise ValueError("3つのひずみカラムを指定する必要があります")

    for col in target_columns:
        if col not in collection.columns:
            raise ValueError(f"カラム '{col}' が見つかりません")

    e1 = np.array(collection[target_columns[0]].values, dtype=float)
    e2 = np.array(collection[target_columns[1]].values, dtype=float)
    e3 = np.array(collection[target_columns[2]].values, dtype=float)

    e_max, e_min, gamma_max, final_theta = compute_rosette_strains(
        e1, e2, e3, r_type=r_type, angle_offset=angle_offset
    )

    result = collection.clone()
    unit = collection[target_columns[0]].unit

    new_cols = {
        f"{prefix}_e1": (e_max, "Max Principal Strain"),
        f"{prefix}_e2": (e_min, "Min Principal Strain"),
        f"{prefix}_gamma": (gamma_max, "Max Shear Strain"),
        f"{prefix}_theta": (final_theta, "Principal Direction Angle (deg)"),
    }

    for name, (vals, desc) in new_cols.items():
        col_unit = "deg" if "theta" in name else unit
        result.columns[name] = Column(
            ch=None,
            name=name,
            unit=col_unit,
            values=vals,
            metadata={"description": desc, "source_rosette": rosette_name or "manual"},
        )
        # 第1ゲージの座標をコピー
        x, y, z = collection.get_column_coordinates(target_columns[0])
        result.set_column_coordinates(name, x, y, z)

    return result
