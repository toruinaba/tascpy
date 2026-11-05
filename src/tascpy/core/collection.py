"""ColumnCollection: 単位などの列メタデータ付きの不変な表"""

from __future__ import annotations

import copy
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterable, Iterator, List, Mapping, Optional, Self, Sequence, Type, TypeVar, Union

import numpy as np
import polars as pl

from .column import KEEP, Column, ColumnMeta, to_series
from .names import missing_message, normalize
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


def _check_unique_channels(meta: Mapping[str, ColumnMeta]) -> None:
    """チャンネル名（None 以外）が列の間で重ならないこと"""
    owners: Dict[str, List[str]] = {}
    for name, m in meta.items():
        if m.ch is not None:
            owners.setdefault(m.ch, []).append(name)
    duplicated = {ch: names for ch, names in owners.items() if len(names) > 1}
    if duplicated:
        detail = ", ".join(f"'{ch}'（列 {names}）" for ch, names in duplicated.items())
        raise ValueError(f"チャンネル名が重複しています: {detail}"
                         "（列をコピーするときは with_column(..., ch=None) のようにチャンネル名を外してください）")


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
        _check_unique_channels(meta)
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
            raise KeyError(missing_message("列", name, ((n, repr(n), n) for n in names)))

    def _missing_column(self, name: str) -> KeyError:
        """列 name が見つからないときの KeyError（列名・チャンネル名から近い候補を添える）"""
        candidates = [(n, repr(n), n) for n in self._meta]
        candidates += [(m.ch, f"{n!r}（ch {m.ch!r}）", n) for n, m in self._meta.items() if m.ch]
        hint = f"（インデックス列は coll.{name} で取得します）" if name in INDEX_COLUMNS else ""
        return KeyError(missing_message("列", name, candidates) + hint)

    def _missing_ch(self, ch: str) -> KeyError:
        """チャンネル ch が見つからないときの KeyError（チャンネル名・列名から近い候補を添える）"""
        candidates = [(m.ch, repr(m.ch), n) for n, m in self._meta.items() if m.ch]
        candidates += [(n, f"{m.ch!r}（列 {n!r}）", n) for n, m in self._meta.items() if m.ch]
        return KeyError(missing_message("チャンネル", ch, candidates))

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
                raise self._missing_column(key)
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
        raise self._missing_ch(ch)

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

    def catalog(self) -> pl.DataFrame:
        """データ列の一覧表（1列を1行として、列の順に並べた DataFrame）

        列数が多いデータで、列の構成を確かめたり、条件に合う列を探したりするための表です。
        polars の式で絞り込み、`select` に渡して使います。

        | 列 | 内容 |
        |---|---|
        | `ch` / `name` / `unit` / `dtype` | チャンネル名・列名・単位・データ型 |
        | `n_valid` / `null_count` | 欠損でない値の数・欠損の数 |
        | `n_unique` | 欠損を除いた値の種類数（0 なら全欠損、1 なら定数。断線などの疑い） |
        | `min` / `max` / `abs_max` | 最小・最大・絶対値の最大（数値列のみ、それ以外は欠損） |
        | `abs_max_step` | 絶対値が最大になる行のステップ |
        | attrs のキー | 列メタの attrs の各項目（標準の列と同名のキーは `attrs.` を前に付ける） |

        読み込み時に列名を補ったり変えたりした列は、attrs の `raw_name` に元の名前（空欄なら ""）が入ります。

        Examples:
            >>> coll = ColumnCollection({"SG1": [0.0, 1500.0], "SG2": [0.0, 200.0], "SG3": [None, None]},
            ...                         units={"SG1": "με", "SG2": "με"})
            >>> cat = coll.catalog()
            >>> cat.filter(pl.col("n_unique") <= 1)["name"].to_list()    # 全欠損・定数の列
            ['SG3']
            >>> coll.select(cat.filter((pl.col("unit") == "με") & (pl.col("abs_max") > 1000))["name"]).columns
            ['SG1']
        """
        names = self.columns
        df = self._df
        numeric = [n for n in names if df[n].dtype.is_numeric()]

        def stat(expr: Any) -> Dict[str, Any]:
            if not numeric:
                return {}
            return df.select(expr(pl.col(n)).alias(n) for n in numeric).row(0, named=True)

        mins, maxs = stat(lambda e: e.min()), stat(lambda e: e.max())
        abs_maxs, abs_args = stat(lambda e: e.abs().max()), stat(lambda e: e.abs().arg_max())
        uniques = df.select(pl.col(n).drop_nulls().n_unique().alias(n) for n in names).row(0, named=True) if names else {}
        nulls = {n: df[n].null_count() for n in names}
        steps = df["step"]

        table: Dict[str, pl.Series] = {
            "ch": pl.Series("ch", [self._meta[n].ch for n in names], dtype=pl.String),
            "name": pl.Series("name", names, dtype=pl.String),
            "unit": pl.Series("unit", [self._meta[n].unit for n in names], dtype=pl.String),
            "dtype": pl.Series("dtype", [str(df[n].dtype) for n in names], dtype=pl.String),
            "n_valid": pl.Series("n_valid", [len(self) - nulls[n] for n in names], dtype=pl.Int64),
            "null_count": pl.Series("null_count", [nulls[n] for n in names], dtype=pl.Int64),
            "n_unique": pl.Series("n_unique", [uniques[n] for n in names], dtype=pl.Int64),
            "min": pl.Series("min", [mins.get(n) for n in names], dtype=pl.Float64),
            "max": pl.Series("max", [maxs.get(n) for n in names], dtype=pl.Float64),
            "abs_max": pl.Series("abs_max", [abs_maxs.get(n) for n in names], dtype=pl.Float64),
            "abs_max_step": pl.Series(
                "abs_max_step", [None if abs_args.get(n) is None else steps[abs_args[n]] for n in names],
                dtype=steps.dtype),
        }
        keys = dict.fromkeys(k for n in names for k in self._meta[n].attrs)
        for key in keys:
            label = f"attrs.{key}" if key in table else key
            table[label] = to_series(label, [self._meta[n].attrs.get(key) for n in names])
        return pl.DataFrame(list(table.values()))

    def find(
        self,
        text: Optional[str] = None,
        *,
        unit: Union[str, Sequence[str], None] = None,
        min_abs: Optional[float] = None,
        dead: Optional[bool] = None,
        where: Optional[Callable[[Column], bool]] = None,
    ) -> List[str]:
        """条件に合うデータ列の名前を、列の順に返す（条件はすべて満たすものだけ）

        結果は `select` に渡して使います。条件を指定しなければ全列を返します。

        Args:
            text: 列名・チャンネル名・attrs の値のいずれかに含まれる文字列
                （全角と半角、大文字と小文字、空白の違いは無視する）
            unit: 単位（複数指定するといずれか。全角と半角の違いは無視し、大文字と小文字は区別する）
            min_abs: 絶対値の最大がこの値以上の数値列（`catalog()` の `abs_max`）
            dead: True なら全欠損・定数の列、False ならそれ以外（`catalog()` の `n_unique` が 1 以下かどうか）
            where: 列（`Column`）を受け取って真偽を返す関数

        Examples:
            >>> coll = ColumnCollection({"SG1": [0.0, 1500.0], "SG2": [0.0, 200.0], "SG3": [None, None]},
            ...                         units={"SG1": "με", "SG2": "µε"})
            >>> coll.find(unit="με")                      # マイクロ記号の µε も一致する
            ['SG1', 'SG2']
            >>> coll.find("sg", min_abs=1000), coll.find(dead=True)
            (['SG1'], ['SG3'])
            >>> coll.select(coll.find(where=lambda c: c.max() is not None and c.max() > 100)).columns
            ['SG1', 'SG2']
        """
        names = self.columns
        if text is not None:
            target = normalize(text)
            names = [n for n in names if any(target in normalize(v) for v in self._search_texts(n))]
        if unit is not None:
            units = {normalize(u, casefold=False) for u in ([unit] if isinstance(unit, str) else unit)}
            names = [n for n in names
                     if self._meta[n].unit is not None and normalize(self._meta[n].unit, casefold=False) in units]
        if min_abs is not None or dead is not None:
            stats = {row["name"]: row for row in self.select(names).catalog().iter_rows(named=True)}
            if min_abs is not None:
                names = [n for n in names if stats[n]["abs_max"] is not None and stats[n]["abs_max"] >= min_abs]
            if dead is not None:
                names = [n for n in names if (stats[n]["n_unique"] <= 1) == dead]
        if where is not None:
            names = [n for n in names if where(self[n])]
        return names

    def _search_texts(self, name: str) -> List[str]:
        """`find(text=...)` で探す文字列（列名・チャンネル名・attrs の値）"""
        meta = self._meta[name]
        texts = [name] + ([meta.ch] if meta.ch else [])
        return texts + [str(v) for v in meta.attrs.values() if v is not None and v != ""]

    def __repr__(self) -> str:
        names = self.columns
        shown = [f"{n} [{self._meta[n].unit}]" if self._meta[n].unit else n for n in names[:6]]
        if len(names) > 6:
            shown.append(f"... ({len(names)} total)")
        results = f" results={list(self._results)}" if self._results else ""
        return f"<{type(self).__name__} rows={len(self)} columns=[{', '.join(shown)}]{results}>"

    # ── 変更（新しいコレクションを返す） ─────────────

    def with_column(self, name: str, values: Any, *, unit: Any = KEEP, ch: Any = KEEP, attrs: Any = KEEP) -> Self:
        """列を追加または上書きする

        上書き時は、指定しなかったメタを既存の列から引き継ぎます。新しい列に `Column` を渡した場合は、
        その `Column` のメタを引き継ぎます。チャンネル名は列の間で一意なので、同じ表の列をコピーするときは
        `ch=None` を指定してください。

        Raises:
            ValueError: 長さが行数と一致しない場合、チャンネル名が他の列と重なる場合

        Examples:
            >>> coll = ColumnCollection({"P": Column("P", [1.0, 2.0], unit="kN", ch="@1")})
            >>> coll.with_column("P_copy", coll["P"], ch=None)["P_copy"].unit
            'kN'
        """
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
