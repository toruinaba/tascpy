#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""座標ドメインの高度な可視化サンプル"""

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

    # グリッド上に配置された25個のセンサー
    grid_size = 5
    sensor_columns = {}

    for i in range(grid_size):
        for j in range(grid_size):
            x = i * 4.0
            y = j * 4.0

            # 各センサーのデータ（時間とともに変化する値）
            values = (
                np.sin(np.linspace(0, 4 * np.pi, 100) + i * np.pi / 5) * 5
                + np.cos(np.linspace(0, 6 * np.pi, 100) + j * np.pi / 5) * 3
                + 15
            )

            # 高さによるバリエーション（山のような形状）
            z = 5.0 * np.exp(-((i - grid_size / 2) ** 2 + (j - grid_size / 2) ** 2) / 8)

            # 列を作成
            col_name = f"sensor_{i+1}_{j+1}"
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
    for i in range(grid_size):
        for j in range(grid_size):
            x = i * 4.0
            y = j * 4.0
            z = 5.0 * np.exp(-((i - grid_size / 2) ** 2 + (j - grid_size / 2) ** 2) / 8)

            col_name = f"sensor_{i+1}_{j+1}"
            coordinate_collection.set_column_coordinates(col_name, x=x, y=y, z=z)

    return coordinate_collection


# ベクトル場データの作成
def add_vector_data(coordinate_collection):
    """コレクションにベクトル場データを追加"""
    grid_size = 5

    # u成分とv成分のリストを作成
    u_list = []
    v_list = []
    w_list = []

    for i in range(grid_size):
        for j in range(grid_size):
            # 渦状のベクトル場を作成
            x = i * 4.0
            y = j * 4.0

            # 中心位置
            center_x = (grid_size - 1) * 4.0 / 2
            center_y = (grid_size - 1) * 4.0 / 2

            # 中心からの変位
            dx = x - center_x
            dy = y - center_y

            # 渦場（中心からの距離に応じた大きさで）
            dist = np.sqrt(dx**2 + dy**2)
            scale = 1.0 if dist < 0.1 else 1.0 / dist

            # 時間変化するデータ（100ステップ分）
            u_values = [-dy * scale * (0.8 + 0.2 * np.sin(t / 10)) for t in range(100)]
            v_values = [dx * scale * (0.8 + 0.2 * np.sin(t / 10)) for t in range(100)]
            w_values = [0.5 * np.sin(t / 15) for t in range(100)]

            u_list.append(u_values)
            v_list.append(v_values)
            w_list.append(w_values)

    # u成分とv成分の列を追加
    coordinate_collection.columns["u_velocity"] = Column(
        ch=None,
        name="u_velocity",
        unit="m/s",
        values=u_list[0],  # 最初のセンサーのデータを代表として使用
    )

    coordinate_collection.columns["v_velocity"] = Column(
        ch=None,
        name="v_velocity",
        unit="m/s",
        values=v_list[0],  # 最初のセンサーのデータを代表として使用
    )

    coordinate_collection.columns["w_velocity"] = Column(
        ch=None,
        name="w_velocity",
        unit="m/s",
        values=w_list[0],  # 最初のセンサーのデータを代表として使用
    )

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
    coordinate_data = add_vector_data(coordinate_data)

    print("作成した座標コレクション:")
    print(f"- ステップ数: {len(coordinate_data.step)}")
    print(f"- センサー数: {len(coordinate_data.columns) - 3}")  # ベクトル成分を除く

    print("\n# 高度な可視化機能のデモ")

    # 特定のステップのデータを使用
    step_50 = extract_step_data(coordinate_data, 50)

    # 1. 等高線プロット
    print("\n## 1. plot_spatial_contour - 等高線プロット")
    fig1, ax1 = plt.subplots(figsize=(10, 8))
    plot_spatial_contour(
        step_50,
        value_column="sensor_1_1",
        levels=15,
        resolution=(50, 50),
        filled=True,
        ax=ax1,
    )
    plt.tight_layout()
    plt.savefig(os.path.join(IMGS_DIR, "coordinate_contour.png"), dpi=100)
    plt.close()

    # 2. 3D表面プロット
    print("\n## 2. plot_3d_surface - 3D表面プロット")
    fig2 = plt.figure(figsize=(12, 10))
    ax2 = fig2.add_subplot(111, projection="3d")
    plot_3d_surface(step_50, value_column="sensor_3_3", resolution=(50, 50), ax=ax2)
    plt.tight_layout()
    plt.savefig(os.path.join(IMGS_DIR, "coordinate_3d_surface.png"), dpi=100)
    plt.close()

    # 3. 距離行列プロット
    print("\n## 3. plot_coordinate_distance - 距離行列")
    fig3, ax3 = plt.subplots(figsize=(10, 8))
    # サンプル数を減らす（最初の9個のセンサーのみ使用）
    sensor_names = [f"sensor_{i}_{j}" for i in range(1, 4) for j in range(1, 4)]
    # 新しいコレクションを作成
    reduced_data = CoordinateCollection(
        step=step_50.step,
        columns={
            name: step_50.columns[name].clone()
            for name in sensor_names
            if name in step_50.columns
        },
        metadata=step_50.metadata.copy() if step_50.metadata else {},
    )
    # 座標情報をコピー
    for name in sensor_names:
        if name in step_50.columns:
            x, y, z = step_50.get_column_coordinates(name)
            if x is not None or y is not None or z is not None:
                reduced_data.set_column_coordinates(name, x=x, y=y, z=z)

    plot_coordinate_distance(reduced_data, plot_type="matrix", ax=ax3)
    plt.tight_layout()
    plt.savefig(os.path.join(IMGS_DIR, "coordinate_distance_matrix.png"), dpi=100)
    plt.close()

    # 4. 空間クラスタリング
    print("\n## 4. plot_spatial_cluster - 空間クラスタリング")
    fig4, ax4 = plt.subplots(figsize=(10, 8))
    try:
        plot_spatial_cluster(reduced_data, n_clusters=4, method="kmeans", ax=ax4)
        plt.tight_layout()
        plt.savefig(os.path.join(IMGS_DIR, "coordinate_clustering.png"), dpi=100)
    except ImportError:
        print(
            "scikit-learnがインストールされていないため、クラスタリングをスキップします"
        )
        print("インストールするには: pip install scikit-learn")
    plt.close()

    # 5. ベクトル場プロット
    print("\n## 5. plot_vector_field - ベクトル場")
    fig5, ax5 = plt.subplots(figsize=(10, 8))
    plot_vector_field(
        step_50, u_column="u_velocity", v_column="v_velocity", scale=1.0, ax=ax5
    )
    plt.tight_layout()
    plt.savefig(os.path.join(IMGS_DIR, "coordinate_vector_field.png"), dpi=100)
    plt.close()

    print("\n画像ファイルを保存しました。")
    print(f"保存先: {IMGS_DIR}")


if __name__ == "__main__":
    main()
