# tascpy 基本サンプル集

このディレクトリには、tascpy ライブラリの基本的な使い方を示すサンプルスクリプトが含まれています。それぞれのスクリプトは特定の機能に焦点を当て、実用的な例を通じて tascpy の基本的な操作方法を学ぶことができます。

## サンプルファイル一覧

### 1. データの作成と基本操作

1. **[01_create_collection.py](./01_create_collection.py)** - ColumnCollection オブジェクトの作成方法
   - 直接インスタンス化
   - 辞書からの作成
   - CSVファイルからの読み込み
   - NumPy 配列からの変換
   
   ```python
   # CSVファイルからのコレクション作成
   collection = ColumnCollection.from_file(
       filepath="sample.csv", format_name="csv", auto_detect_types=True
   )
   
   # 直接インスタンス化
   collection = ColumnCollection(
       step=steps,
       columns={
           "Force1": NumberColumn(ch="CH0", name="Force1", unit="kN", values=[0.0, 2.9, 2.9]),
           "Displacement1": NumberColumn(ch="CH2", name="Displacement1", unit="mm", values=[0.00, 0.08, 0.08])
       },
       metadata={"title": "無題"}
   )
   ```

2. **[02_data_access.py](./02_data_access.py)** - データアクセス方法
   - インデックス・列名を使ったアクセス
   - 値の取得と設定
   - メタデータの利用
   
   ```python
   # 列名によるアクセス
   force_values = collection["Force1"].values
   
   # インデックスによるアクセス
   step_3_data = collection[3]
   
   # メタデータアクセス
   test_title = collection.metadata.get("title", "")
   ```

3. **[03_column_operations.py](./03_column_operations.py)** - 列操作
   - 列の追加・削除・変更
   - 列名の変更と複製
   - データ型の変換
   
   ```python
   # 列操作の例
   # 新しい列の追加
   collection.add_column("ElapsedMinutes", elapsed_minutes)
   
   # カラムオブジェクトから新しい列を追加
   test_id_column = StringColumn(ch="ID", name="TestID", unit="", values=["A001", "A001", "B001", "B001", "B001"])
   collection.add_column("TestID", test_id_column)
   
   # 列の削除
   collection.remove_column("Displacement2")
   
   # チェーンメソッドを使った列操作
   result = (
       collection.clone()
       .add_column("ElapsedMinutes", elapsed_minutes)
       .remove_column("Displacement2")
   )
   ```

4. **[04_select_operations.py](./04_select_operations.py)** - データ選択操作
   - 行の選択（ステップ選択）
   - 列の選択
   - インデックスによる選択
   - 統合的な選択操作
   
   ```python
   # 行の選択
   step_selection = collection.ops.select(steps=[3, 4, 5]).end()
   
   # 列の選択
   column_selection = collection.ops.select(columns=["Force1", "Displacement1"]).end()
   
   # インデックスによる選択
   index_selection = collection.ops.select(indices=[0, 2, 4]).end()
   
   # チェーンメソッドを使った選択操作
   result = (
       ops.select(columns=["Force1", "Displacement1"], steps=[4, 6, 8, 10])
       .search_by_value("Displacement1", ">", 0)
       .divide("Force1", "Displacement1", result_column="Stiffness")
       .end()
   )
   ```

### 2. データ処理と変換

5. **[05_math_operations.py](./05_math_operations.py)** - 数学的操作
   - 基本四則演算（加算、減算、乗算、除算）
   - 式の評価
   - ステップによる選択と演算
   
   ```python
   # 数学的操作のチェーンメソッド例
   result = (
       collection.ops
       .add("Force1", 1.0)  # 値の加算
       .subtract("Force2", "Force1")  # 列同士の減算
       .multiply("Displacement1", 10)  # 値の乗算
       .divide("Force1", "Displacement1", handle_zero_division="none")  # 列同士の除算
       .end()
   )
   
   # 複合演算の例
   result = ops.add("Force1", "Force2", result_column="TotalForce").end()
   ```

6. **[06_filter_search.py](./06_filter_search.py)** - フィルタリングと検索
   - 条件に基づくフィルタリング
   - 関数を使ったフィルタリング
   - 特定パターンの検索
   - 値に基づく選択
   
   ```python
   # フィルタリング操作のチェーンメソッド例
   result = (
       collection.ops
       .search_by_value("Force1", ">", 5.0)  # 5.0より大きい値を選択
       .end()
   )
   ```

7. **[07_interpolate.py](./07_interpolate.py)** - データの補間
   - 線形補間

   
   ```python
   # 補間処理のチェーンメソッド例
   result = (
       collection.ops
       .interpolate(point_count=10, method="linear")  # 10点の線形補間
       .end()
   )
   ```

8. **[08_transform.py](./08_transform.py)** - データ変換
   - 正規化（最小-最大、Z-スコア）
   - 単位変換と物理量計算
   - 対数変換
   - 応力・ひずみ変換
   
   ```python
   # データ変換のチェーンメソッド例
   result = (
       collection.ops
       .normalize("Force1", method="minmax", result_column="NormalizedForce")  # 正規化
       .normalize("Force2", method="zscore", result_column="StandardizedForce")  # 標準化
       .log("Strain", base=math.e, result_column="LogStrain")  # 対数変換
       .end()
   )
   
   # 物理量計算の例
   physical_result = (
       full_converted.ops
       .divide("Force1_N", area_m2, result_column="Stress_Pa")  # 応力計算
       .divide("Stress_Pa", 1e6, result_column="Stress_MPa")  # 単位変換
       .divide("Displacement1_m", length_m, result_column="Strain")  # ひずみ計算
       .end()
   )
   ```

### 3. 高度な操作と可視化

9. **[09_visualization.py](./09_visualization.py)** - データの可視化
   - 散布図によるプロット
   - 線グラフによるプロット
   - データ選択と可視化の連携
   - Matplotlibとの連携
   
   ```python
   # 可視化の例（散布図）
   fig, ax = plt.subplots(figsize=(8, 5))
   (
       collection.ops.select(columns=["Displacement1", "Force1"])
       .plot(
           x_column="Displacement1",
           y_column="Force1",
           plot_type="scatter",
           label="試験体1",
           ax=ax,
       )
       .end()
   )
   
   # 線グラフプロットの例
   fig, ax = plt.subplots(figsize=(8, 5))
   (
       collection.ops.select(indices=list(range(0, len(collection), 2)))
       .plot(
           x_column="Displacement1",
           y_column="Force1",
           plot_type="line",
           color="blue",
           label="試験体1 (間引き)",
           marker="o",
           linestyle="-",
           linewidth=2,
           ax=ax,
       )
       .end()
   )
   ```

10. **[10_column_combine.py](./10_column_combine.py)** - 列の合成
    - ステップに基づく列の切り替え
    - 列の条件付き選択
    - 複数データのブレンド処理
    
    ```python
    # 列合成のチェーンメソッド例
    result = (
        collection.ops
        .switch_by_step(
            column1="sin_wave",
            column2="cos_wave",
            threshold=5.0,
            compare_mode="value",
            result_column="switch_at_5"
        )
        .blend_by_step(
            column1="sin_wave",
            column2="cos_wave",
            start=4.0,
            end=6.0,
            compare_mode="value",
            blend_method="linear",
            result_column="linear_blend"
        )
        .conditional_select(
            column1="sin_wave",
            column2="cos_wave",
            condition_column="condition",
            threshold=0.0,
            compare=">",
            result_column="conditional"
        )
        .end()
    )
    ```

11. **[11_stats_operations.py](./11_stats_operations.py)** - 統計処理
    - 基本統計量の計算（平均、標準偏差、最大値、最小値など）
    - 四分位数の計算
    - データのばらつき分析
    
    ```python
    # 基本統計量の計算例（カラムごとの統計量を直接取得）
    load_column = collection["Load"]
    
    # 個別の統計量の取得
    max_value = load_column.max()
    min_value = load_column.min()
    mean_value = load_column.mean()
    median_value = load_column.median()
    std_value = load_column.std()
    sum_value = load_column.sum()
    variance_value = load_column.variance()
    
    # 分位数の計算
    q1 = load_column.quantile(0.25)
    q3 = load_column.quantile(0.75)
    
    # 複数列の統計情報の取得
    for column_name in numeric_columns:
        column = collection[column_name]
        print(f"{column_name}の統計情報:")
        print(f"  平均値: {column.mean():.4f}")
        print(f"  中央値: {column.median():.4f}")
        print(f"  標準偏差: {column.std():.4f}")
    ```

## 使用方法

各サンプルファイルは独立して実行可能です。以下のように実行してください：

```bash
python 01_create_collection.py
```

サンプルファイルは番号順に学習を進めることをお勧めします。基本的な概念から始まり、徐々に高度なトピックへと進んでいきます。

## サンプルデータ

サンプルスクリプトでは、`examples/data` ディレクトリにあるサンプルデータファイルを使用しています。これらのファイルが存在しない場合、スクリプト内で模擬データが自動的に生成されます。

主なサンプルデータファイル：

- `sample.csv` - 一般的なサンプルデータ
- `load_displacement_sample.csv` - 荷重-変位分析用のサンプルデータ

## メソッドチェーンについて

tascpy の大きな特徴は、メソッドチェーンによるデータ処理です。これにより、複数の操作を連続して記述でき、コードの可読性と保守性が向上します。

### 基本的なチェーンパターン

```python
# 基本的なチェーンパターン
result = (
    collection.ops      # 操作の開始
    .add("Force1", 1.0)       # 最初の操作
    .multiply("Force1", 2.0)       # 2番目の操作
    .divide("Force1", "Displacement1")       # 3番目の操作
    .end()              # チェーンの終了と結果の取得
)
```

### result_columnパラメータの使用

多くの操作メソッドでは、`result_column` パラメータを指定することで新しいカラム名を設定できます：

```python
# result_columnパラメータを使った例
collection.ops.add("Force1", 10, result_column="Force1Plus10").end()
```

## 可視化結果

いくつかのサンプルでは、データの可視化結果が `examples/basic/imgs` ディレクトリに保存されます。サンプルスクリプトでは、グラフの表示とファイル保存の両方の例が含まれています。

例として生成されるプロット：
- 散布図と線グラフによる荷重-変位曲線
- 複数系列データの同一グラフへのプロット
- データ選択や前処理を施した結果の視覚化
- 試験体間の比較分析

09_visualization.py では、以下のようなグラフ表示手法を示しています：
```python
# 散布図と線グラフの組み合わせ例
fig, ax = plt.subplots(figsize=(8, 5))
(
    collection.ops.select(columns=["Displacement1", "Force1"])
    .plot(
        x_column="Displacement1",
        y_column="Force1",
        plot_type="scatter",
        label="試験体1",
        ax=ax,
    )
    .end()
)
```

## tascpy の特徴

これらのサンプルを通じて、tascpy の主要な特徴を学ぶことができます：

- **メソッドチェーン** - 複数の操作を連続して実行する効率的な方法
- **イミュータブルなデータ操作** - 元のデータを変更せず、新しいデータを生成
- **豊富なデータ処理関数** - 分析業務に役立つ幅広い関数群
- **直感的な可視化** - データを素早く視覚化する機能
- **型ヒントとサポート** - 開発環境での自動補完と型安全性
- **ドメイン特化機能** - 特定の分析ドメイン向けの特化機能

## 発展的な学習

基本サンプルに加えて、発展的なトピックについては以下のディレクトリを参照してください：

- `examples/advance` - 外れ値分析など高度な分析テクニック
- `examples/domains` - ドメイン特化機能のサンプル
  - `examples/domains/load_displacement` - 荷重-変位分析用の特化機能
  - `examples/domains/coordinate` - 座標データ処理用の特化機能

これらの発展的なサンプルでは、基本サンプルで学んだ技術を実際の分析シナリオに適用する方法を示しています。

## 実践的なワークフロー例

基本サンプルの知識を組み合わせた実践的なワークフロー例：

```python
# 実践的なデータ分析ワークフロー例
result = (
    collection.ops
    .select(columns=["Force1", "Force2", "Displacement1"])  # 必要な列の選択
    .add("Force1", "Force2", result_column="TotalForce")  # 合計荷重の計算
    .divide("TotalForce", "Displacement1", result_column="Stiffness")  # 剛性計算
    .end()
)
```
