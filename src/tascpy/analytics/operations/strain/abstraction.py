"""ひずみドメインの抽象化・デコレータ群"""

import functools
from typing import Callable
import numpy as np

from tascpy.domains.strain import StrainCollection
from tascpy.core.column import Column

def resolve_rosette_strains():
    """
    ロゼット定義またはカラムリストから3つのひずみ配列(e1, e2, e3)と設定を抽出し、
    純粋関数に注入するデコレータ。
    結果（e_max, e_min, gamma_max, theta）を受け取り、動的にカラムを生成する。
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(collection: StrainCollection, *args, **kwargs):
            rosette_name = kwargs.pop("rosette_name", None)
            columns = kwargs.pop("columns", None)
            r_type = kwargs.pop("rosette_type", "rectangular")
            angle_offset = kwargs.pop("orientation", 0.0)
            prefix = kwargs.pop("prefix", None)

            # ロゼット情報の取得
            target_columns = columns
            
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

            # データの取得
            e1 = np.array(collection[target_columns[0]].values, dtype=float)
            e2 = np.array(collection[target_columns[1]].values, dtype=float)
            e3 = np.array(collection[target_columns[2]].values, dtype=float)

            # 純粋関数の呼び出し
            e_max, e_min, gamma_max, final_theta = func(e1, e2, e3, r_type=r_type, angle_offset=angle_offset)

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
                
                # 第1ゲージの座標をコピー
                x, y, z = collection.get_column_coordinates(target_columns[0])
                result.set_column_coordinates(name, x, y, z)

            return result
        return wrapper
    return decorator


def resolve_stress_strain():
    """
    応力、ひずみ、横ひずみ（任意）の配列とその他のパラメータを抽出し、
    純粋関数に注入するデコレータ。
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(collection: StrainCollection, *args, **kwargs):
            stress_column = kwargs.pop("stress_column", None)
            strain_column = kwargs.pop("strain_column", None)
            lateral_strain_column = kwargs.pop("lateral_strain_column", None)

            # argsからのフォールバックサポート (引数順序: stress_column, strain_column)
            if stress_column is None and len(args) > 0:
                stress_column = args[0]
            if strain_column is None and len(args) > 1:
                strain_column = args[1]

            if not stress_column or stress_column not in collection.columns:
                raise ValueError(f"応力カラム '{stress_column}' が見つかりません")
            if not strain_column or strain_column not in collection.columns:
                raise ValueError(f"ひずみカラム '{strain_column}' が見つかりません")

            # データ取得
            stress = np.array(collection[stress_column].values, dtype=float)
            strain = np.array(collection[strain_column].values, dtype=float)
            
            lateral_strain = None
            if lateral_strain_column:
                if lateral_strain_column not in collection.columns:
                    raise ValueError(f"横ひずみカラム '{lateral_strain_column}' が見つかりません")
                lateral_strain = np.array(collection[lateral_strain_column].values, dtype=float)

            # args はここではもう使わない（キーワード引数として func に直接渡すか、必要なものをkwargsに残す）
            # kwargs の中から elastic_range と offset を抽出して渡す
            elastic_range = kwargs.pop("elastic_range", (0.0005, 0.0025))
            offset = kwargs.pop("offset", 0.002)

            # 純粋関数の呼び出し
            return func(
                stress=stress, 
                strain=strain, 
                lateral_strain=lateral_strain, 
                elastic_range=elastic_range, 
                offset=offset
            )
        return wrapper
    return decorator


def resolve_stress_calculation():
    """
    応力計算のための荷重データ配列と断面積を抽出し純粋関数に注入し、
    結果をカラムとして保存するデコレータ。
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(collection: StrainCollection, *args, **kwargs):
            load_column = kwargs.pop("load_column", None)
            area = kwargs.pop("area", None)
            result_column = kwargs.pop("result_column", "stress")
            unit = kwargs.pop("unit", "MPa")

            # argsフォールバック
            if load_column is None and len(args) > 0:
                load_column = args[0]
            if area is None and len(args) > 1:
                area = args[1]

            if load_column not in collection.columns:
                raise ValueError(f"荷重カラム '{load_column}' が見つかりません")
                
            load_vals = np.array(collection[load_column].values, dtype=float)
            
            # 純粋関数の呼び出し
            stress_vals = func(load_vals, area)
            
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
        return wrapper
    return decorator
