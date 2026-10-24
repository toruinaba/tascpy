# 操作の追加方法

`collection.ops.xxx(...)` で呼び出す操作は、2 つの層で実装されています。

| 層 | 場所 | 役割 |
|---|---|---|
| numeric | `src/tascpy/numeric/` | NumPy 配列を受け取り配列・値を返す純粋関数。コレクションを知らない |
| ops | `src/tascpy/analytics/ops/` | コレクションから列を取り出し、numeric を呼び、結果を格納した新しいコレクションを返すメソッド |

```text
col.ops.add("A", "B")
  └─ CoreOps.add()                       # ops 層: 列の解決・結果の格納
       └─ numeric.math.add()             # numeric 層: 計算のみ
```

## 操作クラス

| クラス | 対象コレクション | 主な操作 |
|---|---|---|
| `CoreOps` | `ColumnCollection` | 四則演算、微分・積分、抽出・除外、統計、列の合成、分割 |
| `LoadDisplacementOps(CoreOps)` | `LoadDisplacementCollection` | 剛性、降伏点、サイクル、スケルトン曲線など |
| `CoordinateOps(CoreOps)` | `CoordinateCollection` | 座標補間 |
| `StrainOps(CoordinateOps)` | `StrainCollection` | ロゼット解析、応力、降伏点（座標補間も利用可） |

各コレクションの `ops` プロパティが対応するクラスを返します。操作は全て通常のメソッドとして定義されているため、IDE の補完と型チェックがそのまま効きます。チェーンを続ける操作は `Self` を返し、`end()` でコレクションを取り出します。

```python
result = (
    ld.ops
    .remove_consecutive_duplicates_across()   # CoreOps の操作
    .cycle_count()                             # LoadDisplacementOps の操作
    .create_skeleton_curve()
    .end()                                     # -> LoadDisplacementCollection
)
```

ドメイン変換は型付きのメソッドを使うと、変換後の操作も補完されます。

```python
col.ops.as_load_displacement("荷重", "変位")   # -> LoadDisplacementOps
col.ops.as_coordinate(coordinates={...})       # -> CoordinateOps
col.ops.as_strain(rosettes={...})              # -> StrainOps
ld.ops.as_core()                               # ドメインの設定を外す -> CoreOps
```

`split_by_integers` / `split_at_indices` / `split_by_cycles` は `OpsList` を返します。

```python
parts = ld.ops.cycle_count().split_by_cycles()
parts.map(lambda o: o.find_yield_point())        # 各要素に操作を適用 -> OpsList
parts.collect(lambda o: o.end()["荷重"].max())    # 値のリスト
parts.filter(lambda c: len(c) > 10)              # コレクションで絞り込み
parts.concat()                                   # 連結 -> 操作オブジェクト
parts.end()                                      # コレクションのリスト
```

## 操作を追加する手順

### 1. numeric に純粋関数を書く

関数は解析の対象ごとのモジュールに置きます（x-y 曲線なら `curve.py`、繰り返し載荷なら `hysteresis.py`）。

```python
# src/tascpy/numeric/curve.py
def compute_peak_load(load_data: np.ndarray) -> float:
    """最大荷重を返します"""
    return float(np.nanmax(load_data))
```

### 2. 対応する Ops クラスにメソッドを書く

```python
# src/tascpy/analytics/ops/load_displacement.py
class LoadDisplacementOps(CoreOps[LoadDisplacementCollection]):
    ...

    def find_peak_load(self) -> Self:
        """最大荷重を求め、結果 "peak_load" に格納します"""
        value = compute_peak_load(self._c.load_data)
        return self._with_result(ScalarResult(name="peak_load", value=value))
```

列を追加する操作であれば `_with_column` を使います。結果の単位は、明示された `unit` がなければ `default_unit` になります。`default_unit` は [単位の方針](developer_guide_design.md#単位の方針) に従って決め、自明でなければ `None` にします。

```python
    def scale_load(self, factor: float, result_column: Optional[str] = None,
                   unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """荷重を factor 倍した列を追加します（単位は荷重の単位）"""
        load = self._c.load_column
        values = self._numeric(load) * factor
        return self._with_column(result_column or f"{load}*{factor}", values, unit, ch,
                                 default_unit=self._unit_of(load))
```

行の抽出・検索などの表操作は numeric に置かず、ops の中で polars の式やコレクションのメソッド（`take` / `select` など）で実装します。

### 3. テストを書く

numeric 関数のテストと、ops メソッドのテストを分けて書きます。詳細は [テスト戦略](developer_guide_testing.md) を参照してください。

## ヘルパー一覧

`CoreOps` には操作の実装に使う内部ヘルパーがあります。`self._c` は対象のコレクションです。

| ヘルパー | 用途 |
|---|---|
| `_column_values(name)` | 列の値を取得（存在しなければ `KeyError`） |
| `_numeric(x)` | 列名・配列を float 配列に変換（`None` や `"*****"` などの欠損表記は NaN）。スカラーはそのまま |
| `_raw(x)` | 列名を値の配列に変換（数値変換はしない）。文字列列の比較などに使う |
| `_unit_of(x)` / `_first_unit(*xs)` | 列の単位を取得（結果列の単位を引き継ぐときに使う） |
| `_scaled_unit(a, b)` / `_compound_unit(y, x, sep)` | 列×スカラーの単位 / `"y/x"` のような合成表記 |
| `_with_column(name, values, unit, ch, default_unit=)` | 結果を列として追加・上書き。NaN は欠損 (null) として格納 |
| `_with_rows(rows, **metadata)` | 行インデックスまたはブールマスクで行を抽出 |
| `_mask(expr)` | polars の式から行マスクを作る（欠損は False） |
| `_with_result(result)` | `AnalysisResult`（`ScalarResult` など）を `results` に追加 |
| `_with_point(name, (is_valid, x, y, info), x_unit, y_unit)` | `PointResult` を追加（降伏点など） |
| `_with_curve(name, x, y, x_unit, y_unit)` | `XYSeriesResult` を追加（スケルトン曲線など） |
| `_split(row_groups)` | 行グループごとに分割して `OpsList` を返す |

コレクションは不変なので、どのヘルパーも新しいコレクションを返します。

## 新しいドメインを追加する

コレクションのサブクラスと、`CoreOps` のサブクラスを対で作ります。ドメイン固有の設定は属性として持ちます。属性は `with_*` などの操作で自動的に引き継がれます。不変条件は `_validate` で検査します（操作のたびに呼ばれます）。

```python
from typing import Self

from tascpy.core import CoreOps
from tascpy.core.collection import ColumnCollection


class TimeSeriesCollection(ColumnCollection):
    domain = "timeseries"

    @classmethod
    def from_collection(cls, collection: ColumnCollection, time_column: str) -> "TimeSeriesCollection":
        new = collection._as_class(cls)
        new._time_column = time_column
        new._validate()
        return new

    def _validate(self) -> None:
        if self._time_column not in self:
            raise ValueError(f"列 '{self._time_column}' が存在しません")

    def _apply_rename(self, mapping) -> None:
        self._time_column = mapping.get(self._time_column, self._time_column)

    @property
    def ops(self) -> "TimeSeriesOps":
        return TimeSeriesOps(self)


class TimeSeriesOps(CoreOps[TimeSeriesCollection]):
    def mark_frequency(self, frequency: str) -> Self:
        return self._next(self._c.with_metadata(frequency=frequency))
```

変換メソッド（`as_timeseries` など）が必要なら `CoreOps` に追加します。

## 型チェック

メソッドチェーンの型が崩れていないことは pyright で検査します。設定は `pyproject.toml` の `[tool.pyright]` にあり、`tests/typecheck/ops_chains.py` の `assert_type` が検査対象です。操作の戻り値の型を変えた場合は、このファイルも更新してください。

```bash
pyright   # requirements-dev.txt に含まれています
```
