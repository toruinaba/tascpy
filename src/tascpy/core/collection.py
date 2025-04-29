from typing import Dict, List, Any, Optional, Union, TypeVar, Callable
from .indices import Indices
from .column import Column

T = TypeVar("T")


class ColumnCollection:
    """複数のcollumnと一つのstepを保持するクラス"""

    def __init__(self, step, columns, metadata=None):
        """
        Args:
            step: Stepオブジェクトまたはステップ値のリスト
            columns: {名前: Column}の辞書または{名前: 値リスト}の辞書
            metadata: メタデータの辞書
        """
        # ステップの初期化
        if isinstance(step, Indices):
            self.step = step
        else:
            self.step = Indices(values=step if step is not None else [])

        # 列の初期化
        self.columns = {}
        if columns:
            for name, column in columns.items():
                if isinstance(column, Column):
                    self.columns[name] = column
                else:
                    self.columns[name] = Column(None, name, None, column)
        self.metadata = metadata if metadata is not None else {}

    def __len__(self) -> int:
        return len(self.step)

    def __getitem__(self, key):
        """キーに基づいてデータにアクセス
        Args:
            key: 列名またはインデックス(整数/スライス)

        Returns:
            列名の場合: 指定された列
            整数インデックスの場合: 指定された行のデータを含む辞書
            スライスの場合: 指定された行範囲を含む新しいColumnCollection

        Raises:
            KeyError: 指定された列名が存在しない場合
            TypeError: キーが文字列または整数/スライスでない場合
        """
        if isinstance(key, str):
            # 列名によるアクセス
            if key == "step":
                return self.step
            elif key in self.columns:
                return self.columns[key]
            else:
                raise KeyError(f"列'{key}'が存在しません")
        elif isinstance(key, (int, slice)):
            # インデックスによるアクセス
            if isinstance(key, int):
                # 単一行の場合
                if isinstance(key, int):
                    # 単一行の場合
                    values = {}
                    for name, column in self.columns.items():
                        values[name] = column.values[key]
                    from .row import Row

                    return Row(step=self.step.values[key], values=values)
            else:
                # スライスの場合は新しいColumnCollectionを返す
                new_step = Indices(values=self.step.values[key])
                new_columns = {}
                for name, column in self.columns.items():
                    new_column = column.clone()
                    new_column.values = column.values[key]  # スライス
                    new_columns[name] = new_column

                return ColumnCollection(
                    step=new_step, columns=new_columns, metadata=self.metadata.copy()
                )
        else:
            raise TypeError(
                f"キーは文字列または整数/スライスである必要があります: {type(key)}"
            )

    def clone(self):
        """コレクションのクローンを作成"""
        return ColumnCollection(
            step=self.step.clone(),
            columns={name: column.clone() for name, column in self.columns.items()},
            metadata=self.metadata.copy(),
        )

    def add_column(
        self, name: str, column: Union[Column, List[Any]]
    ) -> "ColumnCollection":
        """列を追加
        Args:
            name: 列名
            column: Columnオブジェクトまたは値のリスト

        Returns:
            self(メソッドチェーン用)
        """
        if name in self.columns:
            raise KeyError(f"列'{name}'はすでに存在します")
        if isinstance(column, Column):
            self.columns[name] = column
        else:
            self.columns[name] = Column(None, name, None, column)
        self.harmonize_length()
        return self

    def remove_column(self, name: str) -> "ColumnCollection":
        """列を削除
        Args:
            name: 列名

        Returns:
            self(メソッドチェーン用)
        """
        if name not in self.columns:
            raise KeyError(f"列'{name}'は存在しません")
        del self.columns[name]
        return self

    def harmonize_length(self) -> None:
        """列の長さをStepに合わせる"""
        for column in self.columns.values():
            if len(column) != len(self.step):
                raise ValueError(
                    f"列'{column.name}'の長さ({len(column)})がStepの長さ({len(self.step)})と一致しません"
                )
        # step, columnsの長さを揃える（ロジック実装次第追加予定）

    @property
    def ops(self):
        """操作プロキシクラスを返す"""
        from ..operations.proxy import CollectionOperations

        return CollectionOperations(self)

    @property
    def __repr__(self) -> str:
        """文字列表現"""
        return f"ColumnCollection(step={self.step}, columns={self.columns}, metadata={self.metadata})"

    def head(self, n: int = 5) -> "ColumnCollection":
        """最初のn行を取得
        Args:
            n: 行数

        Returns:
            ColumnCollection: 最初のn行を含む新しいColumnCollection

        Raises:
            ValueError: nが負の整数または列数を超える場合
        """
        if n < 0:
            raise ValueError("nは0以上の整数である必要があります")
        if n > len(self):
            raise ValueError(f"nは{len(self)}以下である必要があります")
        return self[:n]

    def tail(self, n: int = 5) -> "ColumnCollection":
        """最後のn行を取得
        Args:
            n: 行数

        Returns:
            ColumnCollection: 最後のn行を含む新しいColumnCollection

        Raises:
            ValueError: nが負の整数または列数を超える場合
        """
        if n < 0:
            raise ValueError("nは0以上の整数である必要があります")
        if n > len(self):
            raise ValueError(f"nは{len(self)}以下である必要があります")
        return self[-n:]

    def describe(self) -> Dict[str, Dict[str, Any]]:
        """データの概要を取得
        Returns:
            辞書: 各列の統計情報を含む辞書
        """
        stats = {}
        for name, column in self.columns.items():
            # columnが数値の場合は統計情報を計算
            if isinstance(column.values, (list, tuple)):
                stats[name] = {
                    "count": len(column.values),
                    "mean": sum(column.values) / len(column.values),
                    "min": min(column.values),
                    "max": max(column.values),
                }
            else:
                stats[name] = {"count": len(column.values)}
        return stats

    def apply(self, func: Callable[[List[Any]], List[Any]]) -> "ColumnCollection":
        """各Columnに関数を適用
        Args:
            func: 適用する関数
        Returns:
            ColumnCollection: 新しいColumnCollection
        """
        new_columns = {}
        for name, column in self.columns.items():
            new_columns[name] = column.apply(func)
        # 適用後長さが揃っているか確認
        self.harmonize_length()
        # 新しいColumnCollectionを返す
        return ColumnCollection(
            step=self.step,
            columns=new_columns,
            metadata=self.metadata.copy(),
        )
