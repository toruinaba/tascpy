# tascpy サンプル集

このディレクトリには、tascpy ライブラリの使用方法を示す様々なサンプルスクリプトが含まれています。
初心者から上級者まで、様々な習熟度に合わせたサンプルを提供しています。

## サンプルコレクション

1. **[basic](./basic/)** - 基本的な使い方
   - ColumnCollection の作成と操作
   - データアクセス、選択、フィルタリング
   - 数学的演算と補間
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
# 1. CSVファイルからデータを読み込む
collection = ColumnCollection.from_file("data.csv", format_name="csv")

# 2. 必要な列を選択し、データをクリーニング
clean_data = (
    collection.ops
    .select(columns=["Time", "Measurement"])
    .filter_out_none(columns=["Measurement"])  # 欠損値を除去
    .detect_and_remove_outliers(
        column="Measurement", 
        window_size=15, 
        threshold=0.3
    )  # 外れ値を除去
    .end()
)

# 3. データ変換と処理
processed_data = (
    clean_data.ops
    .moving_average(column="Measurement", window_size=5, result_column="MA5")
    .evaluate("Measurement - MA5", result_column="Deviation")
    .end()
)

# 4. 結果の可視化
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# 生データと移動平均の比較
processed_data.ops.plot(
    x_column="Time", 
    y_column="Measurement", 
    ax=ax1, 
    label="生データ",
    color="gray",
    alpha=0.7
).end()

processed_data.ops.plot(
    x_column="Time", 
    y_column="MA5", 
    ax=ax1, 
    label="5点移動平均",
    color="blue",
    linewidth=2
).end()

ax1.set_title("計測データと移動平均")
ax1.legend()
ax1.grid(True)

# 偏差プロット
processed_data.ops.plot(
    x_column="Time", 
    y_column="Deviation", 
    ax=ax2, 
    label="偏差",
    color="red"
).end()

ax2.axhline(y=0, color="black", linestyle="-", alpha=0.3)
ax2.set_title("移動平均からの偏差")
ax2.set_xlabel("時間")
ax2.grid(True)

plt.tight_layout()
plt.show()
```

### シナリオ2: 荷重-変位データの特性解析

```python
# 1. データの読み込みと荷重-変位ドメインへの変換
collection = ColumnCollection.from_file("load_displacement_data.csv", format_name="csv")

ld_collection = collection.ops.as_domain(
    "load_displacement",
    load_column="Force",
    displacement_column="Displacement"
).end()

# 2. 特性解析（初期剛性、降伏点などの計算）
analysis_result = (
    ld_collection.ops
    .calculate_stiffness(range_start=0.1, range_end=0.5, result_column="InitialStiffness")
    .calculate_yield_point(method="offset", offset_ratio=0.002)
    .calculate_max_load(result_column="MaxLoad")
    .end()
)

# 3. 結果レポートの作成と可視化
fig, ax = plt.subplots(figsize=(10, 8))

# 荷重-変位曲線のプロット
analysis_result.ops.plot(
    x_column="Displacement", 
    y_column="Force", 
    ax=ax, 
    label="荷重-変位曲線",
    color="blue",
    linewidth=2
).end()

# 初期剛性線のプロット
yield_point = [
    analysis_result["YieldPoint_Displacement"].values[0],
    analysis_result["YieldPoint_Load"].values[0]
]

# 初期剛性直線の描画
stiffness = analysis_result["InitialStiffness"].values[0]
x_vals = np.linspace(0, yield_point[0] * 1.5, 100)
y_vals = stiffness * x_vals

ax.plot(x_vals, y_vals, linestyle="--", color="green", label=f"初期剛性: {stiffness:.2f} kN/mm")

# 降伏点のマーク
ax.scatter(yield_point[0], yield_point[1], color="red", s=100, marker="o", label=f"降伏点: ({yield_point[0]:.2f}, {yield_point[1]:.2f})")

# 0.2%オフセット線（必要に応じて）
offset_x = np.linspace(0.002, yield_point[0] * 1.5, 100)  # 0.2%オフセット
offset_y = stiffness * (offset_x - 0.002)
ax.plot(offset_x, offset_y, linestyle=":", color="purple", label="0.2%オフセット線")

ax.set_title("荷重-変位特性解析")
ax.set_xlabel("変位 (mm)")
ax.set_ylabel("荷重 (kN)")
ax.grid(True)
ax.legend()

plt.tight_layout()
plt.show()

# 4. 結果の出力
print(f"=== 解析結果 ===")
print(f"初期剛性: {analysis_result['InitialStiffness'].values[0]:.2f} kN/mm")
print(f"降伏荷重: {yield_point[1]:.2f} kN")
print(f"降伏変位: {yield_point[0]:.2f} mm")
print(f"最大荷重: {analysis_result['MaxLoad'].values[0]:.2f} kN")
```

## 補足情報

### スタブファイル生成

サンプルコードを実行する前に、IDE の自動補完を有効にするためにスタブファイルの生成を行うことをおすすめします：

```python
import tascpy  # 初回インポート時に自動的にスタブファイルが生成されます

# または手動で生成する場合：
from tascpy.operations.stub_generator import generate_stubs
generate_stubs()
```

### プロットのカスタマイズ

すべての可視化メソッドは Matplotlib のパラメータをサポートしているため、プロットを細かくカスタマイズできます：

```python
collection.ops.plot(
    x_column="Time", 
    y_column="Value",
    plot_type="scatter",  # 散布図
    marker="o",           # マーカースタイル
    s=50,                 # マーカーサイズ
    alpha=0.7,            # 透明度
    c="Value2",           # 色付けに使う列
    cmap="viridis",       # カラーマップ
    colorbar=True,        # カラーバーの表示
    title="タイトル",      # グラフタイトル
    xlabel="X軸ラベル",    # X軸ラベル
    ylabel="Y軸ラベル",    # Y軸ラベル
    grid=True             # グリッド線の表示
).end()
```

### エラーハンドリング

tascpy の操作でエラーが発生した場合は、わかりやすいエラーメッセージが表示されます。一般的なエラーとその対処法：

- **列名の誤り**: `KeyError: 'column_name'` → 正しい列名を確認してください
- **型の不一致**: `TypeError: ...` → 数値演算には数値型の列を使用してください
- **データ欠損**: `ValueError: Cannot operate on missing data` → `filter_out_none()` などで欠損値を処理してください

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
# 1. データ読み込み
collection = ColumnCollection.from_file("sample.csv", auto_detect_types=True)

# 2. データ前処理（選択、フィルタリング、補間）
clean_data = (
    collection.ops
    .filter_by_value("Force", lambda x: x is not None)  # Noneを除外
    .select(columns=["Time", "Force", "Displacement"])  # 必要な列のみ選択
    .interpolate(point_count=100, method="linear")  # 等間隔に補間
    .end()
)

# 3. ドメイン特化コレクションへの変換（必要に応じて）
ld_collection = clean_data.ops.as_domain(
    "load_displacement",
    load_column="Force",
    displacement_column="Displacement"
).end()

# 4. 分析と計算
result = (
    ld_collection.ops
    .calculate_stiffness(range_start=0.1, range_end=0.5, result_column="Stiffness")
    .calculate_yield_point(method="offset", offset_ratio=0.002)
    .calculate_energy(result_column="Energy")
    .end()
)

# 5. 可視化と結果確認
fig, ax = plt.subplots(figsize=(10, 6))
result.ops.plot_load_displacement(
    marker="o", 
    linestyle="-", 
    ax=ax,
    title="荷重-変位曲線と降伏点"
).end()

# 剛性と降伏点の表示
print(f"剛性: {result['Stiffness'].mean():.2f} kN/mm")
print(f"降伏荷重: {result['YieldPoint_Load'].values[0]:.2f} kN")
print(f"降伏変位: {result['YieldPoint_Displacement'].values[0]:.2f} mm")
```

## スタブファイル生成

tascpy のチェーンメソッドは動的に登録されるため、IDE の自動補完を有効にするにはスタブファイルの生成が必要です。初回インポート時に自動生成されますが、手動で実行することも可能です：

```python
from tascpy.operations.stub_generator import generate_stubs
generate_stubs()
```

## ヘルプとドキュメント

各サンプルコードにはドキュメント文字列が含まれており、関数やクラスの詳細な使用方法を確認できます。さらに詳しい情報は、[tascpy ドキュメント](../docs) を参照してください。

## 機能リクエストとバグ報告

tascpy の機能リクエストやバグ報告は、プロジェクトの GitHub リポジトリのイシュートラッカーで受け付けています。
