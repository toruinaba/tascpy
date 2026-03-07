# 自動生成されたプロキシベーススタブ - 編集しないでください
from __future__ import annotations
from typing import Optional, Union, List, Dict, Any, Callable, TypeVar, Generic, overload, Literal, TYPE_CHECKING
from tascpy.core.collection import ColumnCollection

if TYPE_CHECKING:
    from .core import CoreCollectionOperations
    from .strain import StrainCollectionOperations
    from .load_displacement import LoadDisplacementCollectionOperations
    from .coordinate import CoordinateCollectionOperations

# コレクション型のTypeVar
C = TypeVar('C', bound=ColumnCollection)
# 戻り値型のTypeVar
T = TypeVar('T', bound='CollectionOperationsBase')

class CollectionOperationsBase(Generic[C]):
    """コレクション操作の基底クラス"""

    def end(self) -> C:
        """操作チェーンを終了し、最終的なColumnCollectionを取得"""
        ...

    def debug(self, message: Optional[str] = None) -> T:
        """デバッグメッセージを表示
        
        Args:
            message: デバッグメッセージ
        
        Returns:
            自身を返す
        """
        ...

    @overload
    def as_domain(self, domain: Literal['core'], **kwargs: Any) -> CoreCollectionOperations:
        ...

    @overload
    def as_domain(self, domain: Literal['strain'], **kwargs: Any) -> StrainCollectionOperations:
        ...

    @overload
    def as_domain(self, domain: Literal['load_displacement'], **kwargs: Any) -> LoadDisplacementCollectionOperations:
        ...

    @overload
    def as_domain(self, domain: Literal['coordinate'], **kwargs: Any) -> CoordinateCollectionOperations:
        ...

    def as_domain(self, domain: str, **kwargs: Any) -> CollectionOperationsBase:
        """現在のコレクションを指定されたドメインに変換
        
        Args:
            domain: 変換先のドメイン名
            **kwargs: 変換に渡す追加引数
        
        Returns:
            指定されたドメインの操作メソッドを提供するCollectionOperations
        """
        ...

