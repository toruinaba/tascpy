from typing import Dict, Callable, Optional, Any, Type
from ..core.collection import ColumnCollection


def create_column_collection(**kwargs: Any) -> ColumnCollection:
    """汎用的なカラムコレクションを作成するファクトリ関数
    Args:
        **kwargs: カラムコレクションの初期化に必要な引数
    Returns:
        ColumnCollection: 作成されたカラムコレクション
    """
    return ColumnCollection(**kwargs)


class DomainCollectionFactory:
    """ドメイン特化コレクションを作成するファクトリークラス"""

    # ドメイン名 -> ファクトリ関数の辞書
    _factories: Dict[str, Callable] = {"core": create_column_collection}

    @classmethod
    def register(cls, domain: str, factory_func: Callable) -> None:
        """ドメイン特化コレクションのファクトリを登録
        Args:
            domain: ドメイン名
            factory_func: ファクトリ関数
        """
        cls._factories[domain] = factory_func

    @classmethod
    def create(cls, domain: str, **kwargs: Any) -> ColumnCollection:
        """ドメイン特化コレクションを作成
        Args:
            domain: ドメイン名
            **kwargs: ファクトリ関数に渡す引数
        Returns:
            ColumnCollection: 作成されたコレクション
        """
        if domain not in cls._factories:
            raise ValueError(f"ドメイン'{domain}'のファクトリが登録されていません")

        factory_func = cls._factories[domain]
        return factory_func(**kwargs)

    @classmethod
    def from_collection(
        cls, collection: ColumnCollection, domain: str, **kwargs: Any
    ) -> ColumnCollection:
        """既存のコレクションからドメイン特化コレクションを作成
        Args:
            collection: 元のColumnCollection
            domain: ドメイン名
            **kwargs: ファクトリ関数に渡す引数
        Returns:
            ColumnCollection: 作成されたコレクション
        """
        if domain not in cls._factories:
            raise ValueError(f"ドメイン'{domain}'のファクトリが登録されていません")

        factory_func = cls._factories[domain]
        return factory_func(
            step=collection.step.clone(),
            columns={
                name: column.clone() for name, column in collection.columns.items()
            },
            metadata=collection.metadata.copy(),
            **kwargs,
        )

    @classmethod
    def get_available_domains(cls) -> Dict[str, str]:
        """登録されているドメインのリストを取得
        Returns:
            Dict[str, str]: ドメイン名とその説明の辞書
        """
        return {domain: f"Factory for {domain}" for domain in cls._factories.keys()}
