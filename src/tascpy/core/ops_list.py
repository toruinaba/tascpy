"""複数コレクションの操作 (`split_*` の戻り値)"""

from __future__ import annotations

from typing import Any, Callable, Generic, Iterator, List, TypeVar, Union, overload

from tascpy.core.collection import concat

from .ops import CoreOps

O = TypeVar("O", bound=CoreOps[Any])
O2 = TypeVar("O2", bound=CoreOps[Any])
T = TypeVar("T")


class OpsList(Generic[O]):
    """操作オブジェクトのリスト

    Examples:
        >>> parts = col.ops.split_by_integers([1, 1, 2, 2])
        >>> smoothed = parts.map(lambda o: o.moving_average("A"))
        >>> peaks = parts.collect(lambda o: o.end()["A"].max())
    """

    def __init__(self, items: List[O]) -> None:
        self._items = list(items)

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
            return OpsList(self._items[index])
        return self._items[index]

    def __repr__(self) -> str:
        return f"<OpsList len={len(self)}>"

    def map(self, func: Callable[[O], O2]) -> OpsList[O2]:
        """各要素に操作を適用し、チェーンを継続します"""
        return OpsList([func(item) for item in self._items])

    def collect(self, func: Callable[[O], T]) -> List[T]:
        """各要素に関数を適用し、結果をリストで返します"""
        return [func(item) for item in self._items]

    def filter(self, predicate: Callable[[Any], bool]) -> OpsList[O]:
        """predicate(collection) が True の要素だけを残します"""
        return OpsList([item for item in self._items if predicate(item.end())])

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
