# 自動生成されたCollectionListOperationsスタブ - 編集しないでください
from typing import Optional, Union, List, Dict, Any, Callable, TypeVar, Generic, overload
from ..core.collection import ColumnCollection
from .proxy_base import CollectionOperationsBase

# コレクション型のTypeVar
C = TypeVar('C', bound=ColumnCollection)

class CollectionListOperations(Generic[C]):
    """複数のColumnCollectionを一度に操作するためのプロキシクラス
    
    このクラスはPylanceの型チェックとオートコンプリートのためのスタブです。
    実際の実行には使用されません。
    """

    def __len__(self) -> int:
        """コレクションリストの長さを返します"""
        ...

    def __getitem__(
        self, index: Union[int, slice]
    ) -> Union[CollectionOperationsBase[C], "CollectionListOperations[C]"]:
        """指定されたインデックスのCollectionOperationsを返します
        
        Args:
            index: アクセスするインデックスまたはスライス
            
        Returns:
            インデックスの場合はCollectionOperations、スライスの場合はCollectionListOperations
            
        Raises:
            IndexError: インデックスが範囲外の場合
            TypeError: インデックスが整数またはスライスでない場合
        """
        ...

    def map(
        self, operation: str, *args: Any, **kwargs: Any
    ) -> Union["CollectionListOperations[C]", List[Any]]:
        """各コレクションに同じ操作を適用します
        
        Args:
            operation: 適用する操作名
            *args: 操作に渡す位置引数
            **kwargs: 操作に渡すキーワード引数
            
        Returns:
            操作結果のCollectionListOperationsまたは結果のリスト
            
        Raises:
            AttributeError: 指定された操作が存在しない場合
        """
        ...

    def filter(
        self, predicate: Callable[[C], bool]
    ) -> "CollectionListOperations[C]":
        """条件を満たすコレクションだけをフィルタリングします
        
        Args:
            predicate: フィルタリング条件を判定する関数
            
        Returns:
            フィルタリングされたコレクションを持つCollectionListOperations
        """
        ...

    def concat(self) -> CollectionOperationsBase[C]:
        """全てのコレクションを連結して一つのCollectionOperationsを返します
        
        Returns:
            連結されたデータを持つCollectionOperations
            
        Raises:
            ValueError: 連結するコレクションが存在しない場合
        """
        ...

    def end_all(self) -> List[C]:
        """操作を終了し、ColumnCollectionのリストを返します"""
        ...

    def as_domain(self, domain: str, **kwargs: Any) -> "CollectionListOperations":
        """全てのコレクションを指定されたドメインに変換します
        
        Args:
            domain: 変換先のドメイン名
            **kwargs: 変換に渡す追加引数
            
        Returns:
            変換されたコレクションリスト
        """
        ...