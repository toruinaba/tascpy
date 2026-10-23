#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""座標ドメインの基本的な可視化サンプル

CoordinateCollection の座標情報（get_coordinate_matrix など）と
CoordinateOps の補間操作を使い、matplotlib で可視化します。
"""

import os

import matplotlib.pyplot as plt
import numpy as np

from tascpy.core.column import Column
from tascpy.domains.coordinate import CoordinateCollection

IMGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs")
os.makedirs(IMGS_DIR, exist_ok=True)


def create_sample_coordinate_data() -> CoordinateCollection:
    """円形に配置した 10 個の温度センサーのデータを作成"""
    n_steps, n_sensors, radius = 100, 10, 10.0
    t = np.linspace(0, 4 * np.pi, n_steps)

    columns = {}
    coordinates = {}
    for i in range(n_sensors):
        name = f"sensor_{i + 1}"
        angle = 2 * np.pi * i / n_sensors
        values = np.sin(t + i * np.pi / 5) * 5 + 10
        columns[name] = Column(name, values.tolist(), unit="℃")
        coordinates[name] = {
            "x": radius * np.cos(angle),
            "y": radius * np.sin(angle),
            "z": 0.0 if i % 2 == 0 else 1.0,
        }

    return CoordinateCollection(columns, step=list(range(n_steps)), coordinates=coordinates)


def values_at_step(collection: CoordinateCollection, columns, step_index: int) -> np.ndarray:
    """指定ステップでの各列の値を取得"""
    return np.array([collection[c].values[step_index] for c in columns], dtype=float)


def idw_grid(points: np.ndarray, values: np.ndarray, resolution=(50, 50), power: float = 2.0, margin: float = 1.0):
    """逆距離加重法でグリッド上の値を補間"""
    xs = np.linspace(points[:, 0].min() - margin, points[:, 0].max() + margin, resolution[0])
    ys = np.linspace(points[:, 1].min() - margin, points[:, 1].max() + margin, resolution[1])
    gx, gy = np.meshgrid(xs, ys)
    d = np.hypot(gx[..., None] - points[:, 0], gy[..., None] - points[:, 1])
    w = 1.0 / np.maximum(d, 1e-12) ** power
    return gx, gy, (w * values).sum(axis=-1) / w.sum(axis=-1)


def main():
    data = create_sample_coordinate_data()
    print("作成した座標コレクション:")
    print(f"- ステップ数: {len(data.step)}")
    print(f"- センサー数: {len(data.columns)}")

    columns = data.get_columns_with_coordinates()
    print(f"\n座標情報を持つ列: {len(columns)} 個")
    for col in columns[:5]:
        x, y, z = data.get_column_coordinates(col)
        print(f"- {col}: x={x:.2f}, y={y:.2f}, z={z}")

    points, names = data.get_coordinate_matrix()

    # 1. センサー位置
    print("\n## 1. 座標位置のプロット")
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(points[:, 0], points[:, 1], s=80)
    for (x, y), name in zip(points, names):
        ax.annotate(name, (x, y), textcoords="offset points", xytext=(5, 5))
    ax.set_aspect("equal")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("センサー位置")
    fig.tight_layout()
    fig.savefig(os.path.join(IMGS_DIR, "coordinate_positions.png"), dpi=100)
    plt.close(fig)

    # 2. ステップ 50 の値で色分けした散布図
    print("\n## 2. 座標に基づく散布図（ステップ 50）")
    values = values_at_step(data, names, 50)
    fig, ax = plt.subplots(figsize=(8, 8))
    sc = ax.scatter(points[:, 0], points[:, 1], c=values, s=values * 20, cmap="coolwarm")
    fig.colorbar(sc, ax=ax, label="温度 [℃]")
    ax.set_aspect("equal")
    ax.set_title("ステップ 50 の温度分布")
    fig.tight_layout()
    fig.savefig(os.path.join(IMGS_DIR, "coordinate_scatter.png"), dpi=100)
    plt.close(fig)

    # 3. 逆距離加重法による空間ヒートマップ
    print("\n## 3. 空間ヒートマップ（ステップ 50）")
    gx, gy, grid = idw_grid(points, values)
    fig, ax = plt.subplots(figsize=(9, 8))
    mesh = ax.pcolormesh(gx, gy, grid, cmap="coolwarm", shading="auto")
    ax.scatter(points[:, 0], points[:, 1], c="k", s=20)
    fig.colorbar(mesh, ax=ax, label="温度 [℃]")
    ax.set_aspect("equal")
    ax.set_title("温度ヒートマップ（逆距離加重補間）")
    fig.tight_layout()
    fig.savefig(os.path.join(IMGS_DIR, "coordinate_heatmap.png"), dpi=100)
    plt.close(fig)

    # 4. ops による任意点での補間（各列の値を指定点へ補間した列を追加）
    print("\n## 4. ops.interpolate_at_point - 原点での補間値")
    step_50 = data.ops.select(indices=[50])
    interpolated = step_50.interpolate_at_point(x=0.0, y=0.0, target_columns=names[:3]).end()
    for name in names[:3]:
        print(f"- interp_{name}: {interpolated[f'interp_{name}'].values[0]:.3f}")

    print(f"\n画像ファイルを保存しました: {IMGS_DIR}")


if __name__ == "__main__":
    main()
