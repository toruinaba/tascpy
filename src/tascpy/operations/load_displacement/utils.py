"""荷重-変位データの基本的な計算・ユーティリティ関数"""

import numpy as np
from typing import Union, List, Optional, Tuple
from ...operations.registry import operation
from ...domains.load_displacement import LoadDisplacementCollection


@operation(domain="load_displacement")
def get_load_column(collection: LoadDisplacementCollection) -> str:
    """荷重データのカラム名を取得

    Args:
        collection: 荷重-変位コレクション

    Returns:
        str: 荷重データのカラム名
    """
    ld_info = collection.metadata.get("load_displacement_domain", {})
    return ld_info.get("load_column", "load")


@operation(domain="load_displacement")
def get_displacement_column(collection: LoadDisplacementCollection) -> str:
    """変位データのカラム名を取得

    Args:
        collection: 荷重-変位コレクション

    Returns:
        str: 変位データのカラム名
    """
    ld_info = collection.metadata.get("load_displacement_domain", {})
    return ld_info.get("displacement_column", "displacement")


@operation(domain="load_displacement")
def get_load_data(collection: LoadDisplacementCollection) -> np.ndarray:
    """荷重データを取得

    Args:
        collection: 荷重-変位コレクション

    Returns:
        np.ndarray: 荷重データの配列
    """
    load_column = get_load_column(collection)
    return np.array(
        [v if v is not None else np.nan for v in collection[load_column].values]
    )


@operation(domain="load_displacement")
def get_displacement_data(collection: LoadDisplacementCollection) -> np.ndarray:
    """変位データを取得

    Args:
        collection: 荷重-変位コレクション

    Returns:
        np.ndarray: 変位データの配列
    """
    disp_column = get_displacement_column(collection)
    return np.array(
        [v if v is not None else np.nan for v in collection[disp_column].values]
    )


@operation(domain="load_displacement")
def get_valid_data_mask(collection: LoadDisplacementCollection) -> np.ndarray:
    """有効なデータポイントのマスクを取得

    Args:
        collection: 荷重-変位コレクション

    Returns:
        np.ndarray: 有効なデータのブールマスク
    """
    load_data = get_load_data(collection)
    disp_data = get_displacement_data(collection)

    # NaNを含まないデータポイントを特定
    return ~(np.isnan(load_data) | np.isnan(disp_data))


@operation(domain="load_displacement")
def get_valid_data(
    collection: LoadDisplacementCollection,
) -> Tuple[np.ndarray, np.ndarray]:
    """有効な荷重と変位のデータ組を取得

    Args:
        collection: 荷重-変位コレクション

    Returns:
        Tuple[np.ndarray, np.ndarray]: 有効な(変位, 荷重)データの組
    """
    load_data = get_load_data(collection)
    disp_data = get_displacement_data(collection)

    # 有効なデータのみを抽出
    mask = get_valid_data_mask(collection)
    return disp_data[mask], load_data[mask]
