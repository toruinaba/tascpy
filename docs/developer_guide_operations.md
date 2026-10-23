# 操作の追加方法

`collection.ops.xxx(...)` で呼び出す操作は、2 つの層で実装されています。

| 層 | 場所 | 役割 |
|---|---|---|
| functional | `src/tascpy/analytics/functional/` | NumPy 配列を受け取り配列・値を返す純粋関数。コレクションを知らない |
| ops | `src/tascpy/analytics/ops/` | コレクションから列を取り出し、functional を呼び、結果を格納した新しいコレクションを返すメソッド |

```text
col.ops.add("A", "B")
  └─ CoreOps.add()                       # ops 層: 列の解決・結果の格納
       └─ functional.core.math.add()     # functional 層: 計算のみ
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
col.ops.as_domain("load_displacement", ...)    # 汎用版（戻り値の型は CoreOps[Any]）
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

### 1. functional に純粋関数を書く

```python
# src/tascpy/analytics/functional/load_displacement/analysis.py
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

列を追加する操作であれば `_with_column` を使います。

```python
    def scale_load(self, factor: float, result_column: Optional[str] = None,
                   unit: Optional[str] = None) -> Self:
        """荷重を factor 倍した列を追加します"""
        load = self._c.load_column
        values = self._numeric(load) * factor
        return self._with_column(result_column or f"{load}*{factor}", values, unit,
                                 default_unit=self._unit_of(load))
```

### 3. テストを書く

functional 関数のテストと、ops メソッドのテストを分けて書きます。詳細は [テスト戦略](developer_guide_testing.md) を参照してください。

## ヘルパー一覧

`CoreOps` には操作の実装に使う内部ヘルパーがあります。`self._c` は対象のコレクションです。

| ヘルパー | 用途 |
|---|---|
| `_column_values(name)` | 列の値を取得（存在しなければ `KeyError`） |
| `_numeric(x)` | 列名・配列を float 配列に変換（`None` や `"*****"` などの欠損表記は NaN）。スカラーはそのまま |
| `_raw(x)` | 列名を値の配列に変換（数値変換はしない）。文字列列の比較などに使う |
| `_unit_of(x)` / `_first_unit(*xs)` | 列の単位を取得（結果列の単位を引き継ぐときに使う） |
| `_with_column(name, values, unit, ch, default_unit=)` | 結果を列として追加。同名列があれば値を上書き。NaN は `None` として格納 |
| `_with_rows(rows)` | 行インデックスまたはブールマスクで行を抽出 |
| `_with_result(result)` | `AnalysisResult`（`ScalarResult` など）を `results` に追加 |
| `_with_point(name, (is_valid, x, y, info))` | `PointResult` を追加（降伏点など） |
| `_with_curve(name, x, y)` | `XYSeriesResult` を追加（スケルトン曲線など） |
| `_split(row_groups)` | 行グループごとに分割して `OpsList` を返す |

どのヘルパーも元のコレクションを変更せず、複製に対して処理します。

## 新しいドメインを追加する

コレクションのサブクラスと、`CoreOps` のサブクラスを対で作ります。

```python
from typing import Self

from tascpy.analytics.ops import CoreOps
from tascpy.core.collection import ColumnCollection
from tascpy.domains.factory import DomainCollectionFactory


class TimeSeriesCollection(ColumnCollection):
    domain = "timeseries"

    @property
    def ops(self) -> "TimeSeriesOps":
        return TimeSeriesOps(self)


class TimeSeriesOps(CoreOps[TimeSeriesCollection]):
    def resample(self, frequency: str) -> Self:
        """リサンプリングします"""
        result = self._c.clone()
        result.metadata["frequency"] = frequency
        return self._next(result)


DomainCollectionFactory.register("timeseries", lambda **kw: TimeSeriesCollection(**kw))

col.ops.as_domain("timeseries").resample("1H").end()
```

`clone()` がサブクラスのインスタンスを返すように、必要に応じて `clone()` もオーバーライドしてください。ドメイン変換時の前処理が必要であれば、`tascpy.domains.converters.register_domain_converter` で変換関数を登録します。

## 型チェック

メソッドチェーンの型が崩れていないことは pyright で検査します。設定は `pyproject.toml` の `[tool.pyright]` にあり、`tests/typecheck/ops_chains.py` の `assert_type` が検査対象です。操作の戻り値の型を変えた場合は、このファイルも更新してください。

```bash
pip install pyright
pyright
```
