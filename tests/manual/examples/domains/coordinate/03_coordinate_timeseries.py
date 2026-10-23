#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""座標データの時系列可視化サンプル

円軌道上を移動する熱源を 4x4 のセンサーで計測したデータを想定し、
センサーごとの時系列・時刻ごとの空間分布・温度勾配を可視化します。
"""

import os

import matplotlib.pyplot as plt
import numpy as np

from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
from tascpy.domains.coordinate import CoordinateCollection

IMGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs")
os.makedirs(IMGS_DIR, exist_ok=True)

N_STEPS = 100
GRID = 4
PITCH = 3.0


def create_sample_timeseries_data() -> CoordinateCollection:
    """移動する熱源の温度データを作成し、座標ドメインに変換"""
    rng = np.random.default_rng(0)
    t = np.arange(N_STEPS)
    source_x = 4.5 + 4.5 * np.cos(t * 2 * np.pi / N_STEPS)
    source_y = 4.5 + 4.5 * np.sin(t * 2 * np.pi / N_STEPS)

    # "time" はインデックス列（時刻）の予約名なので、経過時間の列は別名にする
    columns = {"elapsed": Column("elapsed", np.linspace(0, 10, N_STEPS).tolist(), unit="s")}
    coordinates = {}
    for i in range(GRID):
        for j in range(GRID):
            name = f"sensor_{i + 1}_{j + 1}"
            x, y = i * PITCH, j * PITCH
            dist = np.hypot(x - source_x, y - source_y)
            values = 25.0 + 50.0 / (1.0 + 0.5 * dist) + 0.5 * rng.standard_normal(N_STEPS)
            columns[name] = Column(name, values.tolist(), unit="℃")
            coordinates[name] = {"x": x, "y": y, "z": 0.0}

    collection = ColumnCollection(columns, step=list(range(N_STEPS)))
    # as_coordinate で座標ドメインに変換（型付きで CoordinateOps が返る）
    return collection.ops.as_coordinate(coordinates=coordinates).end()


def spatial_values(collection: CoordinateCollection, step_index: int):
    """指定ステップでのセンサー座標と値を取得"""
    points, names = collection.get_coordinate_matrix()
    values = np.array([collection[n].values[step_index] for n in names], dtype=float)
    return points, names, values


def idw_grid(points: np.ndarray, values: np.ndarray, resolution=(40, 40), power: float = 2.0):
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
    data = create_sample_timeseries_data()
    print("時系列座標コレクション:")
    print(f"- ステップ数: {len(data.step)}")
    print(f"- 座標付きセンサー数: {len(data.get_columns_with_coordinates())}")

    # 1. 角のセンサーの時系列（CorePlotter.plot を elapsed 列に対して使用）
    print("\n## 1. センサーごとの時系列プロット")
    corners = ["sensor_1_1", "sensor_1_4", "sensor_4_1", "sensor_4_4"]
    fig, ax = plt.subplots(figsize=(12, 6))
    for name in corners:
        data.plot.plot(y_column=name, x_column="elapsed", ax=ax, label=name)
    ax.set_ylabel("温度 [℃]")
    ax.legend()
    ax.set_title("角のセンサーの温度変化")
    save(fig, "coordinate_timeseries.png")

    # 2. 4 時刻の空間分布スナップショット
    print("## 2. 時刻ごとの空間分布スナップショット")
    snapshots = [0, 25, 50, 75]
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    vmin = min(spatial_values(data, s)[2].min() for s in snapshots)
    vmax = max(spatial_values(data, s)[2].max() for s in snapshots)
    for ax, step_index in zip(axes.flat, snapshots):
        points, _, values = spatial_values(data, step_index)
        gx, gy, grid = idw_grid(points, values)
        mesh = ax.pcolormesh(gx, gy, grid, cmap="hot", vmin=vmin, vmax=vmax, shading="auto")
        ax.scatter(points[:, 0], points[:, 1], c="b", s=15)
        ax.set_aspect("equal")
        ax.set_title(f"t = {data['elapsed'][step_index]:.1f} s")
    fig.colorbar(mesh, ax=axes, label="温度 [℃]")
    fig.savefig(os.path.join(IMGS_DIR, "coordinate_time_snapshots.png"), dpi=100)
    plt.close(fig)

    # 3. 中間時刻の温度勾配
    print("## 3. 温度勾配（ステップ 50）")
    points, _, values = spatial_values(data, 50)
    gx, gy, grid = idw_grid(points, values)
    dy, dx = np.gradient(grid, gy[:, 0], gx[0, :])
    sl = (slice(None, None, 4), slice(None, None, 4))
    fig, ax = plt.subplots(figsize=(9, 8))
    mesh = ax.pcolormesh(gx, gy, grid, cmap="hot", shading="auto")
    ax.quiver(gx[sl], gy[sl], dx[sl], dy[sl], color="cyan")
    fig.colorbar(mesh, ax=ax, label="温度 [℃]")
    ax.set_aspect("equal")
    ax.set_title("温度勾配（ステップ 50）")
    save(fig, "coordinate_gradient_field.png")

    # 4. 各時刻で最も温度が高いセンサー（熱源の追跡）
    print("## 4. 最高温度センサーの推移")
    for step_index in snapshots:
        _, names, values = spatial_values(data, step_index)
        hottest = names[int(np.argmax(values))]
        print(f"   ステップ {step_index:3d}: {hottest} ({values.max():.1f} ℃)")

    print(f"\n画像ファイルを保存しました: {IMGS_DIR}")


if __name__ == "__main__":
    main()
