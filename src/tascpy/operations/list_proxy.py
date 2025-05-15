from typing import Any, Dict, List, Optional, Callable, TypeVar, Union, Generic
from ..core.collection import ColumnCollection
from .proxy import CollectionOperations

# ColumnCollectionおよびその派生クラス用のTypeVar
T = TypeVar("T", bound=ColumnCollection)


class CollectionListOperations(Generic[T]):
    """複数のColumnCollectionを一度に操作するためのプロキシクラス"""

    def __init__(self, collections: List[T], domain: str = "core"):
        """
        Args:
            collections: ColumnCollectionオブジェクトのリスト
            domain: 操作のドメイン（デフォルトは"core"）
        """
        self._collections = collections
        self._domain = domain

    def __len__(self) -> int:
        """コレクションリストの長さを返します"""
        return len(self._collections)

    def __getitem__(
        self, index: Union[int, slice]
    ) -> Union[CollectionOperations[T], "CollectionListOperations[T]"]:
        """指定されたインデックスのCollectionOperationsを返します"""
        if isinstance(index, int):
            if index < 0 or index >= len(self._collections):
                raise IndexError("インデックスが範囲外です")
            return CollectionOperations(self._collections[index], self._domain)
        elif isinstance(index, slice):
            sliced_collections = self._collections[index]
            return CollectionListOperations(sliced_collections, self._domain)
        else:
            raise TypeError("インデックスは整数またはスライスである必要があります")

    def map(
        self, operation: str, *args, **kwargs
    ) -> Union["CollectionListOperations", List[Any]]:
        """
        各コレクションに同じ操作を適用します

        Args:
            operation: 適用する操作名
            *args: 操作に渡す位置引数
            **kwargs: 操作に渡すキーワード引数

        Returns:
            操作結果のCollectionListOperationsまたは結果のリスト
        """
        results = []
        for collection in self._collections:
            # CollectionOperationsオブジェクトを作成
            ops = CollectionOperations(collection, self._domain)
            # 指定された操作メソッドを取得
            method = getattr(ops, operation, None)
            if method is None:
                raise AttributeError(f"操作 '{operation}' は存在しません")

            # メソッドを呼び出し、結果を取得
            result = method(*args, **kwargs)

            # 結果がCollectionOperationsの場合は元のオブジェクトを取得
            if isinstance(result, CollectionOperations):
                result = result.end()
            elif isinstance(result, CollectionListOperations):
                result = result.end_all()

            results.append(result)

        # 全ての結果がColumnCollectionの場合、新しいCollectionListOperationsを返す
        if all(isinstance(r, ColumnCollection) for r in results):
            return CollectionListOperations(results, self._domain)

        # それ以外の場合は結果のリストをそのまま返す
        return results

    def filter(
        self, predicate: Callable[[ColumnCollection], bool]
    ) -> "CollectionListOperations":
        """
        条件を満たすコレクションだけをフィルタリングします

        Args:
            predicate: フィルタリング条件

        Returns:
            フィルタリングされたコレクションを持つCollectionListOperations
        """
        filtered = [col for col in self._collections if predicate(col)]
        return CollectionListOperations(filtered, self._domain)

    def concat(self) -> CollectionOperations:
        """
        全てのコレクションを連結して一つのCollectionOperationsを返します

        Returns:
            連結されたデータを持つCollectionOperations
        """
        from itertools import chain

        # コレクションが空の場合はエラー
        if not self._collections:
            raise ValueError("連結するコレクションがありません")

        # 最初のコレクションをベースにする
        result = self._collections[0].clone()

        # 2番目以降のコレクションを連結
        for collection in self._collections[1:]:
            # ステップ値を連結
            result.step.values.extend(collection.step.values)

            # 各カラムのデータを連結
            for name, column in collection.columns.items():
                if name in result.columns:
                    # 既存のカラムにデータを追加
                    result.columns[name].values.extend(column.values)
                else:
                    # 新しいカラムを追加（前のコレクションではNoneで埋める）
                    new_column = column.clone()
                    # 前のコレクションの分をNoneで埋める
                    previous_length = sum(
                        len(c.step.values) for c in self._collections[:1]
                    )
                    new_column.values = [None] * previous_length + column.values
                    result.columns[name] = new_column

            # 他のコレクションにあってこのコレクションにないカラムをNoneで埋める
            for existing_name in result.columns:
                if existing_name not in collection.columns:
                    result.columns[existing_name].values.extend(
                        [None] * len(collection.step.values)
                    )

        return CollectionOperations(result, self._domain)

    def end_all(self) -> List[T]:
        """操作を終了し、ColumnCollectionのリストを返します"""
        return self._collections

    def as_domain(self, domain: str, **kwargs) -> "CollectionListOperations":
        """
        全てのコレクションを指定されたドメインに変換します

        Args:
            domain: 変換先のドメイン名
            **kwargs: 変換に渡す追加引数

        Returns:
            変換されたコレクションリスト
        """
        converted = []
        for collection in self._collections:
            ops = CollectionOperations(collection, self._domain)
            converted_ops = ops.as_domain(domain, **kwargs)
            converted.append(converted_ops.end())

        return CollectionListOperations(converted, domain)
