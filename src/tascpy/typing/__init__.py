# 自動生成されたスタブファイル - 編集しないでください
# このファイルはPylanceの自動補完と型チェック用です

from typing import cast, TypeVar, Union, overload, Any, Dict, List, Optional, Callable, Generic, Literal
from ..core.collection import ColumnCollection

from .core import CoreCollectionOperations
from .load_displacement import LoadDisplacementCollectionOperations
from .coordinate import CoordinateCollectionOperations
from .list_proxy import CollectionListOperations

# 型ヒント用の変数
T = TypeVar('T', bound='CollectionOperationsBase')

# ドメインごとのスタブ型をエクスポート
__all__ = [
    'CoreCollectionOperations',
    'LoadDisplacementCollectionOperations',
    'CoordinateCollectionOperations',
    'CollectionListOperations',
]
