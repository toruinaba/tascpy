from typing import Dict, Any, Optional, Tuple
from ..core.collection import ColumnCollection
from .factory import DomainCollectionFactory
from .load_displacement import LoadDisplacementCollection
from ..domains.converters import register_domain_converter


def create_load_displacement_collection(**kwargs: Any) -> LoadDisplacementCollection:
    """荷重-変形コレクションを作成するファクトリ関数"""
    return LoadDisplacementCollection(**kwargs)


# ドメインファクトリーへの登録
DomainCollectionFactory.register(
    "load_displacement", create_load_displacement_collection
)


@register_domain_converter(source_domain="core", target_domain="load_displacement")
def prepare_for_load_displacement(
    collection: ColumnCollection, **kwargs: Any
) -> Tuple[ColumnCollection, Dict[str, Any]]:
    """一般コレクションから荷重-変位コレクションへの変換準備を行う

    Args:
        collection: 変換元のコレクション
        **kwargs: 追加のパラメータ

    Returns:
        tuple: (変換用に準備されたコレクション, 更新されたkwargs)
    """
    # 荷重カラムと変位カラムを決定
    load_column = kwargs.get("load_column")
    disp_column = kwargs.get("displacement_column")

    # カラム名が指定されていない場合、既存カラムから推測
    if not load_column:
        # 荷重を含むカラム名を探す
        possible_load_columns = ["load", "force", "荷重", "力"]
        for colname in possible_load_columns:
            matching = [
                c for c in collection.columns.keys() if colname.lower() in c.lower()
            ]
            if matching:
                load_column = matching[0]
                break

    if not disp_column:
        # 変位を含むカラム名を探す
        possible_disp_columns = ["disp", "displacement", "変位", "変形"]
        for colname in possible_disp_columns:
            matching = [
                c for c in collection.columns.keys() if colname.lower() in c.lower()
            ]
            if matching:
                disp_column = matching[0]
                break

    # カラム名が見つからない場合は最初の数値カラムを使用
    if not load_column or not disp_column:
        numeric_columns = [
            name
            for name, col in collection.columns.items()
            if any(isinstance(v, (int, float)) for v in col.values)
        ]

        if len(numeric_columns) >= 2:
            if not load_column:
                load_column = numeric_columns[0]
            if not disp_column:
                disp_column = numeric_columns[1]

    # 必要なカラムが見つからない場合はエラー
    if not load_column or not disp_column:
        raise ValueError("荷重と変位のカラムを指定または検出できませんでした")

    # 更新されたkwargsを返す
    kwargs.update({"load_column": load_column, "displacement_column": disp_column})

    return collection, kwargs
