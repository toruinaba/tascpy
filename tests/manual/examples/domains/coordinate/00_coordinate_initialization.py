#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""座標ドメインにおける初期化時の座標設定サンプル

CoordinateCollectionの初期化時に座標情報を設定する方法を示します。
"""

import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
from tascpy.domains.coordinate import CoordinateCollection
from tascpy.domains import as_coordinate

print("==== 座標コレクション (CoordinateCollection) の初期化サンプル ====")

# --------------------------------------------------------------------------
# サンプル1: CoordinateCollectionのコンストラクタで座標情報を設定
# --------------------------------------------------------------------------
print("\n===== CoordinateCollectionの直接初期化 =====")

# ステップとカラムを準備
steps = list(range(10))
columns = {
    "sensor1": Column("sensor1", [20 + i for i in range(10)], unit="℃"),
    "sensor2": Column("sensor2", [25 + i * 0.5 for i in range(10)], unit="℃"),
    "sensor3": Column("sensor3", [18 + i * 0.7 for i in range(10)], unit="℃"),
}

# 座標情報を辞書で定義
coordinates = {
    "sensor1": {"x": 0.0, "y": 0.0, "z": 0.0},  # 原点
    "sensor2": {"x": 10.0, "y": 0.0, "z": 0.0},  # X軸上
    "sensor3": {"x": 0.0, "y": 10.0, "z": 5.0},  # Y軸とZ軸方向
}

# 座標情報を初期化時に渡してインスタンス化
collection1 = CoordinateCollection(columns, step=steps, coordinates=coordinates)

# 作成した情報を表示
print(f"コレクション内のカラム数: {len(collection1.columns)}")

# すべてのカラムの座標情報を表示
for col_name in collection1.columns:
    x, y, z = collection1.get_column_coordinates(col_name)
    print(f"カラム: {col_name}, 座標: ({x}, {y}, {z})")

# 座標を持つカラム名のリストを取得
cols_with_coords = collection1.get_columns_with_coordinates()
print(f"座標を持つカラム: {cols_with_coords}")

# 2つのセンサー間の距離を計算
distance = collection1.distance("sensor1", "sensor3")
print(f"sensor1とsensor3の間の距離: {distance:.2f}")

# --------------------------------------------------------------------------
# サンプル2: 汎用コレクションから座標ドメインへ変換
# --------------------------------------------------------------------------
print("\n===== ops.as_coordinate による変換 =====")

# ステップとカラムを準備
steps = list(range(10))
columns = {
    "posX": Column("posX", [i * 0.1 for i in range(10)], unit="mm"),
    "posY": Column("posY", [i * 0.2 for i in range(10)], unit="mm"),
    "value": Column("value", [5 + i * 0.5 for i in range(10)], unit="V"),
}

# 座標情報を辞書で定義 - 正方形の頂点を模擬
coordinates = {
    "posX": {"x": 0.0, "y": 0.0},
    "posY": {"x": 10.0, "y": 10.0},
    "value": {"x": 5.0, "y": 5.0, "z": 1.0},
}

# 汎用コレクションを作成し、座標情報を渡して座標ドメインに変換
collection2 = (
    ColumnCollection(columns, step=steps).ops.as_domain(as_coordinate, coordinates=coordinates).end()
)

# 作成した情報を表示
print(f"コレクション型: {type(collection2).__name__}")
print(f"コレクション内のカラム数: {len(collection2.columns)}")

# すべてのカラムの座標情報を表示
for col_name in collection2.columns:
    x, y, z = collection2.get_column_coordinates(col_name)
    print(f"カラム: {col_name}, 座標: ({x}, {y}, {z if z is not None else 'None'})")

# --------------------------------------------------------------------------
# サンプル3: 座標情報の格納場所と変更
# --------------------------------------------------------------------------
print("\n===== 座標情報の格納場所と変更 =====")

# ステップとカラムを準備
steps = list(range(5))
columns = {
    "node1": Column("node1", [100 * i for i in range(5)], unit="N"),
    "node2": Column("node2", [150 * i for i in range(5)], unit="N"),
}

# 座標情報を辞書で定義
coordinates = {
    "node1": {"x": 0.0, "y": 0.0, "z": 0.0},
    "node2": {"x": 100.0, "y": 0.0, "z": 0.0},
}

collection3 = CoordinateCollection(columns, step=steps, coordinates=coordinates)

# 座標は各列のメタ情報 attrs["coordinates"] に格納されている
print("\n列メタの構造:")
for col_name in collection3.columns:
    meta = collection3.meta[col_name]
    print(f"カラム: {col_name}, 単位: {meta.unit}, coordinates: {meta.attrs['coordinates']}")

# 座標の変更は新しいコレクションを返す（None の軸は既存の値を残す）
moved = collection3.with_coordinates("node2", x=120.0)
print(f"変更前の node2: {collection3.get_column_coordinates('node2')}")
print(f"変更後の node2: {moved.get_column_coordinates('node2')}")

# 列名を変更しても座標は列に追従する
renamed = collection3.rename({"node1": "base"})
print(f"改名後の base の座標: {renamed.get_column_coordinates('base')}")

# --------------------------------------------------------------------------
# サンプル4: メソッドチェーンを活用した座標情報の操作
# --------------------------------------------------------------------------
print("\n===== メソッドチェーンを活用した座標情報の操作 =====")

# 基本的なデータの準備
steps = list(range(5))
columns = {
    "point_a": Column("point_a", [1.0, 1.2, 1.5, 1.8, 2.0], unit="V"),
    "point_b": Column("point_b", [2.0, 2.5, 3.0, 3.5, 4.0], unit="V"),
    "point_c": Column("point_c", [0.5, 0.6, 0.7, 0.8, 0.9], unit="V"),
}

# 座標情報付きのコレクションを作成
coordinates = {
    "point_a": {"x": 0.0, "y": 0.0},
    "point_b": {"x": 10.0, "y": 0.0},
    "point_c": {"x": 5.0, "y": 8.7},
}

# コレクション作成
collection4 = CoordinateCollection(columns, step=steps, coordinates=coordinates)

# メソッドチェーンを使用した操作
result = (
    collection4.ops.select(["point_a", "point_b"])  # point_aとpoint_bのみ選択
    .add("point_a", "point_b", result_column="sum_ab")  # 2つのカラムの加算
    .multiply("sum_ab", 0.5, result_column="avg_ab")  # 平均値の計算
    .end()
)

print(f"メソッドチェーン実行後のカラム数: {len(result.columns)}")
print("結果のカラム名:", result.columns)

# 結果にも座標情報は保持されている
coords_in_result = result.get_columns_with_coordinates()
print(f"結果で座標を持つカラム: {coords_in_result}")

print("\n全てのサンプル実行が完了しました。")
