# 自動生成されたstubsドメインのスタブファイル - 編集しないでください
from typing import Optional, Union, List, Dict, Any, Callable, TypeVar, cast
from ...core.collection import ColumnCollection
from .proxy_base import CollectionOperationsBase

class StubsCollectionOperations(CollectionOperationsBase):
    """stubsドメインの操作メソッドスタブ定義
    
    このクラスはPylanceの型チェックとオートコンプリートのためのスタブです。
    実際の実行には使用されません。
    """

    def end(self) -> ColumnCollection:
        """操作チェーンを終了し、最終的なColumnCollectionを取得"""
        ...

    def debug(self, message: Optional[str] = None) -> "StubsCollectionOperations":
        """デバッグメッセージを表示
        
        Args:
            message: デバッグメッセージ
        
        Returns:
            StubsCollectionOperations: 自身を返す
        """
        ...

