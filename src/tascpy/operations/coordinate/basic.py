"""座標ドメインの基本的な操作関数

このモジュールには、座標情報を取得・設定するための基本的な操作関数が含まれています。
"""

from typing import Dict, Optional, List, Any, Tuple
import numpy as np
from ...operations.registry import operation
from ...domains.coordinate import CoordinateCollection


@operation(domain="coordinate")
def get_column_coordinates(
    collection: CoordinateCollection, column: str
) -> Dict[str, Optional[float]]:
    """列の座標情報を取得する

    Args:
        collection: 座標コレクション
        column: 列名

    Returns:
        Dict[str, Optional[float]]: 座標情報を含む辞書
    """
    x, y, z = collection.get_column_coordinates(column)
    return {"x": x, "y": y, "z": z}


@operation(domain="coordinate")
def set_column_coordinates(
    collection: CoordinateCollection,
    column: str,
    x: Optional[float] = None,
    y: Optional[float] = None,
    z: Optional[float] = None,
) -> CoordinateCollection:
    """指定した列の座標値を設定する

    Args:
        collection: 座標コレクション
        column: 列名
        x: X座標
        y: Y座標
        z: Z座標

    Returns:
        CoordinateCollection: 更新されたコレクション
    """
    result = collection.clone()
    result.set_column_coordinates(column, x=x, y=y, z=z)
    return result


@operation(domain="coordinate")
def get_columns_with_coordinates(collection: CoordinateCollection) -> List[str]:
    """座標情報が設定されている列のリストを取得する

    Args:
        collection: 座標コレクション

    Returns:
        List[str]: 座標情報を持つ列名のリスト
    """
    return collection.get_columns_with_coordinates()


@operation(domain="coordinate")
def extract_coordinates(
    collection: CoordinateCollection, result_prefix: str = "coord_"
) -> CoordinateCollection:
    """各列の座標値を新しい列としてコレクションに追加する

    Args:
        collection: 座標コレクション
        result_prefix: 結果列の接頭辞

    Returns:
        CoordinateCollection: 座標列を追加したコレクション
    """
    from ...core.column import Column

    result = collection.clone()
    coordinate_columns = collection.get_columns_with_coordinates()

    for column_name in coordinate_columns:
        x, y, z = collection.get_column_coordinates(column_name)

        # X座標の列を追加
        if x is not None:
            result.columns[f"{result_prefix}{column_name}_x"] = Column(
                ch=None,
                name=f"{result_prefix}{column_name}_x",
                unit="m",  # 単位はメートルと仮定
                values=[x] * len(collection.step),
                metadata={
                    "description": f"X coordinate of {column_name}",
                    "type": "coordinate",
                    "component": "x",
                },
            )

        # Y座標の列を追加
        if y is not None:
            result.columns[f"{result_prefix}{column_name}_y"] = Column(
                ch=None,
                name=f"{result_prefix}{column_name}_y",
                unit="m",  # 単位はメートルと仮定
                values=[y] * len(collection.step),
                metadata={
                    "description": f"Y coordinate of {column_name}",
                    "type": "coordinate",
                    "component": "y",
                },
            )

        # Z座標の列を追加
        if z is not None:
            result.columns[f"{result_prefix}{column_name}_z"] = Column(
                ch=None,
                name=f"{result_prefix}{column_name}_z",
                unit="m",  # 単位はメートルと仮定
                values=[z] * len(collection.step),
                metadata={
                    "description": f"Z coordinate of {column_name}",
                    "type": "coordinate",
                    "component": "z",
                },
            )

    return result
