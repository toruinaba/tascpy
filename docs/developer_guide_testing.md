# テスト戦略 (Testing Strategy)

tascpy は、数値計算の正確性と、データ操作パイプラインとしての振る舞いを分けてテストします。

## 1. テストディレクトリの構成

### `tests/unit/` (単体テスト)

1. **`numeric` テスト**: `tests/unit/numeric/`
   * 対象: `src/tascpy/numeric/` の純粋な数値計算関数
   * 目的: NumPy 配列を直接渡し、数学的に正しい値が返るかを検証します
   * 特徴: `ColumnCollection` は使いません。境界値や NaN などの入力パターンの網羅に集中し、`np.testing.assert_allclose` 等で検証します

2. **`ops` テスト**: `tests/unit/core/ops/`（汎用）、`tests/unit/domains/<ドメイン>/test_ops_*.py`
   * 対象: `src/tascpy/core/ops.py` と `src/tascpy/domains/<ドメイン>/ops.py` の操作クラス（`CoreOps` / `LoadDisplacementOps` / `CoordinateOps` / `StrainOps`）
   * 目的: コレクション上で操作が正しく連動するかを検証します
   * 特徴: 計算そのものの正確性ではなく、列名の解決、存在しない列での `KeyError`、欠損値の扱い、`result_column` への格納、単位・メタデータの引き継ぎ、元のコレクションが変更されないことなどに集中します

3. **その他**: `tests/unit/core/`（モデル・io・plot）、`tests/unit/domains/<ドメイン>/`（コレクション・描画）に各パッケージのテストがあります

### `tests/func/` (機能テスト)

「CSV を読み込み、フィルタリングし、移動平均をかけて描画する」といった、実際の使い方に沿った一連のメソッドチェーンを通しで検証します。

### `tests/typecheck/` (型チェック)

実行はせず、pyright で `assert_type` を検査します。メソッドチェーンの戻り値の型（IDE の補完）が崩れていないことを保証します。

### doctest（docstring の例とチュートリアル）

docstring の `Examples` と `docs/tutorial.md` は `pytest` で実行し、表示している結果を検査します（`pytest.ini` の `--doctest-modules` / `--doctest-glob`）。

- docstring の例は、`docs/api/sample_data.md` で定義する `col` / `ld` / `coord` / `strain` を使って書きます。ルートの `conftest.py` がこのページのコードブロックを実行して、doctest の名前空間に入れます。
- doctest は一時ディレクトリで実行します（サンプルを保存した `data.txt` が置いてあります）。ファイルを書く例でも作業ツリーは汚れません。
- 浮動小数点の値は期待値に書いた桁数で比較します（`NUMBER`）。例えば `100.0` と書けば `99.99999999999999` も一致とみなします。
- `.end()` だけで終わる例は出力が長くなるので、`.columns` や列の値など、確かめたい途中の結果を表示する形にします。

## 2. numeric と ops を分ける理由

数学的ロジックとデータハンドリングを分けることで、バグの場所を切り分けやすくするためです。

例えば `col.ops.average_columns(["A", "B"])` が失敗したとき、
* numeric のテストが落ちていれば、平均の計算そのものにバグがあります
* numeric は通り ops が落ちていれば、列の取り出しや欠損値の変換、結果の格納にバグがあります

## 3. テストの書き方

新しい操作（例: `my_new_calculation`）を追加する場合、2 段階でテストを書きます。

### ステップ1: numeric テスト

```python
# tests/unit/numeric/test_math.py
import numpy as np
from tascpy.numeric.math import my_new_calculation

def test_my_new_calculation():
    arr = np.array([1.0, 2.0, np.nan])
    np.testing.assert_allclose(my_new_calculation(arr), [2.0, 4.0, np.nan])
```

### ステップ2: ops テスト

```python
# tests/unit/core/ops/test_math.py
import numpy as np
import pytest

class TestMyNewCalculation:
    def test_basic(self, sample_collection):
        result = sample_collection.ops.my_new_calculation("A", result_column="calc").end()

        assert "calc" in result.columns
        np.testing.assert_allclose(result["calc"].values, [2.0, 4.0, 6.0, 8.0, 10.0])
        assert "calc" not in sample_collection.columns  # 元のコレクションは変更されない

    def test_missing_column(self, sample_collection):
        with pytest.raises(KeyError):
            sample_collection.ops.my_new_calculation("non_existent_column")
```

## 4. 実行方法

```bash
pytest
pyright   # 型チェック（設定は pyproject.toml）
```

## Tips

* **フィクスチャの活用**: 各テストでデータを長々と定義せず、既存の `sample_collection` などのフィクスチャを使ってください
* **モックは使わない**: 依存関係が少ないため、実際のデータオブジェクトを生成してテストします
