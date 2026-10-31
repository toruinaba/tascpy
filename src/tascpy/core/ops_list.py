"""複数コレクションの操作 (`split_*` の戻り値)"""

from __future__ import annotations

from numbers import Number
from typing import Any, Callable, Dict, Generic, Iterator, List, Optional, Sequence, Tuple, TypeVar, Union, overload

import numpy as np

from tascpy.core.collection import ColumnCollection, concat

from .ops import CoreOps
from .result import PointResult, ScalarResult
from .row import Row

O = TypeVar("O", bound=CoreOps[Any])
O2 = TypeVar("O2", bound=CoreOps[Any])
T = TypeVar("T")


def _cells(name: str, value: Any) -> List[Tuple[str, Any, Optional[str]]]:
    """集約した値を (列名, 値, 単位) の並びにする"""
    if isinstance(value, ScalarResult):
        return [(name, value.value, value.unit)]
    if isinstance(value, PointResult):
        return [(f"{name}_x", value.x, value.x_unit), (f"{name}_y", value.y, value.y_unit)]
    if value is None or isinstance(value, (Number, np.generic)):
        return [(name, value, None)]
    raise TypeError(f"to_table にできない値です ({type(value).__name__})。"
                    "スカラー・ScalarResult・PointResult・Row のいずれかを集めてください")


def _step(key: Any) -> Any:
    return int(key) if isinstance(key, float) and key.is_integer() else key


class Collected(List[T], Generic[T, O]):
    """`OpsList.collect` の結果（各要素の値のリスト。分割のキーと元のコレクションを持つ）

    `to_table` で 1 要素 1 行の表にできます。
    """

    def __init__(self, values: List[T], keys: List[Any], sources: List[ColumnCollection]) -> None:
        super().__init__(values)
        self._keys = list(keys)
        self._sources = list(sources)

    @property
    def keys(self) -> List[Any]:
        """各要素の分割のキー"""
        return list(self._keys)

    @overload
    def to_table(self: Collected[Row, O2], name: None = None) -> O2: ...
    @overload
    def to_table(self, name: str) -> CoreOps[ColumnCollection]: ...
    def to_table(self, name: Optional[str] = None) -> Any:
        """1 要素 1 行の表を返します（ステップは分割のキー）

        - Row を集めた場合: 元の列名・単位の列と、元の行のステップ "source_step" 列。元のドメインを引き継ぎます（name は指定しない）
        - スカラー・ScalarResult・PointResult を集めた場合: name が必須。ScalarResult は単位付きの 1 列、
          PointResult は "{name}_x" / "{name}_y" の 2 列です。複数の値の表は `join` で横に並べます

        Raises:
            ValueError: 要素が空の場合、name の指定が値の種類と合わない場合、要素によって列や単位が異なる場合
            TypeError: 表にできない値の場合、要素によって値の種類が異なる場合

        Examples:
            >>> parts = col.ops.split_by_integers([1, 1, 1, 2, 2, 2])
            >>> parts.collect(lambda o: o.end()["荷重"].max()).to_table(name="max_load").end()["max_load"].values
            array([ 80., 115.])
            >>> peaks = parts.collect(lambda o: o.nearest_row("荷重", 100.0)).to_table().end()
            >>> peaks.step.tolist(), peaks["荷重"].values, peaks["source_step"].values
            ([1, 2], array([ 80., 100.]), array([3., 4.]))
        """
        if not self:
            raise ValueError("集約する要素がありません")
        is_row = [isinstance(value, Row) for value in self]
        if all(is_row):
            if name is not None:
                raise ValueError("Row を集めた表は元の列名を使うため、name は指定しません")
            return self._row_table()
        if any(is_row):
            raise TypeError("Row と他の値が混ざっています")
        if name is None:
            raise ValueError("表の列名 name を指定してください")
        return self._value_table(name)

    def _value_table(self, name: str) -> CoreOps[ColumnCollection]:
        layout = [(column, unit) for column, _, unit in _cells(name, self[0])]
        values: Dict[str, List[Any]] = {column: [] for column, _ in layout}
        for value, key in zip(self, self._keys):
            cells = _cells(name, value)
            current = [(column, unit) for column, _, unit in cells]
            if [c for c, _ in current] != [c for c, _ in layout]:
                raise TypeError(f"値の種類が要素によって異なります（キー {key}）")
            if current != layout:
                raise ValueError(f"単位が要素によって異なります（{[u for _, u in layout]} とキー {key} の "
                                 f"{[u for _, u in current]}）")
            for column, cell, _ in cells:
                values[column].append(cell)
        return CoreOps(ColumnCollection(values, step=self._keys, units=dict(layout),
                                        metadata=self._sources[0].metadata))

    def _row_table(self) -> CoreOps[Any]:
        rows: List[Row] = list(self)  # type: ignore[arg-type]
        source = self._sources[0]
        names = list(rows[0].units)
        if "source_step" in names:
            raise ValueError("元のコレクションに 'source_step' 列があるため、行の表を作れません")
        for row, key, src in zip(rows, self._keys, self._sources):
            if list(row.units) != names or row.units != rows[0].units:
                raise ValueError(f"行の列または単位が要素によって異なります（キー {key}）")
            if type(src) is not type(source) or src._domain_config() != source._domain_config():
                raise ValueError(f"元のコレクションのドメインの設定が要素によって異なります（キー {key}）")
        table = ColumnCollection(
            {**{n: [row[n] for row in rows] for n in names}, "source_step": [row.step for row in rows]},
            step=self._keys, meta={n: source.meta[n] for n in names}, units={"source_step": ""},
            metadata=source.metadata,
        )
        if type(source) is not ColumnCollection:
            table = type(source)._from_config(table, source._domain_config())
        return table.ops


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

    def collect(self, func: Callable[[O], T]) -> Collected[T, O]:
        """各要素に関数を適用し、結果をリスト（`Collected`）で返します

        `stiffness` / `yield_point` / `nearest_row` などの値への集約を要素ごとに求めるときに使います。
        結果は `to_table` で 1 要素 1 行の表にできます。
        """
        return Collected([func(item) for item in self._items], self._keys, [item.end() for item in self._items])

    def filter(self, predicate: Callable[[Any], bool]) -> OpsList[O]:
        """predicate(collection) が True の要素だけを残します"""
        kept = [(item, key) for item, key in zip(self._items, self._keys) if predicate(item.end())]
        return OpsList([item for item, _ in kept], [key for _, key in kept])

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
