# 自動生成されたプロキシベーススタブ - 編集しないでください
from typing import Optional, Union, List, Dict, Any, Callable, TypeVar, Generic, overload, Literal
from ..core.collection import ColumnCollection

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

