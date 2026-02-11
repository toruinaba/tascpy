# 実装計画 - コアストレージのNumPy化 (Status: Proposed)

## 目標
`DataHolder` および `Column` クラスの内部データ保持構造を Python リストから NumPy 配列 (`np.ndarray`) に変更し、メモリ効率と演算速度を向上させます。また、これに伴い不要となる操作関数の型変換処理を削除します。

## 変更内容

### 1. コアクラスの変更
#### [MODIFY] [src/tascpy/core/data_holder.py](file:///Users/inaba_toru/Developer/prjs/tascpy/src/tascpy/core/data_holder.py)
- `values` を `np.ndarray` として保持するように変更。
- `__init__` で入力を `np.array` に変換。
- データアクセス時のオーバーヘッドを最小化。

#### [MODIFY] [src/tascpy/core/column.py](file:///Users/inaba_toru/Developer/prjs/tascpy/src/tascpy/core/column.py)
- `NumberColumn`: `dtype=float` を強制し、`None` を `np.nan` として扱う。
- `StringColumn`: `dtype=object` (または `str` / `U`) を使用。
- `Column` (Generic): `dtype=object` を使用して柔軟性を維持（`None`保持）。
- `count_nones`, `max`, `mean` 等のメソッドを NumPy の高速な実装 (`np.isnan`, `np.nanmax`, `np.nanmean` 等) に置き換え。

#### [MODIFY] [src/tascpy/core/step.py](file:///Users/inaba_toru/Developer/prjs/tascpy/src/tascpy/core/step.py)
- `find_step_index` を `np.searchsorted` や `np.isclose` を使用した実装に変更。

### 2. オペレーションの最適化 (冗長な変換の削除)
ベースオブジェクトが既に NumPy 配列であることを前提に、各オペレーション内の `np.array()` 変換を削除または簡素化します。

#### [MODIFY] [src/tascpy/utils/data.py](file:///Users/inaba_toru/Developer/prjs/tascpy/src/tascpy/utils/data.py)
- 引数が既に `np.ndarray` であることを期待（または許容）し、再変換を避ける。
- `None` チェックを `np.isnan` チェックに変更（数値データの場合）。

#### [MODIFY] [src/tascpy/operations/core/math.py](file:///Users/inaba_toru/Developer/prjs/tascpy/src/tascpy/operations/core/math.py)
- `add`, `subtract` 等での `v1_arr = np.array(...)` を削除し、直接演算を行う。
- `evaluate` における名前空間への追加ロジックを簡素化。

#### [MODIFY] [src/tascpy/operations/core/stats.py](file:///Users/inaba_toru/Developer/prjs/tascpy/src/tascpy/operations/core/stats.py)
- `detect_outliers` での配列変換を削除。

#### [MODIFY] [src/tascpy/operations/core/transform.py](file:///Users/inaba_toru/Developer/prjs/tascpy/src/tascpy/operations/core/transform.py)
- `sin`, `cos` 等での配列変換を削除。

## 互換性とテスト
- `NumberColumn` が `None` の代わりに `NaN` を返すようになるため、既存のテスト (`test_core.py`) が `v is None` を期待している箇所で失敗する可能性があります。
- テストコードも `np.isnan(v)` を許容するように修正するか、`NumberColumn` のプロパティアクセサで `NaN` -> `None` 変換を行う（互換性維持のためには後者が安全だが、パフォーマンスの恩恵が減る）。
- **方針**: 内部データは `NaN` で保持するが、外部インターフェース（`values` プロパティのgetter以外、あるいは取得時）での扱いは慎重に行う。
    - パフォーマンス優先のため、`values` は `ndarray` をそのまま返す。
    - 既存テストを修正して `NaN` 対応を行う。

## 検証
- 既存の全テストパスを確認。
- `test_numerical_refactoring.py` の再実行。
