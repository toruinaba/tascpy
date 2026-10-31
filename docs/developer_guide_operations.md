# 操作の追加方法

`collection.ops.xxx(...)` で呼び出す操作は、2 つの層で実装されています。

| 層 | 場所 | 役割 |
|---|---|---|
| numeric | `src/tascpy/numeric/` | NumPy 配列を受け取り配列・値を返す純粋関数。コレクションを知らない |
| ops | `src/tascpy/core/ops.py`（汎用）、`src/tascpy/domains/<ドメイン>/ops.py` | コレクションから列を取り出し、numeric を呼び、結果を格納した新しいコレクションを返すメソッド |

```text
col.ops.add("A", "B", result_column="合計")
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

各コレクションの `ops` プロパティが対応するクラスを返します。操作は全て通常のメソッドとして定義されているため、IDE の補完と型チェックがそのまま効きます。

## 操作の種類と命名

操作は戻り値で分け、チェーンの流れが変わるものだけを名前で示します。

| 種類 | 戻り値 | 命名 | 例 |
|---|---|---|---|
| 変換（列を足す・行を絞る） | `Self`（チェーンが続く） | 動詞（印なし） | `add`、`select`、`mark_cycles` |
| ドメインの設定を外す | 別の Ops | `as_*` | `as_core` |
| ドメインのコレクションに変換する | コレクション（チェーンが終わる） | `end_as` | `end_as(as_load_displacement, ...)` |
| 新しい表への集約 | 別の Ops（新しい表でチェーンが続く） | `to_<名詞>` | `to_skeleton_curve`、`to_hysteresis_table`、`collect(...).to_table` |
| 値への集約 | 結果オブジェクトや値（チェーンが終わる） | 名詞 | `stiffness`、`yield_point`、`grid`、`nearest_row` |
| 分割 | `OpsList` | `split_*` | `split_by_cycles` |

- 値への集約は、データの 1 行を選ぶものは `Row`（`nearest_row`）、計算で値を作るものは結果オブジェクト（`ScalarResult` / `PointResult` など）を返します。
- 値への集約は結果を `results` に入れず、そのまま返します。保存したいときは呼び出し側が `with_result` で付けます（解析結果がデータの変更に追従しないため、自動では付けません）。
- 列や単位を推測しません。ドメインへの変換（`as_load_displacement` など）は使う列を必ず受け取り、サイクル列など他の操作が作った列も名前から探しません（省略時は既定の規則でその場で計算し、既存の列を使うときは列名を引数で受け取ります）。結果の単位が決められないときは `None`（不明）にし、呼び出し側が `unit=` で指定します。
- 列を足す操作は、結果の列名をキーワード専用の必須引数 `result_column` で受け取ります（複数の列を作る操作は接頭辞を必須にします）。操作の側で既定の列名は決めません。既存の列名を指定した場合は、意図した上書きとして扱います。
- 解析の条件はキーワード専用引数（`*` 以降）にします。
- plotter（`collection.plot`）は解析をしません。降伏点や外れ値の判定などは ops で求め、結果（`PointResult` や判定の列）を plotter に渡して描画します。

```python
point = (
    ld.ops
    .remove_consecutive_duplicates_across()   # 変換 (CoreOps)
    .to_skeleton_curve()                       # 新しい表 (LoadDisplacementOps)
    .yield_point(offset_value=0.5)             # 値 -> PointResult
)
```

ドメインへの変換は `end_as` に各ドメインの変換関数（`from_collection` の別名）を渡します。チェーンはそこで終わり、ドメインのコレクションが返ります。ドメインの操作は `.ops` で続けます。変換の引数も変換後の操作も、型チェックと補完が効きます。

```python
from tascpy.domains import as_coordinate, as_load_displacement, as_strain

col.ops.end_as(as_load_displacement, load_column="荷重", displacement_column="変位")  # -> LoadDisplacementCollection
col.ops.end_as(as_coordinate, coordinates={...})       # -> CoordinateCollection
col.ops.end_as(as_strain, rosettes={...})              # -> StrainCollection
ld.ops.as_core()                               # ドメインの設定を外す -> CoreOps
```

`split_by_integers` / `split_at_indices` / `split_by_cycles` は `OpsList` を返します。

```python
parts = ld.ops.split_by_cycles()
parts.map(lambda o: o.moving_average("荷重", result_column="荷重_平滑"))  # 各要素に操作を適用 -> OpsList
parts.collect(lambda o: o.end()["荷重"].max())    # 値のリスト
parts.collect(lambda o: o.stiffness())            # 結果オブジェクトのリスト（分割のキーを持つ）
parts.collect(lambda o: o.stiffness()).to_table(name="k")   # 1 要素 1 行の表 -> CoreOps（ステップは分割のキー）
parts.collect(lambda o: o.nearest_row("荷重", 100.0)).to_table()   # 行の表（元の列名・ドメインのまま）
table_a.join(table_b)                            # ステップが同じ表を横に並べる
parts.keys                                       # 分割のキー（サイクル番号など）
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
# src/tascpy/domains/load_displacement/ops.py
class LoadDisplacementOps(CoreOps[LoadDisplacementCollection]):
    ...

    def peak_load(self) -> ScalarResult:
        """最大荷重を求めます（単位は荷重の単位）"""
        value = compute_peak_load(self._c.load_data)
        return ScalarResult(name="peak_load", value=value, unit=self._c.load.unit)
```

列を追加する操作であれば `_with_column` を使います。結果の単位は、明示された `unit` がなければ `default_unit` になります。`default_unit` は [単位の方針](developer_guide_design.md#単位の方針) に従って決め、自明でなければ `None` にします。

```python
    def scale_load(self, factor: float, *, result_column: str,
                   unit: Optional[str] = None, ch: Optional[str] = None) -> Self:
        """荷重を factor 倍した列を追加します（単位は荷重の単位）"""
        load = self._c.load_column
        values = self._numeric(load) * factor
        return self._with_column(result_column, values, unit, ch, default_unit=self._unit_of(load))
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
| `_point(name, (is_valid, x, y, info), x_unit, y_unit)` | 計算結果を `PointResult` にする（降伏点など。is_valid は metadata に入る） |
| `_split(row_groups)` | 行グループごとに分割して `OpsList` を返す |

コレクションは不変なので、コレクションを返すヘルパーはどれも新しいコレクションを返します。

## 新しいドメインを追加する

`src/tascpy/domains/<ドメイン>/` にパッケージを作り、コレクションのサブクラス（`collection.py`）と `CoreOps` のサブクラス（`ops.py`）を対で置きます。core 側の変更は要りません（tascpy の外のパッケージでも同じように定義できます）。ドメイン固有の設定は属性として持ちます。属性は `with_*` などの操作で自動的に引き継がれます。不変条件は `_validate` で検査します（操作のたびに呼ばれます）。

```python
from typing import Any, Dict, Mapping, Self

import numpy as np

from tascpy.core import CoreOps
from tascpy.core.collection import ColumnCollection
from tascpy.core.result import ScalarResult


class TimeSeriesCollection(ColumnCollection):
    domain = "timeseries"

    @classmethod
    def from_collection(cls, collection: ColumnCollection, time_column: str) -> Self:
        new = collection._as_class(cls)
        new._time_column = time_column
        new._validate()
        return new

    def _validate(self) -> None:
        if self._time_column not in self:
            raise ValueError(f"列 '{self._time_column}' が存在しません")

    def _apply_rename(self, mapping) -> None:
        self._time_column = mapping.get(self._time_column, self._time_column)

    def _domain_config(self) -> Dict[str, Any]:
        return {"time_column": self._time_column}

    @classmethod
    def _from_config(cls, collection: ColumnCollection, config: Mapping[str, Any]) -> Self:
        return cls.from_collection(collection, **config)

    @property
    def ops(self) -> "TimeSeriesOps":
        return TimeSeriesOps(self)


class TimeSeriesOps(CoreOps[TimeSeriesCollection]):
    def sampling_interval(self) -> ScalarResult:
        """時刻列の間隔の中央値を求めます（値への集約なので結果を返す）"""
        time = self._c._time_column
        return ScalarResult("sampling_interval", float(np.median(np.diff(self._numeric(time)))),
                            unit=self._unit_of(time))
```

変換関数は `from_collection` の別名として公開します。`col.ops.end_as(as_timeseries, "t")` で変換でき、引数は `from_collection` のシグネチャで型検査されます。

```python
as_timeseries = TimeSeriesCollection.from_collection
```

- `domain` を定義したサブクラスは定義時にレジストリへ登録され、`_domain_config` / `_from_config` の組で Parquet に保存・復元できます。
- 描画が必要なら `plotter.py`（`CorePlotter` のサブクラス）と `draw.py`（描画関数）を置き、コレクションの `plot` プロパティの中で遅延インポートします（matplotlib を描画時にだけ読み込むため）。
- 他のドメインに依存する場合は、`pyproject.toml` の import-linter の契約に許可を追加します。

## 型チェック

メソッドチェーンの型が崩れていないことは pyright で検査します。設定は `pyproject.toml` の `[tool.pyright]` にあり、`tests/typecheck/ops_chains.py` の `assert_type` が検査対象です。操作の戻り値の型を変えた場合は、このファイルも更新してください。

```bash
pyright   # requirements-dev.txt に含まれています
```
