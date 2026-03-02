from typing import (
    Any,
    Dict,
    List,
    Optional,
    Callable,
    TypeVar,
    Union,
    TYPE_CHECKING,
    Generic,
)

from tascpy.core.collection import ColumnCollection
import numpy as np

if TYPE_CHECKING:
    from tascpy.typing.proxy_base import CollectionOperationsBase
    from tascpy.typing.core import CoreCollectionOperations



# ColumnCollectionおよびその派生クラス用のTypeVar
T = TypeVar("T", bound=ColumnCollection)


class CollectionOperations(Generic[T]):
    """ColumnCollectionの操作プロキシクラス, デコレーターパターンを使用"""

    def __init__(self, collection: T, domain: Optional[str] = None):
        """
        Args:
            collection: ColumnCollectionオブジェクト
            domain: 操作のドメイン（指定がない場合はコレクションのdomainを使用）
        """
        if isinstance(collection, type(self)):
            self._collection = collection._collection
            # ドメインが指定された場合はそれを優先、それ以外は元のプロキシのドメインを継承する
            if domain is not None:
                 self._domain = domain
            else:
                 self._domain = collection._domain
        else:
            self._collection = collection
            self._domain = domain if domain is not None else getattr(collection, "domain", "core")

        # スタブファイルが生成されていない場合、生成を試みる
        if TYPE_CHECKING:
            pass  # 型チェック時には何もしない
        else:
            from .registry import OperationRegistry

            OperationRegistry.generate_stubs()

        self._add_operations()

    def _add_operations(self) -> None:
        """操作メソッドを追加するためのメソッド"""
        from tascpy.analytics.operations.registry import OperationRegistry

        core_ops = OperationRegistry.get_operations("core")
        for name, func in core_ops.items():
            setattr(self, name, self._create_operation_method(func))

            # 特殊ケース: abs_values関数をabsという名前でも使えるようにする
            if name == "abs_values":
                setattr(self, "abs", self._create_operation_method(func))

        if self._domain != "core":
            domain_ops = OperationRegistry.get_operations(self._domain)
            for name, func in domain_ops.items():
                setattr(self, name, self._create_operation_method(func))

    def _wrap_result(self, result: Any, func_name: str) -> Any:
        """結果を適切にラップして返すヘルパーメソッド"""
        # 結果がColumnCollectionのリストであれば、CollectionListOperationsを作成
        if (
            isinstance(result, list)
            and result
            and all(isinstance(item, ColumnCollection) for item in result)
        ):
            from .list_proxy import CollectionListOperations

            return CollectionListOperations(result, self._domain)

        # 結果がColumnCollectionであれば、新しいプロキシを作成 (チェーン継続)
        elif isinstance(result, ColumnCollection):
            return CollectionOperations(result, self._domain)

        # それ以外（スカラ値、辞書、Noneなど）はラップせずにそのまま返す (チェーン終了)
        # 集計操作(max, minなど)や副作用(plot, to_csvなど)はこちらに該当する
        return result

    def _create_operation_method(self, func: Callable) -> Callable:
        """操作メソッドからメソッドを作成
        Args:
            func: 操作メソッド
        Returns:
            self._collectionを第一引数として呼び出すメソッド
        """

        def method(*args: Any, **kwargs: Any) -> Any:
            # 関数を実行し値を取得
            result = func(self._collection, *args, **kwargs)
            return self._wrap_result(result, func.__name__)

        # メソッドのドキュメントと名前を設定
        method.__name__ = func.__name__
        method.__doc__ = func.__doc__
        return method

    def end(self) -> T:
        """操作を終了し、ColumnCollectionを返す"""
        return self._collection

    def as_domain(self, domain: str, **kwargs: Any) -> "CollectionOperations":
        """現在のコレクションを指定されたドメインに変換
        Args:
            domain: 変換先のドメイン
            **kwargs: ドメインに渡す追加の引数
        Returns:
            CollectionOperations: 新しいCollectionOperationsオブジェクト
        """
        from tascpy.domains.factory import DomainCollectionFactory
        from tascpy.domains.converters import prepare_for_domain_conversion

        current_collection = self.end()

        # ドメイン変換準備
        prepared_collection, mod_kwargs = prepare_for_domain_conversion(
            current_collection, target_domain=domain, **kwargs
        )

        domain_collection = DomainCollectionFactory.from_collection(
            prepared_collection, domain, **mod_kwargs
        )
        return CollectionOperations(domain_collection, domain=domain)

    def pipe(self, func: Callable) -> "CollectionOperations":
        """関数を適用して新しいCollectionOperationsを作成
        Args:
            func: 適用する関数
        Returns:
            CollectionOperations: 新しいCollectionOperationsオブジェクト
        """
        new_collection = self._collection.apply(func)
        return CollectionOperations(new_collection, self._domain)

    def debug(self, message: Optional[str] = None) -> "CollectionOperations[T]":
        """デバッグメッセージを表示
        Args:
            message: デバッグメッセージ
        Returns:
            CollectionOperations: 自身を返す
        """
        if message:
            print(f"DEBUG: {message}")
        print(f"Collection: {self._collection}")
        print(f"Domain: {self._domain}")
        print(f"Columns: {self._collection.columns}")
        print(f"metadata: {self._collection.metadata}")
        return self

    # --- Collectionへの委譲メソッド ---

    def __len__(self) -> int:
        return len(self._collection)

    def __getitem__(self, key: Any) -> Any:
        return self._collection[key]

    def __iter__(self):
        return iter(self._collection)

    @property
    def columns(self) -> Dict[str, Any]:
        return self._collection.columns

    @property
    def step(self):
        return self._collection.step

    @property
    def metadata(self) -> Dict[str, Any]:
        return self._collection.metadata

    def __getattr__(self, name: str) -> Any:
        """その他の属性やメソッドをCollectionに委譲"""
        attr = getattr(self._collection, name)
        
        if callable(attr):
            def method(*args: Any, **kwargs: Any) -> Any:
                result = attr(*args, **kwargs)
                return self._wrap_result(result, name)
            
            method.__name__ = name
            method.__doc__ = attr.__doc__
            return method
            
        return attr

