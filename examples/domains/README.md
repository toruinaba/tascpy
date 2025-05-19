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
   - 2D/3Dプロット
   - カラーマップによる値の表現
   - 時間変化の表現
   
   ```python
   # 座標データの3Dプロット例
   (
       coord_collection.ops
       .coordinate_plot_3d(
           column_values="temperature",
           colormap="rainbow",
           title="空間上の温度分布",
           value_label="温度 (℃)",
           show_colorbar=True,
           marker_size=100,
           show_labels=True,
           ax=ax
       )
       .end()
   )
   ```

3. **[02_coordinate_visualization_advanced.py](./coordinate/02_coordinate_visualization_advanced.py)** - 高度な座標可視化
   - 等高線プロット
   - 補間による面表示
   - マルチプロット比較
   
4. **[03_coordinate_timeseries.py](./coordinate/03_coordinate_timeseries.py)** - 時系列座標データ処理
   - 座標の時間変化の捕捉
   - 軌跡のプロット
   - 移動速度・加速度の計算
   
5. **[04_coordinate_axis_visualization.py](./coordinate/04_coordinate_axis_visualization.py)** - 座標軸可視化
   - 座標軸の表示とカスタマイズ
   - ベクトル場の可視化
   - 基準点と方向の表示

### 座標ドメインの主要機能

#### 1. 座標定義と操作

```python
# 座標の追加
collection.set_column_coordinates("sensor4", x=5.0, y=5.0, z=0.0)

# 座標の更新
collection.update_column_coordinates("sensor1", x=1.0, y=1.0, z=1.0)

# 座標の取得
x, y, z = collection.get_column_coordinates("sensor1")

# 距離計算 
distance = collection.calculate_distance("sensor1", "sensor2")
```

#### 2. 空間補間

```python
# 空間内の任意の点での値を補間計算
interpolated_collection = (
    coord_collection.ops
    .spatial_interpolate(
        column="temperature",
        method="idw",  # 逆距離加重法
        power=2,
        result_column="interpolated_temp"
    )
    .end()
)
```

#### 3. 特殊プロット機能

```python
# 等高線プロット
collection.ops.contour_plot(
    column="temperature",
    grid_size=(50, 50),
    colormap="viridis",
    levels=10,
    title="温度分布等高線"
)

# ヒートマッププロット
collection.ops.heatmap_plot(
    column="temperature",
    grid_size=(50, 50),
    colormap="plasma",
    title="温度分布ヒートマップ"
)
```

## 2. 荷重-変位データ処理ドメイン (load_displacement)

材料試験や構造実験における荷重-変位関係の解析に特化したドメインです。

### サンプルファイル一覧

1. **[01_load_displacement_domain.py](./load_displacement/01_load_displacement_domain.py)** - 荷重-変位ドメインの基本操作
   - `LoadDisplacementCollection` の作成と設定
   - 荷重-変位曲線のプロット
   - 剛性計算とヤング率の推定
   
   ```python
   # 荷重-変位ドメインへの変換
   ld_collection = collection.ops.as_domain(
       "load_displacement",
       load_column="Force1",
       displacement_column="Displacement1"
   ).end()
   
   # 荷重-変位曲線のプロット
   ld_collection.ops.plot_load_displacement(
       title="荷重-変位曲線",
       xlabel="変位 (mm)",
       ylabel="荷重 (kN)",
       marker="o",
       linestyle="-"
   )
   
   # 剛性計算
   result = ld_collection.ops.calculate_stiffness(
       range_start=0.1,
       range_end=0.5,
       result_column="Stiffness"
   ).end()
   ```

2. **[02_load_displacement_special_curves.py](./load_displacement/02_load_displacement_special_curves.py)** - 特殊曲線の生成とプロット
   - スケルトン曲線の生成
   - 累積曲線の生成
   - 包絡線の抽出
   
   ```python
   # スケルトン曲線の作成
   skeleton_result = (
       ld_collection.ops
       .create_skeleton_curve(
           result_load_column="SkeletonLoad", 
           result_displacement_column="SkeletonDisp"
       )
       .end()
   )
   
   # 累積曲線の作成
   cumulative_result = (
       ld_collection.ops
       .create_cumulative_curve(
           result_load_column="CumulativeLoad",
           result_displacement_column="CumulativeDisp"
       )
       .end()
   )
   ```

3. **[03_yield_point_calculation.py](./load_displacement/03_yield_point_calculation.py)** - 降伏点の計算と評価
   - 線形領域の判定
   - オフセット法による降伏点検出
   - 降伏点の視覚化
   
   ```python
   # 降伏点の計算
   yield_result = (
       ld_collection.ops
       .calculate_yield_point(
           method="offset",
           offset_ratio=0.002,  # 0.2%オフセット法
           range_start=0.1,
           range_end=0.4,
           detailed_info=True  # 詳細情報の取得
       )
       .end()
   )
   
   # 降伏点のプロット
   ld_collection.ops.plot_yield_point(
       method="offset",
       offset_ratio=0.002,
       show_tangent_line=True,
       show_offset_line=True,
       title="降伏点の検出 (0.2%オフセット法)"
   )
   ```

### 荷重-変位ドメインの主要機能

#### 1. 基本特性の計算

```python
# 線形領域の剛性計算
result = ld_collection.ops.calculate_stiffness(
    range_start=0.1,   # 荷重または変位の範囲開始点
    range_end=0.5,     # 荷重または変位の範囲終了点
    range_type="displacement",  # 'displacement'または'load'で範囲の種類を指定
    result_column="Stiffness"  # 結果列名
).end()

# 降伏点の計算
yield_result = ld_collection.ops.calculate_yield_point(
    method="offset",   # 'offset'または'proportional_limit'
    offset_ratio=0.002,  # オフセットひずみ率 (0.2%)
    result_column_prefix="YieldPoint"  # 結果列名の接頭辞
).end()

# 最大荷重点の検出
max_load_result = ld_collection.ops.find_max_load_point(
    result_column_prefix="MaxLoadPoint"
).end()
```

#### 2. 特殊曲線の生成

```python
# スケルトン曲線の作成
skeleton_result = ld_collection.ops.create_skeleton_curve(
    peak_selection="all",  # 'all'、'positive'または'negative'
    result_load_column="SkeletonLoad", 
    result_displacement_column="SkeletonDisp"
).end()

# 累積曲線の作成
cumulative_result = ld_collection.ops.create_cumulative_curve(
    result_load_column="CumulativeLoad",
    result_displacement_column="CumulativeDisp"
).end()
```

#### 3. エネルギー計算

```python
# エネルギー計算（荷重-変位曲線下の面積）
energy_result = ld_collection.ops.calculate_energy(
    result_column="Energy",
    cumulative=True  # 累積エネルギーを計算
).end()

# 各サイクルのエネルギー消費を計算
cycle_energy_result = ld_collection.ops.calculate_cycle_energy(
    result_column="CycleEnergy"
).end()
```

## 使用方法

各サンプルファイルは、ドメイン固有の処理を学ぶための独立したスクリプトです。以下のように実行してください：

```bash
python coordinate/01_coordinate_visualization_basic.py
python load_displacement/01_load_displacement_domain.py
```

## ドメイン特化コレクションの作成

新しいドメインコレクションを作成するには、一般的な `ColumnCollection` から変換するか、直接ドメイン特化クラスをインスタンス化します：

### 1. as_domain メソッドを使用した変換

```python
# 一般的なコレクションからドメイン特化コレクションへの変換
load_disp_collection = collection.ops.as_domain(
    "load_displacement",
    load_column="Force1",
    displacement_column="Displacement1"
).end()

coordinate_collection = collection.ops.as_domain(
    "coordinate",
    coordinates={
        "sensor1": {"x": 0.0, "y": 0.0, "z": 0.0},
        "sensor2": {"x": 10.0, "y": 0.0, "z": 0.0},
    }
).end()
```

### 2. コンストラクタを使用した直接生成

```python
# 荷重-変位ドメインの直接作成
from tascpy.domains.load_displacement import LoadDisplacementCollection

ld_collection = LoadDisplacementCollection(
    step=steps,
    columns=columns,
    metadata=metadata,
    load_column="Force1",
    displacement_column="Displacement1"
)

# 座標ドメインの直接作成
from tascpy.domains.coordinate import CoordinateCollection

coord_collection = CoordinateCollection(
    step=steps,
    columns=columns,
    metadata=metadata,
    coordinates=coordinate_dict
)
```

### 3. ファクトリを使用した作成

```python
# ドメインコレクションファクトリを使用した作成
from tascpy.domains.factory import DomainCollectionFactory

ld_collection = DomainCollectionFactory.create(
    "load_displacement",
    step=steps,
    columns=columns,
    metadata=metadata,
    load_column="Force1",
    displacement_column="Displacement1"
)

coord_collection = DomainCollectionFactory.create(
    "coordinate",
    step=steps,
    columns=columns,
    metadata=metadata,
    coordinates=coordinate_dict
)
```

## 可視化結果

サンプルスクリプトから生成されるプロット画像は、各ドメインディレクトリ内の `imgs` フォルダに保存されます。これらのプロットは、ドメイン特化機能の効果を視覚的に理解するのに役立ちます。

主な可視化結果：

### 座標ドメイン
- 2D/3D座標プロット
- 等高線・ヒートマップ
- 時系列変化のアニメーション
- 空間補間結果

### 荷重-変位ドメイン
- 荷重-変位曲線
- スケルトン・累積曲線
- 降伏点の検出と表示
- エネルギー変化のプロット

## ドメイン拡張の基本

tascpy では独自のドメイン特化コレクションを開発することも可能です。詳細は [開発者ガイド](../../docs/developer_guide.md) を参照してください。
