# tascpy サンプル集

このディレクトリには、tascpy ライブラリの使用方法を示す様々なサンプルスクリプトが含まれています。
初心者から上級者まで、様々な習熟度に合わせたサンプルを提供しています。

## サンプルコレクション

1. **[basic](./basic/)** - 基本的な使い方
   - ColumnCollection の作成と操作
   - データアクセス、選択、フィルタリング
   - 数学的演算
   - データ変換と可視化
   - [詳細な説明を見る](./basic/README.md)

2. **[advance](./advance/)** - 高度な分析技法
   - 異常値の検出と処理
   - データのクリーニングと前処理
   - 複雑な可視化テクニック
   - [詳細な説明を見る](./advance/README.md)

3. **[domains](./domains/)** - ドメイン特化機能
   - 座標データ処理 (coordinate)
   - 荷重-変位分析 (load_displacement)
   - ドメイン間の変換と連携
   - [詳細な説明を見る](./domains/README.md)

4. **[jupyter](./jupyter/)** - Jupyter Notebook サンプル
   - インタラクティブなデータ分析
   - ウィジェットを活用した対話的な可視化
   - ノートブック形式での解析例
   - [詳細な説明を見る](./jupyter/README.md)

5. **[data](./data/)** - サンプルデータ
   - 基本的な分析用のサンプルCSVファイル
   - 荷重-変位分析用のサンプルデータ
   - テスト用データの生成スクリプト

## 学習の進め方

tascpy を効果的に学ぶためには、以下の順序でサンプルを進めることをおすすめします：

1. **基本を学ぶ** ([basic](./basic/))
   - まず `01_create_collection.py` から `05_math_operations.py` までの基本操作を理解する
   - 次に選択操作 (`04_select_operations.py`) とフィルタリング (`06_filter_search.py`) を学ぶ
   - データ変換と可視化の方法を `08_transform.py` と `09_visualization.py` で確認する

2. **高度な分析技法を習得する** ([advance](./advance/))
   - 異常値の検出と処理技術を `01_outlier_analysis_visualization.py` で学ぶ
   - 複雑なデータの前処理と可視化のパターンを理解する

3. **ドメイン特化機能に進む** ([domains](./domains/))
   - 興味のある分野（座標データまたは荷重-変位分析）のサンプルを確認する
   - ドメイン特化コレクションの作成と操作方法を学ぶ

4. **Jupyter Notebook での活用** ([jupyter](./jupyter/))
   - 対話的な環境での tascpy の使い方を学ぶ
   - 実際のデータを使った分析フローを体験する

## 実践的なワークフロー例

### シナリオ1: 計測データの前処理と可視化

```python
import matplotlib.pyplot as plt
import tascpy

# 1. CSVファイルからデータを読み込む
collection = tascpy.load("data.csv", format_name="csv")

# 2. 必要な列を選択し、データをクリーニング
clean_data = (
    collection.ops
    .select(columns=["Time", "Measurement"])
    .filter_out_none(columns=["Measurement"])  # 欠損値を除去
    .remove_outliers("Measurement", window_size=15, threshold=0.3)  # 外れ値を除去
    .end()
)

# 3. データ変換と処理
processed_data = (
    clean_data.ops
    .moving_average("Measurement", window_size=5, result_column="MA5")
    .evaluate("Measurement - MA5", result_column="Deviation")
    .end()
)

# 4. 結果の可視化
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

processed_data.plot.plot(y_column="Measurement", x_column="Time", ax=ax1, label="生データ", color="gray")
processed_data.plot.plot(y_column="MA5", x_column="Time", ax=ax1, label="5点移動平均", color="blue")
ax1.set_title("計測データと移動平均")
ax1.legend()

processed_data.plot.plot(y_column="Deviation", x_column="Time", ax=ax2, label="偏差", color="red")
ax2.axhline(y=0, color="black", alpha=0.3)
ax2.set_title("移動平均からの偏差")

plt.tight_layout()
plt.show()
```

### シナリオ2: 荷重-変位データの特性解析

```python
import matplotlib.pyplot as plt
import tascpy

# 1. データの読み込みと荷重-変位ドメインへの変換
collection = tascpy.load("load_displacement_data.csv", format_name="csv")
ld_ops = collection.ops.as_load_displacement(load_column="Force", displacement_column="Displacement")

# 2. 特性解析（初期剛性、降伏点）
analysis_result = (
    ld_ops
    .calculate_stiffness(range_start=0.1, range_end=0.5)  # 結果は results["stiffness"]
    .find_yield_point(method="offset", offset_value=0.002)  # 結果は results["yield_point"]
    .end()
)
stiffness = analysis_result.results["stiffness"].value
yield_point = analysis_result.results["yield_point"]

# 3. 可視化（降伏点・初期剛性線・オフセット線を描画）
fig, ax = plt.subplots(figsize=(10, 8))
analysis_result.plot.plot_yield_point(
    yield_disp=yield_point.x,
    yield_load=yield_point.y,
    yield_method="offset",
    initial_slope=yield_point.metadata.get("initial_slope", stiffness),
    ax=ax,
)
plt.show()

# 4. 結果の出力
print(f"初期剛性: {stiffness:.2f} kN/mm")
print(f"降伏荷重: {yield_point.y:.2f} kN")
print(f"降伏変位: {yield_point.x:.2f} mm")
print(f"最大荷重: {analysis_result['Force'].max():.2f} kN")
```

## 補足情報

### プロットのカスタマイズ

すべての可視化メソッドは Matplotlib のパラメータをサポートしているため、プロットを細かくカスタマイズできます：

```python
collection.plot.plot(
    y_column="Value",
    x_column="Time",
    x_label="X軸ラベル",   # X軸ラベル
    y_label="Y軸ラベル",   # Y軸ラベル
    marker="o",           # 以下は matplotlib の plot にそのまま渡されます
    linestyle="--",
    alpha=0.7,
    color="tab:blue",
)
```

### エラーハンドリング

tascpy の操作でエラーが発生した場合は、わかりやすいエラーメッセージが表示されます。一般的なエラーとその対処法：

- **列名の誤り**: `KeyError: "列 'column_name' が存在しません"` → 正しい列名を確認してください
- **ゼロ除算**: `ValueError: ゼロによる除算が発生しました` → `filter_by_condition()` で分母が 0 の行を除いてください
- **データ欠損**: 欠損値は計算時に NaN として扱われます。行ごと除く場合は `filter_out_none()` を使用してください

## サンプルデータ

サンプルスクリプトで使用されるデータは `data` ディレクトリに格納されています：

- `sample.csv` - 基本サンプル用の汎用データ
- `load_displacement_sample.csv` - 荷重-変位分析用のデータ

また、各サンプルスクリプトは、データファイルが存在しない場合に自動的に模擬データを生成するよう設計されています。

## 学習の進め方

tascpy の学習には、以下の順序でサンプルを進めることをお勧めします：

1. まず、`basic` ディレクトリのサンプルから開始し、tascpy の基本的な使い方を理解する
2. 次に、必要に応じて `domains` ディレクトリの特定ドメインのサンプルを参照する
3. 最後に、`advance` ディレクトリの高度な分析手法を学ぶ

各サンプルファイルは独立して実行可能で、以下のようにコマンドラインから実行できます：

```bash
python basic/01_create_collection.py
```

## 実践的なワークフロー例

tascpy の実際の使用シナリオを示す実践的なワークフロー例：

```python
import tascpy

# 1. データ読み込み
collection = tascpy.load("sample.csv", format_name="csv")

# 2. データ前処理（選択、欠損除去、重複除去）
ld_ops = (
    collection.ops
    .select(columns=["Time", "Force", "Displacement"])  # 必要な列のみ選択
    .filter_out_none()  # 欠損を含む行を除外
    .remove_consecutive_duplicates_across()  # 連続する重複行を除外
    # 3. ドメイン特化コレクションへの変換
    .as_load_displacement(load_column="Force", displacement_column="Displacement")
)

# 4. 分析と計算
result = (
    ld_ops
    .calculate_stiffness(range_start=0.1, range_end=0.5)
    .find_yield_point(method="offset", offset_value=0.002)
    .end()
)

# 5. 可視化と結果確認
result.plot.plot_load_displacement(marker="o", linestyle="-")

yield_point = result.results["yield_point"]
print(f"剛性: {result.results['stiffness'].value:.2f} kN/mm")
print(f"降伏荷重: {yield_point.y:.2f} kN")
print(f"降伏変位: {yield_point.x:.2f} mm")
```

## ヘルプとドキュメント

各サンプルコードにはドキュメント文字列が含まれており、関数やクラスの詳細な使用方法を確認できます。さらに詳しい情報は、[tascpy ドキュメント](../docs) を参照してください。

## 機能リクエストとバグ報告

tascpy の機能リクエストやバグ報告は、プロジェクトの GitHub リポジトリのイシュートラッカーで受け付けています。
