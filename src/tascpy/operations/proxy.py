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

from ..core.collection import ColumnCollection

if TYPE_CHECKING:
    from ..typing.proxy_base import CollectionOperationsBase
    from ..typing.core import CoreCollectionOperations
    from ..typing.load_displacement import LoadDisplacementCollectionOperations
    from ..typing.coordinate import CoordinateCollectionOperations


# ColumnCollectionおよびその派生クラス用のTypeVar
T = TypeVar("T", bound=ColumnCollection)


class CollectionOperations(Generic[T]):
    """ColumnCollectionの操作プロキシクラス, デコレーターパターンを使用"""

    def __init__(self, collection: T, domain: str = "core"):
        """
        Args:
            collection: ColumnCollectionオブジェクト
            domain: 操作のドメイン（デフォルトは"core"）
        """
        self._collection = collection
        self._domain = domain

        # スタブファイルが生成されていない場合、生成を試みる
        if TYPE_CHECKING:
            pass  # 型チェック時には何もしない
        else:
            from .registry import OperationRegistry

            OperationRegistry.generate_stubs()

        self._add_operations()

    def _add_operations(self) -> None:
        """操作メソッドを追加するためのメソッド"""
        from ..operations.registry import OperationRegistry

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

            # 結果がColumnCollectionのリストであれば、CollectionListOperationsを作成
            if (
                isinstance(result, list)
                and result
                and all(isinstance(item, ColumnCollection) for item in result)
            ):
                from .list_proxy import CollectionListOperations

                return CollectionListOperations(result, self._domain)

            # 結果がColumnCollectionであれば、新しいプロキシを作成
            elif isinstance(result, ColumnCollection):
                return CollectionOperations(result, self._domain)

            return result

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
        from ..domains.factory import DomainCollectionFactory
        from ..domains.converters import prepare_for_domain_conversion

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
