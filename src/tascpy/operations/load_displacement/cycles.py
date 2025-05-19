"""荷重-変位データのサイクル処理関数"""

from typing import Union, List, Optional
import numpy as np
from ...operations.registry import operation
from ...domains.load_displacement import LoadDisplacementCollection
from ...core.column import Column
from .utils import get_load_column, get_displacement_column


@operation(domain="load_displacement")
def cycle_count(
    collection: LoadDisplacementCollection,
    column: Optional[str] = None,
    step: float = 0.5,
    result_column: Optional[str] = None,
) -> LoadDisplacementCollection:
    """データの荷重符号反転からサイクル数をカウント

    荷重の符号変化（正負の反転）からサイクル数をカウントし、
    新しい列として追加します。

    Args:
        collection: 荷重-変位コレクション
        column: サイクルをカウントする列（指定がない場合は荷重列を使用）
        step: サイクルカウントの増分
        result_column: 結果を格納する列名

    Returns:
        LoadDisplacementCollection: サイクル数を含むコレクション
    """
    # 対象列の特定
    if column is None:
        # デフォルトは荷重列
        column = get_load_column(collection)

    if column not in collection.columns:
        raise ValueError(f"列 '{column}' が見つかりません")

    # データを取得
    data = collection[column].values

    # サイクルをカウント
    cycle = [1.0]
    for i in range(1, len(data)):
        if (
            data[i] is not None
            and data[i - 1] is not None
            and data[i] * data[i - 1] < 0
        ):  # 符号が変わった
            c = cycle[i - 1] + step
            cycle.append(c)
        else:
            cycle.append(cycle[i - 1])

    # 整数に変換
    markers = [int(c) for c in cycle]

    # 結果列名の決定
    if result_column is None:
        result_column = f"{column}_cycle"

    # 結果を新しいコレクションとして作成
    result = collection.clone()
    result.columns[result_column] = Column(
        ch=None,  # chパラメータを追加
        name=result_column,
        unit=None,  # unitパラメータを追加
        values=markers,
        metadata={
            "description": f"Cycle count based on {column}"
        },  # descriptionをmetadataに移動
    )

    return result


@operation(domain="load_displacement")
def split_by_cycles(
    collection: LoadDisplacementCollection, cycle_column: Optional[str] = None
) -> List[LoadDisplacementCollection]:
    """サイクル番号ごとにデータを分割

    データをサイクル番号ごとに分割し、各サイクルの
    荷重-変位コレクションのリストを返します。

    Args:
        collection: 荷重-変位コレクション
        cycle_column: サイクル番号を含む列名（指定がない場合は自動検出/生成）

    Returns:
        List[LoadDisplacementCollection]: サイクルごとに分割されたコレクションのリスト
    """
    # サイクル列の特定または作成
    if cycle_column is None:
        # 既存のサイクル列を探す
        for col_name in collection.columns:
            if "cycle" in col_name.lower():
                cycle_column = col_name
                break

        # 見つからない場合は荷重列に対してcycle_countを実行
        if cycle_column is None:
            temp_result = cycle_count(collection)
            cycle_column = [
                c for c in temp_result.columns if c not in collection.columns
            ][0]
            collection = temp_result

    # サイクルで分割
    from ...operations.core.split import split_by_integers

    return split_by_integers(collection, collection[cycle_column].values)
