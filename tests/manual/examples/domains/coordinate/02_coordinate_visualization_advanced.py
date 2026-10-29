#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""座標ドメインの高度な可視化サンプル

格子状に配置したセンサーを対象に、等高線・3D 表面・距離行列・クラスタリング・
近傍探索・勾配ベクトル場を可視化します。
"""

import os

import matplotlib.pyplot as plt
import numpy as np

from tascpy.core.column import Column
from tascpy.domains.coordinate import CoordinateCollection

IMGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs")
os.makedirs(IMGS_DIR, exist_ok=True)

GRID = 5
PITCH = 4.0


def create_sample_coordinate_data() -> CoordinateCollection:
    """5x5 の格子上に配置した 25 個の温度センサーのデータを作成"""
    t = np.linspace(0, 4 * np.pi, 100)
    columns, coordinates = {}, {}
    for i in range(GRID):
        for j in range(GRID):
            name = f"sensor_{i + 1}_{j + 1}"
            values = np.sin(t + i * np.pi / 5) * 5 + np.cos(1.5 * t + j * np.pi / 5) * 3 + 15
            columns[name] = Column(name, values.tolist(), unit="℃")
            coordinates[name] = {
                "x": i * PITCH,
                "y": j * PITCH,
                "z": 5.0 * np.exp(-((i - GRID / 2) ** 2 + (j - GRID / 2) ** 2) / 8),
            }
    return CoordinateCollection(columns, step=list(range(100)), coordinates=coordinates)


def idw_grid(points: np.ndarray, values: np.ndarray, resolution=(50, 50), power: float = 2.0):
    """逆距離加重法でセンサー範囲のグリッド上の値を補間"""
    xs = np.linspace(points[:, 0].min(), points[:, 0].max(), resolution[0])
    ys = np.linspace(points[:, 1].min(), points[:, 1].max(), resolution[1])
    gx, gy = np.meshgrid(xs, ys)
    d = np.hypot(gx[..., None] - points[:, 0], gy[..., None] - points[:, 1])
    w = 1.0 / np.maximum(d, 1e-12) ** power
    return gx, gy, (w * values).sum(axis=-1) / w.sum(axis=-1)


def save(fig, filename: str) -> None:
    fig.tight_layout()
    fig.savefig(os.path.join(IMGS_DIR, filename), dpi=100)
    plt.close(fig)


def main():
    data = create_sample_coordinate_data()
    print(f"センサー数: {len(data.columns)}, ステップ数: {len(data.step)}")

    points, names = data.get_coordinate_matrix()
    step = 50
    values = np.array([data[name].values[step] for name in names], dtype=float)
    gx, gy, grid = idw_grid(points, values)

    # 1. 等高線
    print("\n## 1. 等高線プロット（ステップ 50）")
    fig, ax = plt.subplots(figsize=(9, 8))
    cs = ax.contourf(gx, gy, grid, levels=15, cmap="viridis")
    ax.contour(gx, gy, grid, levels=15, colors="k", linewidths=0.3)
    ax.scatter(points[:, 0], points[:, 1], c="w", edgecolors="k", s=30)
    fig.colorbar(cs, ax=ax, label="温度 [℃]")
    ax.set_aspect("equal")
    ax.set_title("温度の等高線")
    save(fig, "coordinate_contour.png")

    # 2. 3D 表面
    print("## 2. 3D 表面プロット（ステップ 50）")
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(gx, gy, grid, cmap="viridis", alpha=0.8)
    ax.scatter(points[:, 0], points[:, 1], values, c="r", s=20)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("温度 [℃]")
    save(fig, "coordinate_3d_surface.png")

    # 3. 距離行列（CoordinateCollection.calculate_distance、z を含む 3D 距離）
    print("## 3. 距離行列（対角線上の 5 センサー）")
    subset = [f"sensor_{k}_{k}" for k in range(1, GRID + 1)]
    matrix = np.array([[data.calculate_distance(a, b) for b in subset] for a in subset])
    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(matrix, cmap="Blues")
    ax.set_xticks(range(len(subset)), subset, rotation=45, ha="right")
    ax.set_yticks(range(len(subset)), subset)
    for r in range(len(subset)):
        for c in range(len(subset)):
            ax.text(c, r, f"{matrix[r, c]:.1f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, label="距離")
    ax.set_title("センサー間距離")
    save(fig, "coordinate_distance_matrix.png")

    # 4. 空間クラスタリング（CoordinateOps.clusters）
    print("## 4. 空間クラスタリング（k-means, 4 クラスタ）")
    assignments = data.ops.clusters(n_clusters=4)
    labels = np.array([assignments[name] for name in names])
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(points[:, 0], points[:, 1], c=labels, cmap="tab10", s=120)
    ax.set_aspect("equal")
    ax.set_title("座標によるクラスタリング")
    save(fig, "coordinate_clustering.png")
    for cluster in sorted(set(labels)):
        members = [n for n in names if assignments[n] == cluster]
        print(f"   クラスタ {cluster}: {len(members)} センサー")

    # 5. 近傍探索（calculate_distance による距離順）
    center = "sensor_3_3"
    nearest = sorted((data.calculate_distance(center, n), n) for n in names if n != center)[:4]
    print(f"## 5. {center} の近傍: " + ", ".join(f"{n} ({d:.2f})" for d, n in nearest))

    # 6. 温度勾配のベクトル場
    print("## 6. 温度勾配のベクトル場（ステップ 50）")
    dy, dx = np.gradient(grid, gy[:, 0], gx[0, :])
    sl = (slice(None, None, 5), slice(None, None, 5))
    fig, ax = plt.subplots(figsize=(9, 8))
    mesh = ax.pcolormesh(gx, gy, grid, cmap="coolwarm", shading="auto")
    ax.quiver(gx[sl], gy[sl], dx[sl], dy[sl])
    fig.colorbar(mesh, ax=ax, label="温度 [℃]")
    ax.set_aspect("equal")
    ax.set_title("温度勾配")
    save(fig, "coordinate_vector_field.png")

    print(f"\n画像ファイルを保存しました: {IMGS_DIR}")


if __name__ == "__main__":
    main()
