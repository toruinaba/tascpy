# tascpy ドメイン特化機能サンプル集

このディレクトリには、tascpy ライブラリのドメイン特化機能（Domain-Specific Functions）を示すサンプルスクリプトが含まれています。ドメイン特化機能とは、特定の分析対象や業務領域に合わせた専用機能のことで、tascpy ではこれらの機能を使ってより効率的かつ高度な分析が可能になります。

## ドメイン一覧

現在、tascpy では以下のドメイン固有の機能が提供されています：

1. **coordinate** - 座標データ処理ドメイン
2. **load_displacement** - 荷重-変位データ処理ドメイン

## 1. 座標データ処理ドメイン (coordinate)

座標空間内のポイントや要素の位置・移動・関係性を扱うための特化ドメインです。

### サンプルファイル一覧

1. **[00_coordinate_initialization.py](./coordinate/00_coordinate_initialization.py)** - 座標ドメインの初期化
   - `CoordinateCollection` の作成方法
   - 座標情報の設定と取得
   - 座標間の距離計算
   
   ```python
   # 座標情報を辞書で定義
   coordinates = {
       "sensor1": {"x": 0.0, "y": 0.0, "z": 0.0},  # 原点
       "sensor2": {"x": 10.0, "y": 0.0, "z": 0.0},  # X軸上
       "sensor3": {"x": 0.0, "y": 10.0, "z": 5.0},  # Y軸とZ軸方向
   }
   
   # 座標情報を初期化時に渡してインスタンス化
   collection = CoordinateCollection(step=steps, columns=columns, coordinates=coordinates)
   
   # 座標を持つカラム名のリストを取得
   cols_with_coords = collection.get_columns_with_coordinates()
   
   # 2つのセンサー間の距離を計算
   distance = collection.calculate_distance("sensor1", "sensor3")
   ```

2. **[01_coordinate_visualization_basic.py](./coordinate/01_coordinate_visualization_basic.py)** - 基本的な座標可視化
   - センサー位置のプロット（`get_coordinate_matrix`）
   - 値で色分けした散布図、逆距離加重補間によるヒートマップ
   - `ops.interpolate_at_point` による任意点での補間

   ```python
   points, names = collection.get_coordinate_matrix()   # (N, 2) の座標行列と列名
   values = [collection[n].values[50] for n in names]
   ax.scatter(points[:, 0], points[:, 1], c=values, cmap="coolwarm")
   ```

3. **[02_coordinate_visualization_advanced.py](./coordinate/02_coordinate_visualization_advanced.py)** - 高度な座標可視化
   - 等高線・3D 表面プロット
   - `calculate_distance` による距離行列と近傍探索
   - `spatial_clustering` による k-means クラスタリング
   - 温度勾配のベクトル場

4. **[03_coordinate_timeseries.py](./coordinate/03_coordinate_timeseries.py)** - 時系列座標データ
   - `ops.as_coordinate` による座標ドメインへの変換
   - センサーごとの時系列（`plot.plot`）
   - 時刻ごとの空間分布スナップショットと温度勾配

5. **[04_coordinate_axis_visualization.py](./coordinate/04_coordinate_axis_visualization.py)** - 座標軸に沿った可視化
   - `ops.select` で抽出したステップを `plot.plot_const_x` で X 座標に沿って描画
   - 散布図・棒グラフ・軸の入れ替え・選択センサーの比較

座標の可視化専用のプロット関数はないため、サンプルでは座標情報を取り出して matplotlib で描画しています。

### 座標ドメインの主要機能

#### 1. 座標定義と操作

```python
# 座標の設定（新しいコレクションを返す。None の軸は既存の値を残す）
collection = collection.with_coordinates("sensor4", x=5.0, y=5.0, z=0.0)

# 座標は各列のメタ情報 attrs["coordinates"] に格納され、列の改名・選択に追従する
print(collection.meta["sensor4"].attrs["coordinates"])

# 座標の取得
x, y, z = collection.get_column_coordinates("sensor1")

# 座標を持つ列と座標行列
names = collection.get_columns_with_coordinates()
matrix, valid_names = collection.get_coordinate_matrix(include_z=True)

# 距離計算
distance = collection.calculate_distance("sensor1", "sensor2")

# 座標による k-means クラスタリング（結果は metadata["coordinate_domain"]["clustering_result"]）
clustered = collection.spatial_clustering(n_clusters=3)
```

#### 2. 空間補間（CoordinateOps）

```python
# 任意点 (x, y) での値を、座標を持つ全列から行ごとに逆距離加重で補間した列を追加
result = collection.ops.interpolate_at_point(x=5.0, y=5.0, result_column="center").end()

# 補間元の列の値から、ターゲット列の座標位置の値を行ごとに補間（"interp_sensor3" 列）
result = collection.ops.spatial_interpolation_to_points(
    source_columns=["sensor1", "sensor2"], target_columns=["sensor3"]
).end()

# 指定行の値を矩形グリッド上に補間（結果は results["grid"] の GridResult）
grid = collection.ops.interpolate_grid(x_range=(0, 10), y_range=(0, 10), grid_size=(20, 20), row=-1).end().results["grid"]
grid.values  # (ny, nx)
```

## 2. 荷重-変位データ処理ドメイン (load_displacement)

材料試験や構造実験における荷重-変位関係の解析に特化したドメインです。

### サンプルファイル一覧

1. **[01_load_displacement_domain.py](./load_displacement/01_load_displacement_domain.py)** - 荷重-変位ドメインの基本操作
   - `LoadDisplacementCollection` への変換
   - 荷重-変位曲線のプロット
   - 接線剛性・初期剛性・降伏点の計算

   ```python
   # 荷重-変位ドメインへの変換
   ld_collection = collection.ops.as_load_displacement(
       load_column="Force1", displacement_column="Displacement1"
   ).end()

   # 荷重-変位曲線のプロット
   ld_collection.plot.plot_load_displacement()

   # 初期剛性（結果 "stiffness" に格納）
   stiffness = (
       ld_collection.ops.calculate_stiffness(range_start=0.1, range_end=0.4)
       .end().results["stiffness"].value
   )
   ```

2. **[02_load_displacement_special_curves.py](./load_displacement/02_load_displacement_special_curves.py)** - 特殊曲線の生成とプロット
   - サイクル列の作成（`cycle_count`）
   - スケルトン曲線・累積曲線の生成

   ```python
   curves = (
       ld_collection.ops
       .cycle_count()              # "Force1_cycle" 列を追加
       .create_skeleton_curve()    # サイクル列は自動検出
       .create_cumulative_curve()
       .end()
   )
   skeleton = curves.results["skeleton_curve"]      # XYSeriesResult（x/y は単位付きの Column）
   ```

3. **[03_yield_point_calculation.py](./load_displacement/03_yield_point_calculation.py)** - 降伏点の計算と評価
   - オフセット法・一般降伏法による降伏点検出
   - 検出に失敗するケースとデバッグ情報
   - 降伏点の可視化

   ```python
   result = ld_collection.ops.find_yield_point(
       method="offset", offset_value=0.002, range_start=0.1, range_end=0.4
   ).end()
   point = result.results["yield_point"]   # PointResult (x: 変位, y: 荷重)
   ```

### 荷重-変位ドメインの主要機能

`ld_collection.ops` では汎用操作に加えて以下が使えます。

| メソッド | 内容 | 結果の格納先 |
|---|---|---|
| `calculate_slopes()` | 区間ごとの傾き | 列 `slope_data` |
| `calculate_stiffness(range_start, range_end, method)` | 初期剛性 | `results["stiffness"]` |
| `find_yield_point(method, offset_value, ...)` | 降伏点 | `results["yield_point"]` |
| `cycle_count(column, step)` | サイクル番号 | 列 `{荷重列}_cycle` |
| `split_by_cycles(cycle_column)` | サイクルごとに分割 | `OpsList` |
| `find_peaks_and_valleys(column, distance)` | ピーク/バレーのマーカー | 列 `peak_valley` |
| `create_skeleton_curve(cycle_column)` | スケルトン曲線 | `results["skeleton_curve"]` |
| `create_cumulative_curve(cycle_column)` | 累積曲線 | `results["cumulative_curve"]` |
| `analyze_hysteresis(cycle_column)` | サイクルごとの履歴エネルギー・最大最小値 | 集計表（`ColumnCollection`） |
| `analyze_stiffness_degradation(cycle_column)` | サイクルごとの割線剛性 | 集計表（`ColumnCollection`） |

```python
# サイクルごとの履歴エネルギー
table = ld_collection.ops.cycle_count().analyze_hysteresis().end()
print(table["energy"].values)
```

## 使用方法

各サンプルファイルは、ドメイン固有の処理を学ぶための独立したスクリプトです。以下のように実行してください：

```bash
python coordinate/01_coordinate_visualization_basic.py
python load_displacement/01_load_displacement_domain.py
```

## ドメイン特化コレクションの作成

新しいドメインコレクションを作成するには、一般的な `ColumnCollection` から変換するか、直接ドメイン特化クラスをインスタンス化します：

### 1. ops の変換メソッドを使用した変換

```python
# 一般的なコレクションからドメイン特化コレクションへの変換
load_disp_collection = collection.ops.as_load_displacement(
    load_column="Force1",
    displacement_column="Displacement1",
).end()

coordinate_collection = collection.ops.as_coordinate(
    coordinates={
        "sensor1": {"x": 0.0, "y": 0.0, "z": 0.0},
        "sensor2": {"x": 10.0, "y": 0.0, "z": 0.0},
    }
).end()

# ドメイン固有の設定を外して汎用コレクションに戻す
core_collection = load_disp_collection.ops.as_core().end()
```

### 2. コンストラクタを使用した直接生成

```python
# 荷重-変位ドメインの直接作成
from tascpy.domains.load_displacement import LoadDisplacementCollection

ld_collection = LoadDisplacementCollection(
    columns,
    step=steps,
    units={"Force1": "kN", "Displacement1": "mm"},
    load_column="Force1",
    displacement_column="Displacement1",
)
print(ld_collection.load.unit)  # 'kN'

# 座標ドメインの直接作成
from tascpy.domains.coordinate import CoordinateCollection

coord_collection = CoordinateCollection(
    columns,
    step=steps,
    coordinates=coordinate_dict,
)
```

## 可視化結果

サンプルスクリプトから生成されるプロット画像は、各ドメインディレクトリ内の `imgs` フォルダに保存されます。これらのプロットは、ドメイン特化機能の効果を視覚的に理解するのに役立ちます。

主な可視化結果：

### 座標ドメイン
- センサー位置・散布図・ヒートマップ
- 等高線・3D 表面・距離行列・クラスタリング
- 時刻ごとの空間分布と温度勾配
- 座標軸に沿った値の分布

### 荷重-変位ドメイン
- 荷重-変位曲線
- スケルトン・累積曲線
- 降伏点の検出と表示
- サイクルごとの履歴エネルギーの集計

## ドメイン拡張の基本

tascpy では独自のドメイン特化コレクションを開発することも可能です。詳細は [開発者ガイド](../../docs/developer_guide.md) を参照してください。
