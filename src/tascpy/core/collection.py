"""ColumnCollection: 単位などの列メタデータ付きの不変な表"""

from __future__ import annotations

import copy
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Dict, Iterable, Iterator, List, Mapping, Optional, Self, Sequence, Type, TypeVar, Union

import numpy as np
import polars as pl

from .column import KEEP, Column, ColumnMeta, to_series
from .result import AnalysisResult
from .row import Row

if TYPE_CHECKING:
    from .ops import CoreOps
    from .io.proxy import CollectionIO
    from .plot.plotter import CorePlotter

INDEX_COLUMNS = ("step", "date", "time")

_DOMAINS: Dict[str, type["ColumnCollection"]] = {}

C = TypeVar("C", bound="ColumnCollection")


def _index_series(name: str, values: Any) -> pl.Series:
    if isinstance(values, pl.Series):
        return values.alias(name)
    if isinstance(values, np.ndarray) and values.dtype.kind == "f":
        return pl.Series(name, values, nan_to_null=True)
    return pl.Series(name, list(values), strict=False)


def _check_data_name(name: str) -> None:
    if name in INDEX_COLUMNS:
        raise ValueError(f"'{name}' はインデックス列の予約名のため、データ列名には使えません")


class ColumnCollection:
    """列メタデータ（単位・チャンネル・属性）付きの不変な表

    データは polars の DataFrame に、列メタデータは `ColumnMeta` として別に保持します。
    変更操作はすべて新しいコレクションを返します。

    Examples:
        >>> coll = ColumnCollection({"P": [0.0, 10.0], "d": [0.0, 1.0]}, step=[1, 2], units={"P": "kN", "d": "mm"})
        >>> coll["P"].unit
        'kN'
        >>> coll2 = coll.with_column("P2", coll["P"].values * 2, unit="kN")
    """

    domain: str = "core"

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if "domain" in cls.__dict__:
            _DOMAINS[cls.domain] = cls

    def __init__(
        self,
        columns: Optional[Mapping[str, Any]] = None,
        *,
        step: Any = None,
        date: Any = None,
        time: Any = None,
        units: Optional[Mapping[str, Optional[str]]] = None,
        meta: Optional[Mapping[str, ColumnMeta]] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> None:
        """
        Args:
            columns: {列名: 値の並び または Column}
            step: ステップ値（省略時は 0..n-1）
            date: 日付（任意）
            time: 時刻（任意）
            units: {列名: 単位}（Column で渡したメタを上書き）
            meta: {列名: ColumnMeta}（Column で渡したメタを上書き）
            metadata: コレクション全体のメタデータ
        """
        series: List[pl.Series] = []
        metas: Dict[str, ColumnMeta] = {}
        for name, values in (columns or {}).items():
            _check_data_name(name)
            series.append(to_series(name, values))
            metas[name] = values.meta if isinstance(values, Column) else ColumnMeta()

        n_rows = len(series[0]) if series else (len(step) if step is not None else 0)
        index = [_index_series("step", step if step is not None else range(n_rows))]
        index += [_index_series(n, v) for n, v in (("date", date), ("time", time)) if v is not None]
        for s in index + series:
            if len(s) != n_rows:
                raise ValueError(f"列 '{s.name}' の長さ ({len(s)}) が行数 ({n_rows}) と一致しません")

        for name, m in (meta or {}).items():
            self._require(name, metas)
            metas[name] = m
        for name, unit in (units or {}).items():
            self._require(name, metas)
            metas[name] = metas[name].updated(unit=unit)

        self._set(pl.DataFrame(index + series), metas, dict(metadata or {}), {})

    @classmethod
    def from_frame(
        cls,
        df: pl.DataFrame,
        *,
        step: Optional[str] = None,
        units: Optional[Mapping[str, Optional[str]]] = None,
        meta: Optional[Mapping[str, ColumnMeta]] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Self:
        """polars の DataFrame から作成する

        Args:
            df: 元データ（"step" / "date" / "time" 列はインデックス列として扱う）
            step: ステップとして使う列名（省略時は "step" 列、なければ 0..n-1）
        """
        if step is not None:
            if "step" in df.columns and step != "step":
                raise ValueError("df に 'step' 列があるため、別の列を step に指定できません")
            df = df.rename({step: "step"})
        index = {n: df[n] for n in INDEX_COLUMNS if n in df.columns}
        columns = {n: df[n] for n in df.columns if n not in INDEX_COLUMNS}
        return cls(columns, step=index.get("step"), date=index.get("date"), time=index.get("time"),
                   units=units, meta=meta, metadata=metadata)

    # ── 内部 ──────────────────────────────────

    def _set(self, df: pl.DataFrame, meta: Dict[str, ColumnMeta],
             metadata: Dict[str, Any], results: Dict[str, AnalysisResult]) -> None:
        self._df = df
        self._meta = meta
        self._metadata = metadata
        self._results = results

    def _replace(self, *, df: Optional[pl.DataFrame] = None, meta: Optional[Dict[str, ColumnMeta]] = None,
                 metadata: Optional[Dict[str, Any]] = None,
                 results: Optional[Dict[str, AnalysisResult]] = None, validate: bool = True) -> Self:
        """一部を差し替えた新しいコレクション（ドメイン固有の属性は引き継ぐ）"""
        new = copy.copy(self)
        new._set(
            self._df if df is None else df,
            dict(self._meta) if meta is None else meta,
            dict(self._metadata) if metadata is None else metadata,
            dict(self._results) if results is None else results,
        )
        if validate:
            new._validate()
        return new

    # jedi（marimo の補完）は組み込みの type[C] を解釈できないため typing.Type を使う
    def _as_class(self, cls: Type[C]) -> C:
        """同じデータを持つ別クラス（ドメイン）のコレクション。ドメイン固有の属性は引き継がない"""
        new = cls.__new__(cls)
        new._set(self._df, dict(self._meta), dict(self._metadata), dict(self._results))
        return new

    def _validate(self) -> None:
        """ドメインごとの不変条件の検証（サブクラスで拡張）"""

    def _apply_rename(self, mapping: Mapping[str, str]) -> None:
        """列名の変更をドメイン固有の設定に反映する（サブクラスで拡張、構築中のコピーにのみ呼ばれる）"""

    def _domain_config(self) -> Dict[str, Any]:
        """ドメイン固有の設定（from_collection のキーワード引数として復元できる形、サブクラスで拡張）"""
        return {}

    @classmethod
    def _from_config(cls, collection: "ColumnCollection", config: Mapping[str, Any]) -> Self:
        """`_domain_config()` の内容からこのクラスのコレクションを復元する（サブクラスで拡張）"""
        return collection._as_class(cls)

    @staticmethod
    def _require(name: str, names: Iterable[str]) -> None:
        if name not in names:
            raise KeyError(f"列 '{name}' が存在しません")

    # ── アクセサ ───────────────────────────────

    @property
    def ops(self) -> "CoreOps[Self]":
        """メソッドチェーンで演算・抽出を行う操作オブジェクト (例: `coll.ops.add("A", "B", result_column="合計").end()`)"""
        from .ops import CoreOps

        return CoreOps(self)

    @property
    def plot(self) -> "CorePlotter":
        """可視化を行うプロッター (例: `coll.plot.plot("CH1")`)"""
        from .plot.plotter import CorePlotter

        return CorePlotter(self)

    @property
    def io(self) -> "CollectionIO":
        """ファイル入出力 (例: `coll.io.to_csv("out.csv")`)"""
        from .io.proxy import CollectionIO

        return CollectionIO(self)

    # ── 読み取り ───────────────────────────────

    @property
    def df(self) -> pl.DataFrame:
        """インデックス列とデータ列を含む DataFrame"""
        return self._df

    @property
    def meta(self) -> Mapping[str, ColumnMeta]:
        return MappingProxyType(self._meta)

    @property
    def metadata(self) -> Mapping[str, Any]:
        return MappingProxyType(self._metadata)

    @property
    def results(self) -> Mapping[str, AnalysisResult]:
        return MappingProxyType(self._results)

    @property
    def columns(self) -> List[str]:
        """データ列名のリスト"""
        return list(self._meta)

    @property
    def units(self) -> Dict[str, Optional[str]]:
        return {name: m.unit for name, m in self._meta.items()}

    @property
    def step(self) -> np.ndarray:
        return self._df["step"].to_numpy()

    @property
    def date(self) -> Optional[np.ndarray]:
        return self._df["date"].to_numpy() if "date" in self._df.columns else None

    @property
    def time(self) -> Optional[np.ndarray]:
        return self._df["time"].to_numpy() if "time" in self._df.columns else None

    @property
    def shape(self) -> tuple[int, int]:
        return len(self), len(self._meta)

    def __len__(self) -> int:
        return self._df.height

    def __contains__(self, name: object) -> bool:
        return name in self._meta

    __iter__ = None  # 列名と行のどちらを反復するか曖昧なため、iter_rows() を使う

    def __getitem__(self, key: Union[str, int, slice]) -> Any:
        """`coll["列名"]` → Column、`coll[i]` → Row、`coll[a:b]` → ColumnCollection"""
        if isinstance(key, str):
            if key not in self._meta:
                hint = f"（インデックス列は coll.{key} で取得します）" if key in INDEX_COLUMNS else ""
                raise KeyError(f"列 '{key}' が存在しません{hint}")
            return Column._wrap(self._df[key], self._meta[key])
        if isinstance(key, (int, np.integer)):
            n = len(self)
            if not -n <= key < n:
                raise IndexError(f"行インデックス {key} が範囲外です（行数 {n}）")
            return Row(self._df.row(int(key), named=True), self._meta)
        if isinstance(key, slice):
            return self._replace(df=self._df[key])
        raise TypeError(f"キーは列名・整数・スライスのいずれかで指定してください: {type(key)}")

    def by_ch(self, ch: str) -> Column:
        """チャンネル名で列を取得する"""
        for name, m in self._meta.items():
            if m.ch == ch:
                return self[name]
        raise KeyError(f"チャンネル '{ch}' の列が存在しません")

    def iter_rows(self) -> Iterator[Row]:
        for values in self._df.iter_rows(named=True):
            yield Row(values, self._meta)

    def step_index(self, value: Any, tolerance: Optional[float] = None) -> Optional[int]:
        """step が value と一致する（tolerance 指定時は許容誤差内で最も近い）行のインデックス"""
        steps = self.step
        if tolerance is None:
            hits = np.flatnonzero(steps == value)
            return int(hits[0]) if len(hits) else None
        diff = np.abs(steps.astype(float) - value)
        idx = int(np.nanargmin(diff)) if len(diff) else None
        return idx if idx is not None and diff[idx] <= tolerance else None

    def nearest_step_index(self, value: float) -> Optional[int]:
        """step が value に最も近い行のインデックス（行がなければ None）"""
        if len(self) == 0:
            return None
        return int(np.nanargmin(np.abs(self.step.astype(float) - value)))

    def describe(self) -> Dict[str, Dict[str, Any]]:
        """各データ列の概要（件数・欠損数・単位、数値列は統計量も）"""
        stats: Dict[str, Dict[str, Any]] = {}
        for name in self._meta:
            col = self[name]
            info: Dict[str, Any] = {"dtype": str(col.dtype), "unit": col.unit,
                                    "count": len(col), "null_count": col.null_count()}
            if col.is_numeric:
                info.update(mean=col.mean(), std=col.std(), min=col.min(), max=col.max())
            stats[name] = info
        return stats

    def __repr__(self) -> str:
        names = self.columns
        shown = [f"{n} [{self._meta[n].unit}]" if self._meta[n].unit else n for n in names[:6]]
        if len(names) > 6:
            shown.append(f"... ({len(names)} total)")
        results = f" results={list(self._results)}" if self._results else ""
        return f"<{type(self).__name__} rows={len(self)} columns=[{', '.join(shown)}]{results}>"

    # ── 変更（新しいコレクションを返す） ─────────────

    def with_column(self, name: str, values: Any, *, unit: Any = KEEP, ch: Any = KEEP, attrs: Any = KEEP) -> Self:
        """列を追加または上書きする（上書き時、指定しなかったメタは引き継ぐ）"""
        _check_data_name(name)
        series = to_series(name, values)
        if len(series) != len(self):
            raise ValueError(f"列 '{name}' の長さ ({len(series)}) が行数 ({len(self)}) と一致しません")
        meta = dict(self._meta)
        base = meta.get(name, ColumnMeta())
        if isinstance(values, Column) and name not in meta:
            base = values.meta
        meta[name] = base.updated(unit=unit, ch=ch, attrs=attrs)
        return self._replace(df=self._df.with_columns(series), meta=meta)

    def with_meta(self, name: str, *, unit: Any = KEEP, ch: Any = KEEP, attrs: Any = KEEP) -> Self:
        """列メタを変更する"""
        self._require(name, self._meta)
        meta = dict(self._meta)
        meta[name] = meta[name].updated(unit=unit, ch=ch, attrs=attrs)
        return self._replace(meta=meta)

    def with_attrs(self, name: str, **items: Any) -> Self:
        """列メタの attrs に項目を追加・上書きする"""
        self._require(name, self._meta)
        return self.with_meta(name, attrs={**self._meta[name].attrs, **items})

    def with_metadata(self, **items: Any) -> Self:
        """コレクションのメタデータに項目を追加・上書きする"""
        return self._replace(metadata={**self._metadata, **items})

    def with_result(self, result: AnalysisResult) -> Self:
        """解析結果を追加・上書きする"""
        return self._replace(results={**self._results, result.name: result})

    def select(self, names: Sequence[str]) -> Self:
        """指定したデータ列だけを残す（インデックス列は常に残る）"""
        for name in names:
            self._require(name, self._meta)
        index = [n for n in INDEX_COLUMNS if n in self._df.columns]
        return self._replace(df=self._df.select(index + list(names)),
                             meta={n: self._meta[n] for n in names})

    def drop(self, *names: str) -> Self:
        for name in names:
            self._require(name, self._meta)
        return self.select([n for n in self._meta if n not in names])

    def rename(self, mapping: Mapping[str, str]) -> Self:
        for old, new in mapping.items():
            self._require(old, self._meta)
            _check_data_name(new)
        meta = {mapping.get(n, n): m for n, m in self._meta.items()}
        new = self._replace(df=self._df.rename(dict(mapping)), meta=meta, validate=False)
        new._apply_rename(mapping)
        new._validate()
        return new

    def take(self, rows: Any) -> Self:
        """行インデックスの並び、または行数と同じ長さのブールマスクで行を抽出する"""
        selector = np.asarray(rows)
        if selector.dtype == bool:
            if len(selector) != len(self):
                raise ValueError(f"マスクの長さ ({len(selector)}) が行数 ({len(self)}) と一致しません")
            return self._replace(df=self._df.filter(pl.Series(selector)))
        indices = selector.astype(np.int64).ravel()
        n = len(self)
        if len(indices) and (indices.max() >= n or indices.min() < -n):
            raise IndexError("指定されたインデックスが範囲外です")
        return self._replace(df=self._df.select(pl.all().gather(indices)))

    def head(self, n: int = 5) -> Self:
        return self._replace(df=self._df.head(n))

    def tail(self, n: int = 5) -> Self:
        return self._replace(df=self._df.tail(n))


def concat(collections: Sequence[ColumnCollection]) -> ColumnCollection:
    """行方向に連結する（存在しない列は欠損で埋め、メタ・設定は最初に現れたものを使う）"""
    if not collections:
        raise ValueError("連結するコレクションがありません")
    meta: Dict[str, ColumnMeta] = {}
    for c in collections:
        for name, m in c.meta.items():
            meta.setdefault(name, m)
    df = pl.concat([c.df for c in collections], how="diagonal_relaxed")
    index = [n for n in INDEX_COLUMNS if n in df.columns]
    return collections[0]._replace(df=df.select(index + list(meta)), meta=meta)


def domain_class(name: str) -> type[ColumnCollection]:
    """ドメイン名に対応するコレクションのクラス（`domain` を定義したサブクラスは定義時に登録される）

    Raises:
        ValueError: ドメインが登録されていない場合
    """
    if name == ColumnCollection.domain:
        return ColumnCollection
    if name not in _DOMAINS:
        raise ValueError(f"ドメイン '{name}' が登録されていません（ドメインを定義するモジュールを import してください）")
    return _DOMAINS[name]
