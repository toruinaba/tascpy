from typing import List, Optional, Union
import numpy as np
from ...operations.registry import operation
from ...domains.strain import StrainCollection
from ...core.column import Column
from ...functional.strain.rosette import compute_rosette_strains

@operation(domain="strain")
def calculate_rosette_strains(
    collection: StrainCollection,
    rosette_name: Optional[str] = None,
    columns: Optional[List[str]] = None,
    rosette_type: str = "rectangular",
    orientation: float = 0.0,
    prefix: Optional[str] = None
) -> StrainCollection:
    """ロゼットひずみ計算 (主ひずみ・主応力方向)

    3軸ひずみゲージの値から、最大・最小主ひずみ、最大せん断ひずみ、主ひずみ方向を計算します。

    Args:
        collection: ひずみコレクション
        rosette_name: 定義済みのロゼット名（metadataから情報を取得）
        columns: ゲージのカラム名リスト [e1, e2, e3]。
                 rosette_name指定時は無視されます。
                 直交の場合: 0, 45, 90度
                 デルタの場合: 0, 60, 120度
        rosette_type: ロゼットタイプ ('rectangular' or 'delta')
                      rosette_name指定時はmetadataが優先されます。
        orientation: 第1ゲージの設置角度（X軸基準、反時計回り、度単位）
                     rosette_name指定時はmetadataが優先されます。
        prefix: 結果カラム名の接頭辞。デフォルトは rosette_name または "rosette"

    Returns:
        StrainCollection: 計算結果（e_max, e_min, gamma_max, theta）が追加されたコレクション
    """
    
    # ロゼット情報の取得
    target_columns = columns
    r_type = rosette_type
    angle_offset = orientation
    
    if rosette_name:
        rosette_info = collection.get_rosette(rosette_name)
        if rosette_info:
            target_columns = rosette_info.get("columns")
            r_type = rosette_info.get("type", rosette_type)
            angle_offset = rosette_info.get("orientation", orientation)
            if prefix is None:
                prefix = rosette_name
    
    if prefix is None:
        prefix = "rosette"
        
    if not target_columns or len(target_columns) != 3:
        raise ValueError("3つのひずみカラムを指定する必要があります")
        
    for col in target_columns:
        if col not in collection.columns:
            raise ValueError(f"カラム '{col}' が見つかりません")

    # データの取得
    e1 = np.array(collection[target_columns[0]].values, dtype=float)
    e2 = np.array(collection[target_columns[1]].values, dtype=float)
    e3 = np.array(collection[target_columns[2]].values, dtype=float)
    
    # 計算 (Reference: Dally & Riley or standard mechanics of materials)
    # Unit assumption: Strain is dimensionless (microstrain handling is up to user, but usually raw strain)
    
    e_max, e_min, gamma_max, final_theta = compute_rosette_strains(
        e1, e2, e3, r_type=r_type, angle_offset=angle_offset
    )
    
    # 結果の格納
    result = collection.clone()
    
    # 単位の継承 (e1の単位を使う)
    unit = collection[target_columns[0]].unit
    
    new_cols = {
        f"{prefix}_e1": (e_max, "Max Principal Strain"),
        f"{prefix}_e2": (e_min, "Min Principal Strain"),
        f"{prefix}_gamma": (gamma_max, "Max Shear Strain"),
        f"{prefix}_theta": (final_theta, "Principal Direction Angle (deg)")
    }
    
    for name, (vals, desc) in new_cols.items():
        col_unit = unit
        if "theta" in name:
            col_unit = "deg"
            
        result.columns[name] = Column(
            ch=None,
            name=name,
            unit=col_unit,
            values=vals,
            metadata={"description": desc, "source_rosette": rosette_name or "manual"}
        )
        
        # 座標情報をコピー（代表として第1ゲージの座標を使う、あるいはロゼット中心があればそれを使う）
        # 这里では第1ゲージの座標をコピーする
        x, y, z = collection.get_column_coordinates(target_columns[0])
        result.set_column_coordinates(name, x, y, z)

    return result
