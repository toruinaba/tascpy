#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""座標ドメインにおける初期化時の座標設定サンプル

CoordinateCollectionの初期化時に座標情報を設定する方法を示します。
"""

import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
from tascpy.domains.coordinate import CoordinateCollection
from tascpy.domains.factory import DomainCollectionFactory

print("==== 座標コレクション (CoordinateCollection) の初期化サンプル ====")

# --------------------------------------------------------------------------
# サンプル1: CoordinateCollectionのコンストラクタで座標情報を設定
# --------------------------------------------------------------------------
print("\n===== CoordinateCollectionの直接初期化 =====")

# ステップとカラムを準備
steps = list(range(10))
columns = {
    "sensor1": Column(
        ch=None, name="sensor1", unit="℃", values=[20 + i for i in range(10)]
    ),
    "sensor2": Column(
        ch=None, name="sensor2", unit="℃", values=[25 + i * 0.5 for i in range(10)]
    ),
    "sensor3": Column(
        ch=None, name="sensor3", unit="℃", values=[18 + i * 0.7 for i in range(10)]
    ),
}

# 座標情報を辞書で定義
coordinates = {
    "sensor1": {"x": 0.0, "y": 0.0, "z": 0.0},  # 原点
    "sensor2": {"x": 10.0, "y": 0.0, "z": 0.0},  # X軸上
    "sensor3": {"x": 0.0, "y": 10.0, "z": 5.0},  # Y軸とZ軸方向
}

# 座標情報を初期化時に渡してインスタンス化
collection1 = CoordinateCollection(step=steps, columns=columns, coordinates=coordinates)

# 作成した情報を表示
print(f"コレクション内のカラム数: {len(collection1.columns)}")

# すべてのカラムの座標情報を表示
for col_name in collection1.columns.keys():
    x, y, z = collection1.get_column_coordinates(col_name)
    print(f"カラム: {col_name}, 座標: ({x}, {y}, {z})")

# 座標を持つカラム名のリストを取得
cols_with_coords = collection1.get_columns_with_coordinates()
print(f"座標を持つカラム: {cols_with_coords}")

# 2つのセンサー間の距離を計算
distance = collection1.calculate_distance("sensor1", "sensor3")
print(f"sensor1とsensor3の間の距離: {distance:.2f}")

# --------------------------------------------------------------------------
# サンプル2: ファクトリを使用した座標情報の初期化
# --------------------------------------------------------------------------
print("\n===== ファクトリによる初期化 =====")

# ステップとカラムを準備
steps = list(range(10))
columns = {
    "posX": Column(
        ch=None, name="posX", unit="mm", values=[i * 0.1 for i in range(10)]
    ),
    "posY": Column(
        ch=None, name="posY", unit="mm", values=[i * 0.2 for i in range(10)]
    ),
    "value": Column(
        ch=None, name="value", unit="V", values=[5 + i * 0.5 for i in range(10)]
    ),
}

# 座標情報を辞書で定義 - 正方形の頂点を模擬
coordinates = {
    "posX": {"x": 0.0, "y": 0.0},
    "posY": {"x": 10.0, "y": 10.0},
    "value": {"x": 5.0, "y": 5.0, "z": 1.0},
}

# ファクトリ関数を使用して座標情報付きのコレクションを作成
collection2 = DomainCollectionFactory.create(
    "coordinate", step=steps, columns=columns, coordinates=coordinates
)

# 作成した情報を表示
print(f"コレクション型: {type(collection2).__name__}")
print(f"コレクション内のカラム数: {len(collection2.columns)}")

# すべてのカラムの座標情報を表示
for col_name in collection2.columns.keys():
    x, y, z = collection2.get_column_coordinates(col_name)
    print(f"カラム: {col_name}, 座標: ({x}, {y}, {z if z is not None else 'None'})")

# --------------------------------------------------------------------------
# サンプル3: カスタムメタデータキーと座標情報の同時設定
# --------------------------------------------------------------------------
print("\n===== カスタムメタデータキーと座標情報の同時設定 =====")

# ステップとカラムを準備
steps = list(range(5))
columns = {
    "node1": Column(
        ch=None, name="node1", unit="N", values=[100 * i for i in range(5)]
    ),
    "node2": Column(
        ch=None, name="node2", unit="N", values=[150 * i for i in range(5)]
    ),
}

# 座標情報を辞書で定義
coordinates = {
    "node1": {"x": 0.0, "y": 0.0, "z": 0.0},
    "node2": {"x": 100.0, "y": 0.0, "z": 0.0},
}

# カスタムメタデータキーと座標情報を指定して初期化
collection3 = CoordinateCollection(
    step=steps,
    columns=columns,
    coordinate_metadata_key="position",  # 座標情報が格納されるキーを変更
    coordinates=coordinates,
)

# 作成した情報を表示
print(f"メタデータキー: {collection3.coordinate_metadata_key}")

# すべてのカラムの座標情報を表示
for col_name in collection3.columns.keys():
    x, y, z = collection3.get_column_coordinates(col_name)
    print(f"カラム: {col_name}, 座標: ({x}, {y}, {z})")

# メタデータを直接確認 (内部実装の確認)
print("\n内部メタデータ構造:")
for col_name, col in collection3.columns.items():
    print(f"カラム: {col_name}")
    if hasattr(col, "metadata") and "position" in col.metadata:
        print(f"  - position: {col.metadata['position']}")

# --------------------------------------------------------------------------
# サンプル4: メソッドチェーンを活用した座標情報の操作
# --------------------------------------------------------------------------
print("\n===== メソッドチェーンを活用した座標情報の操作 =====")

# 基本的なデータの準備
steps = list(range(5))
columns = {
    "point_a": Column(
        ch=None, name="point_a", unit="V", values=[1.0, 1.2, 1.5, 1.8, 2.0]
    ),
    "point_b": Column(
        ch=None, name="point_b", unit="V", values=[2.0, 2.5, 3.0, 3.5, 4.0]
    ),
    "point_c": Column(
        ch=None, name="point_c", unit="V", values=[0.5, 0.6, 0.7, 0.8, 0.9]
    ),
}

# 座標情報付きのコレクションを作成
coordinates = {
    "point_a": {"x": 0.0, "y": 0.0},
    "point_b": {"x": 10.0, "y": 0.0},
    "point_c": {"x": 5.0, "y": 8.7},
}

# コレクション作成
collection4 = CoordinateCollection(step=steps, columns=columns, coordinates=coordinates)

# メソッドチェーンを使用した操作
result = (
    collection4.ops.select(["point_a", "point_b"])  # point_aとpoint_bのみ選択
    .add("point_a", "point_b", result_column="sum_ab")  # 2つのカラムの加算
    .multiply("sum_ab", 0.5, result_column="avg_ab")  # 平均値の計算
    .end()
)

print(f"メソッドチェーン実行後のカラム数: {len(result.columns)}")
print("結果のカラム名:", list(result.columns.keys()))

# 結果にも座標情報は保持されている
coords_in_result = result.get_columns_with_coordinates()
print(f"結果で座標を持つカラム: {coords_in_result}")

print("\n全てのサンプル実行が完了しました。")
