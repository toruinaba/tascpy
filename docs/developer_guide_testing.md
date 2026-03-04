# テスト戦略 (Testing Strategy)

tascpyは、数学的・科学的な処理の正確性と、データ操作パイプラインとしての柔軟性を両立させるため、明確に分離されたテストアーキテクチャを採用しています。

このガイドでは、tascpyにおけるテストの構造と、新しい機能を追加する際のテストの書き方について説明します。

---

## 1. テストディレクトリの構成

tascpyのテストは大きく2つのカテゴリ（ディレクトリ）に分かれています。

### `tests/unit/` (単体テスト)
各モジュールや関数の独立した動作を検証するためのテスト群です。さらに内部で役割が分かれています。

1. **`functional` テスト**: `tests/unit/analytics/functional/`
   *   対象: `src/tascpy/analytics/functional/` 配下の純粋な数値計算関数。
   *   目的: 入力された数値やNumPy配列に対して、数学的に正しい値が返ってくるかを検証します。
   *   特徴: `ColumnCollection` などの複雑なオブジェクトは一切使用せず、直接 `np.ndarray` を渡して `np.testing.assert_allclose` 等で検証します。境界値やNaNのような特殊な入力パターンの網羅に集中します。

2. **`operations` テスト**: `tests/unit/analytics/operations/`
   *   対象: `src/tascpy/analytics/operations/` 配下の登録済み操作と `register_functional` などのシステム。
   *   目的: `ColumnCollection` というデータ構造の上で、指定した操作（列の抽出、計算、新しい列としての保存）が正しく連動するかを検証します。
   *   特徴: ここでは純粋な計算処理の正確性（正しく足し算されているか等）ではなく、引数の自動展開（列名からデータへの解決）、エラーハンドリング（存在しない列名指定時の `KeyError`）、欠損値の自動ハンドリング、そして `result_column` への保存やメタデータの伝播が正しく行われるかに集中します。

### `tests/func/` (機能テスト / End-to-End)
「ユーザーがtascpyをどのように使うか」という実践的なシナリオに基づくテスト群です。
例えば、「CSVからデータを読み込み、特定の波形をフィルタリングし、移動平均をかけてグラフを描画する」といった一連の流れ（メソッドチェーン）が通しで動作するかを検証します。

---

## 2. ユニットテストの分離の意味

なぜ `functional` と `operations` でテストを分けるのでしょうか？

それは、**数学的ロジックの複雑さ**と**データハンドリングの複雑さ**を分離し、バグの特定を容易にするためです。

例えば、`col.ops.average_across("A", "with_none")` を実行したときにエラーが発生したとします。
*   もし `functional` のテストだけが落ちていれば、平均値を計算するNumPyの処理（数学的ロジック）にバグがあります。
*   もし `functional` のテストは通るのに `operations` のテストが落ちるなら、コレクションから列を抽出する処理や、自動的なNaN変換処理（`handle_missing_values` デコレータ等）の方にバグがあることが瞬時に切り分けられます。

この分離を維持することで、tascpyの堅牢性を保っています。

---

## 3. テストの書き方とベストプラクティス

新しい機能（例えば `my_new_calculation`）を追加する場合、以下の2ステップでテストを書きます。

### ステップ1: `functional` テストの作成

純粋な関数に対するテストです。

```python
# tests/unit/analytics/functional/core/test_math.py
import numpy as np
import pytest
from tascpy.analytics.functional.math import my_new_calculation

def test_my_new_calculation_functional():
    arr = np.array([1.0, 2.0, np.nan])
    
    # 正常系の計算テスト
    res = my_new_calculation(arr)
    np.testing.assert_allclose(res, [2.0, 4.0, np.nan])
    
    # 境界値やオプション引数のテスト
    res_strict = my_new_calculation(arr, strict=True)
    np.testing.assert_allclose(res_strict, [2.0, 4.0, 0.0])
```

### ステップ2: `operations` テストの作成

`ColumnCollection` との連動テストです。既存のテストファイルにある `sample_collection` フィクスチャを活用します。

```python
# tests/unit/analytics/operations/core/test_math.py
import pytest
import numpy as np
from tascpy.analytics.operations.core.math import my_new_calculation
from tascpy.core.collection import ColumnCollection

# (フィクスチャは通常ファイル上部に定義されています)
# @pytest.fixture
# def sample_collection(): ...

class TestMyNewCalculationOperation:
    """my_new_calculation関数の構造・連動テスト"""

    def test_my_new_calculation_basic(self, sample_collection):
        # 列名で指定して動作するか、結果が自動命名されるか
        result = my_new_calculation(sample_collection, "A", result_column="my_calc_result")
        
        # 新しい列が追加されたか
        assert "my_calc_result" in result.columns
        
        # 値の大まかな確認（詳細な数学的ロジックはfunctionalテストに任せる）
        np.testing.assert_allclose(result["my_calc_result"].values, [2.0, 4.0, 6.0, 8.0, 10.0])

    def test_my_new_calculation_missing_column(self, sample_collection):
        # 存在しないカラムを指定したとき、期待通り KeyError が出るか
        with pytest.raises(KeyError):
            my_new_calculation(sample_collection, "non_existent_column")
```

### Tips
*   **フィクスチャの活用**: `tests/unit/analytics/operations/` のテストでは、各テストの最初に長々とデータを定義するのではなく、予め用意された `sample_collection` や `ops`（メソッドチェーン用）フィクスチャを引き回して使ってください。
*   **モックは非推奨**: tascpyのテストでは、依存関係が少ないため極力モックを使用せず、実際のデータオブジェクトを生成してテストすることを推奨しています。
