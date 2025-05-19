#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""座標ドメインの基本的な可視化サンプル"""

import os
import numpy as np
import matplotlib.pyplot as plt
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column

# 座標ドメインとその機能を明示的にインポート
from tascpy.domains.coordinate import CoordinateCollection

# 座標操作関連の機能をインポート
from tascpy.operations.coordinate.basic import *
from tascpy.operations.coordinate.plot import *

# 出力画像用のディレクトリパスを設定
IMGS_DIR = os.path.join(os.path.dirname(__file__), "imgs")
os.makedirs(IMGS_DIR, exist_ok=True)


# サンプルデータの作成
def create_sample_coordinate_data():
    """サンプルの座標データを作成"""
    # ステップ
    steps = list(range(100))

    # センサーの位置データを作成
    # 円形に配置された10個のセンサー
    n_sensors = 10
    radius = 10.0
    sensor_columns = {}

    for i in range(n_sensors):
        angle = 2 * np.pi * i / n_sensors
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)

        # 各センサーのデータ（時間とともに変化する値）
        values = np.sin(np.linspace(0, 4 * np.pi, 100) + i * np.pi / 5) * 5 + 10

        # 列を作成
        col_name = f"sensor_{i+1}"
        sensor_columns[col_name] = Column(
            ch=None, name=col_name, unit="℃", values=values.tolist()  # 温度を想定
        )

    # 通常のコレクションを作成
    collection = ColumnCollection(steps, sensor_columns)

    # 座標ドメインに変換 (DomainFactoryを使わず直接作成)
    coordinate_collection = CoordinateCollection(
        step=collection.step,
        columns={name: col.clone() for name, col in collection.columns.items()},
        metadata=collection.metadata.copy() if collection.metadata else {},
    )

    # 各センサーに座標を設定
    for i in range(n_sensors):
        angle = 2 * np.pi * i / n_sensors
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        z = 0.0 if i % 2 == 0 else 1.0  # 半分のセンサーは高さ1.0に配置

        col_name = f"sensor_{i+1}"
        coordinate_collection.set_column_coordinates(col_name, x=x, y=y, z=z)

    return coordinate_collection


# 特定のステップのデータだけを残す関数
def extract_step_data(collection, step_index):
    """特定のステップのデータだけを含む新しいコレクションを作成"""
    result = collection.clone()

    # 各列のデータを指定ステップのものだけにする
    for col_name, col in result.columns.items():
        if hasattr(col, "values") and len(col.values) > step_index:
            # step_indexのデータだけを残す
            col.values = [col.values[step_index]]

    return result


# メイン処理
def main():
    # サンプルデータを作成
    coordinate_data = create_sample_coordinate_data()

    print("作成した座標コレクション:")
    print(f"- ステップ数: {len(coordinate_data.step)}")
    print(f"- センサー数: {len(coordinate_data.columns)}")

    # 座標情報を持つ列を表示
    columns_with_coords = coordinate_data.get_columns_with_coordinates()
    print(f"\n座標情報を持つ列: {len(columns_with_coords)} 個")
    for col in columns_with_coords[:5]:  # 最初の5つだけ表示
        x, y, z = coordinate_data.get_column_coordinates(col)
        print(f"- {col}: x={x:.2f}, y={y:.2f}, z={z}")

    print("\n# 基本的な可視化機能のデモ")

    # 1. 座標位置のプロット
    print("\n## 1. plot_coordinates - 座標位置のプロット")
    fig1, ax1 = plt.subplots(figsize=(10, 8))
    plot_coordinates(coordinate_data, ax=ax1)
    plt.tight_layout()
    plt.savefig(os.path.join(IMGS_DIR, "coordinate_positions.png"), dpi=100)
    plt.close()

    # 2. 座標に基づく散布図プロット
    print("\n## 2. plot_spatial_values - 座標に基づく散布図")
    fig2, ax2 = plt.subplots(figsize=(10, 8))
    plot_spatial_values(
        coordinate_data,
        value_column="sensor_1",
        plot_type="scatter",
        ax=ax2,
        size_scale=100,
    )
    plt.tight_layout()
    plt.savefig(os.path.join(IMGS_DIR, "coordinate_scatter.png"), dpi=100)
    plt.close()

    # 3. 座標に基づく空間ヒートマップ
    print("\n## 3. plot_spatial_heatmap - 空間ヒートマップ")
    fig3, ax3 = plt.subplots(figsize=(10, 8))
    # 特定のステップのデータを使用
    step_50 = extract_step_data(coordinate_data, 50)

    plot_spatial_heatmap(
        step_50, value_column="sensor_1", resolution=(50, 50), show_points=True, ax=ax3
    )
    plt.tight_layout()
    plt.savefig(os.path.join(IMGS_DIR, "coordinate_heatmap.png"), dpi=100)
    plt.close()

    print("\n画像ファイルを保存しました。")
    print(f"保存先: {IMGS_DIR}")


if __name__ == "__main__":
    main()
