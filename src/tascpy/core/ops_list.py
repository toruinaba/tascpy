"""複数コレクションの操作 (`split_*` の戻り値)"""

from __future__ import annotations

from numbers import Number
from typing import Any, Callable, Dict, Generic, Iterator, List, Optional, Sequence, Tuple, TypeVar, Union, overload

import numpy as np

from tascpy.core.collection import ColumnCollection, concat

from .ops import CoreOps
from .result import PointResult, ScalarResult

O = TypeVar("O", bound=CoreOps[Any])
O2 = TypeVar("O2", bound=CoreOps[Any])
T = TypeVar("T")


def _cells(name: str, value: Any) -> List[Tuple[str, Any, Optional[str]]]:
    """to_table の関数の戻り値を (列名, 値, 単位) の並びにする"""
    if isinstance(value, ScalarResult):
        return [(name, value.value, value.unit)]
    if isinstance(value, PointResult):
        return [(f"{name}_x", value.x, value.x_unit), (f"{name}_y", value.y, value.y_unit)]
    if value is None or isinstance(value, (Number, np.generic)):
        return [(name, value, None)]
    raise TypeError(f"to_table の '{name}' の戻り値 ({type(value).__name__}) は使えません"
                    "（スカラー・ScalarResult・PointResult のいずれか）")


def _step(key: Any) -> Any:
    return int(key) if isinstance(key, float) and key.is_integer() else key


class OpsList(Generic[O]):
    """操作オブジェクトのリスト（各要素は分割のキーを持つ）

    Examples:
        >>> parts = col.ops.split_by_integers([1, 1, 1, 2, 2, 2])
        >>> parts.keys
        [1, 2]
        >>> smoothed = parts.map(lambda o: o.moving_average("荷重", result_column="荷重_平滑"))
        >>> parts.collect(lambda o: o.end()["荷重"].max())
        [80.0, 115.0]
    """

    def __init__(self, items: List[O], keys: Optional[Sequence[Any]] = None) -> None:
        self._items = list(items)
        self._keys = list(range(len(self._items))) if keys is None else [_step(k) for k in keys]
        if len(self._keys) != len(self._items):
            raise ValueError(f"キーの数 ({len(self._keys)}) が要素の数 ({len(self._items)}) と一致しません")

    @property
    def keys(self) -> List[Any]:
        """各要素の分割のキー（`split_by_integers` ならマーカーの値、`split_at_indices` なら区間の番号）"""
        return list(self._keys)

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[O]:
        return iter(self._items)

    @overload
    def __getitem__(self, index: int) -> O: ...
    @overload
    def __getitem__(self, index: slice) -> OpsList[O]: ...
    def __getitem__(self, index: Union[int, slice]) -> Union[O, OpsList[O]]:
        if isinstance(index, slice):
            return OpsList(self._items[index], self._keys[index])
        return self._items[index]

    def __repr__(self) -> str:
        return f"<OpsList len={len(self)}>"

    def map(self, func: Callable[[O], O2]) -> OpsList[O2]:
        """各要素に操作を適用し、チェーンを継続します"""
        return OpsList([func(item) for item in self._items], self._keys)

    def collect(self, func: Callable[[O], T]) -> List[T]:
        """各要素に関数を適用し、結果をリストで返します"""
        return [func(item) for item in self._items]

    def filter(self, predicate: Callable[[Any], bool]) -> OpsList[O]:
        """predicate(collection) が True の要素だけを残します"""
        kept = [(item, key) for item, key in zip(self._items, self._keys) if predicate(item.end())]
        return OpsList([item for item, _ in kept], [key for _, key in kept])

    def to_table(self, **columns: Callable[[O], Any]) -> CoreOps[ColumnCollection]:
        """各要素を 1 行に集約した表を返します（ステップは分割のキー）

        columns の各関数は要素の操作オブジェクトを受け取り、スカラー、ScalarResult（単位付きの 1 列）、
        PointResult（"{名前}_x" / "{名前}_y" の 2 列）のいずれかを返します。
        同じ関数は全要素で同じ種類・同じ単位の値を返す必要があります。

        Raises:
            ValueError: columns を指定しない場合、要素が空の場合、要素によって単位が異なる場合、列名が重なる場合
            TypeError: 関数が使えない値を返した場合、要素によって戻り値の種類が異なる場合

        Examples:
            >>> table = col.ops.split_by_integers([1, 1, 1, 2, 2, 2]).to_table(
            ...     max_load=lambda o: o.end()["荷重"].max(), rows=lambda o: len(o.end()))
            >>> table.end().step.tolist(), table.end()["max_load"].values
            ([1, 2], array([ 80., 115.]))
        """
        if not columns:
            raise ValueError("集約する列を指定してください")
        if not self._items:
            raise ValueError("集約する要素がありません")
        values: Dict[str, List[Any]] = {}
        units: Dict[str, Optional[str]] = {}
        for name, func in columns.items():
            layout: Optional[List[Tuple[str, Optional[str]]]] = None
            for item, key in zip(self._items, self._keys):
                cells = _cells(name, func(item))
                current = [(column, unit) for column, _, unit in cells]
                if layout is None:
                    layout = current
                    for column, unit in layout:
                        if column in values:
                            raise ValueError(f"to_table の列名 '{column}' が重なっています")
                        values[column], units[column] = [], unit
                elif [c for c, _ in current] != [c for c, _ in layout]:
                    raise TypeError(f"to_table の '{name}' の戻り値の種類が要素によって異なります（キー {key}）")
                elif current != layout:
                    raise ValueError(f"to_table の '{name}' の単位が要素によって異なります"
                                     f"（{[u for _, u in layout]} とキー {key} の {[u for _, u in current]}）")
                for column, value, _ in cells:
                    values[column].append(value)
        return CoreOps(ColumnCollection(values, step=self._keys, units=units, metadata=self._items[0].end().metadata))

    def end(self) -> List[Any]:
        """コレクションのリストを返します"""
        return [item.end() for item in self._items]

    def concat(self) -> O:
        """全コレクションを行方向に連結します（存在しない列は欠損で埋めます）

        Raises:
            ValueError: 要素が空の場合
        """
        if not self._items:
            raise ValueError("連結するコレクションがありません")
        return self._items[0]._next(concat(self.end()))
