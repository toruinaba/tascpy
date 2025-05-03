from .data_holder import DataHolder
from typing import List, Any, Optional, Dict, Union
from copy import deepcopy


class Column(DataHolder):
    """データ列を表すクラス"""

    def __init__(self, ch, name, unit, values=None, metadata=None):
        super().__init__(name, values, metadata)
        self.ch = ch
        self.unit = unit

    def clone(self):
        from copy import deepcopy

        return Column(self.ch, self.name, self.unit, deepcopy(self.values))

    def count_nones(self) -> int:
        """None値の数をカウント"""
        if self.values is None:
            return 0
        return sum(1 for value in self.values if value is None)

    def none_indices(self) -> List[int]:
        """None値を持つインデックスのリストを返す"""
        if self.values is None:
            return []
        return [i for i, value in enumerate(self.values) if value is None]

    def has_none(self) -> bool:
        """None値が1つ以上あるかどうかを返す"""
        if self.values is None:
            return False
        return any(value is None for value in self.values)


class NumberColumn(Column):
    """数値型データのみを格納するカラムクラス"""

    def __init__(self, ch, name, unit, values=None, metadata=None):
        # 値が数値型かどうか検証
        if values is not None:
            # Noneは許容するが、それ以外は数値型であることを確認
            self._validate_numeric_values(values)

        super().__init__(ch, name, unit, values, metadata)

    def _validate_numeric_values(self, values: List[Any]) -> None:
        """値が数値型かNoneであることを検証"""
        for i, value in enumerate(values):
            if value is not None and not isinstance(value, (int, float)):
                raise TypeError(
                    f"値はnumeric型またはNoneである必要があります。インデックス {i} の値: {value}"
                )

    def clone(self):
        """NumberColumnのクローンを作成"""
        return NumberColumn(
            self.ch,
            self.name,
            self.unit,
            deepcopy(self.values),
            deepcopy(self.metadata),
        )


class StringColumn(Column):
    """文字列型データのみを格納するカラムクラス"""

    def __init__(self, ch, name, unit, values=None, metadata=None):
        # 値が文字列型かどうか検証
        if values is not None:
            # Noneは許容するが、それ以外は文字列型であることを確認
            self._validate_string_values(values)

        super().__init__(ch, name, unit, values, metadata)

    def _validate_string_values(self, values: List[Any]) -> None:
        """値が文字列型かNoneであることを検証"""
        for i, value in enumerate(values):
            if value is not None and not isinstance(value, str):
                raise TypeError(
                    f"値はstring型またはNoneである必要があります。インデックス {i} の値: {value}"
                )

    def clone(self):
        """StringColumnのクローンを作成"""
        return StringColumn(
            self.ch,
            self.name,
            self.unit,
            deepcopy(self.values),
            deepcopy(self.metadata),
        )


class InvalidColumn(Column):
    """全ての値がNoneである無効な列を表すクラス"""

    def __init__(self, ch, name, unit, values=None, metadata=None):
        # 値がすべてNoneであることを確認
        if values is not None and any(value is not None for value in values):
            raise ValueError("InvalidColumnの全ての値はNoneである必要があります")

        super().__init__(ch, name, unit, values, metadata)

    def clone(self):
        """InvalidColumnのクローンを作成"""
        return InvalidColumn(
            self.ch,
            self.name,
            self.unit,
            deepcopy(self.values),
            deepcopy(self.metadata),
        )
