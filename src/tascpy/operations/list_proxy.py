from typing import Any, Dict, List, Optional, Callable, TypeVar, Union, Generic
from copy import deepcopy
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
        import numpy as np

        # コレクションが空の場合はエラー
        if not self._collections:
            raise ValueError("連結するコレクションがありません")

        # ステップとカラムの値をリストに収集
        all_steps = [c.step.values for c in self._collections]
        merged_steps = np.concatenate(all_steps)

        # 全てのカラム名を収集
        all_columns = set()
        for c in self._collections:
            all_columns.update(c.columns.keys())

        # 結果の辞書を作成
        merged_columns = {}
        
        # 各カラムについてデータを結合
        for name in all_columns:
            column_values_list = []
            
            # 各コレクションから値を取得（なければNone埋め）
            # ただし、元のカラムの型や属性をどう保持するか？
            # 最初の出現するカラムの属性を採用する
            base_column = None
            
            for c in self._collections:
                length = len(c.step.values)
                if name in c.columns:
                    col = c.columns[name]
                    if base_column is None:
                        base_column = col
                    column_values_list.append(col.values)
                else:
                    # 存在しない場合はNaN (数値) または None (オブジェクト) で埋める
                    # ここでは一旦None (np.nan) で埋めるが、型合わせが必要
                    # base_columnがまだない場合は後で解決... 難しい
                    # 簡易的に: base_columnが決まっていればそれに合わせる
                    # 決まっていなければ一旦Noneのリストとする
                    column_values_list.append(np.full(length, np.nan)) # Default to NaN

            # 結合
            # base_columnを使って型を適切に処理する必要がある
            # 簡易実装：np.concatenate。型不一致ならオブジェクト配列になるかも
            
            # 改善: NaN埋めではなく、適切な型で埋める
            # しかし、まだbase_columnが不明な場合がある（最初のコレクションにない場合）
            # 再度ループするか、より賢くやる
            
        # よりシンプルな実装: ステップごとにループせず、コレクションごとに処理
        # しかしNumPyならarray結合が速い
        
        # リライト:
        # 1. ベースとなるコレクション（結果の入れ物）を作るのは難しい（カラムが異なる）
        # 2. 新しいDataHolder/ColumnCollectionを作る
        
        # 各カラムごとにデータを集める
        final_columns = {}
        total_length = sum(len(c) for c in self._collections)
        
        for name in all_columns:
            # この名を持つ最初のカラムを探してメタデータをコピー
            base_col = next(c.columns[name] for c in self._collections if name in c.columns)
            
            # 全コレクションの値を収集
            arrays_to_concat = []
            for c in self._collections:
                if name in c.columns:
                    arrays_to_concat.append(c.columns[name].values)
                else:
                    # 欠損部分を埋める
                    # base_colの型に合わせてNaNまたはNoneで埋める
                    fill_val = np.nan if np.issubdtype(base_col.values.dtype, np.number) else None
                    arrays_to_concat.append(np.full(len(c), fill_val))
            
            merged_values = np.concatenate(arrays_to_concat)
            new_col = base_col.clone()
            new_col.values = merged_values
            final_columns[name] = new_col

        # 新しいColumnCollectionを作成
        # 注意: ColumnCollectionのコンストラクタはstepとcolumnsを受け取る
        # 既存のクラスメソッド等を使わずに直接構築
        
        result_collection = self._collections[0].__class__(
            merged_steps,
            final_columns,
            deepcopy(self._collections[0].metadata) # メタデータは最初のものを継承
        )

        return CollectionOperations(result_collection, self._domain)

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
