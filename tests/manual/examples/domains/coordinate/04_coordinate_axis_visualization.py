#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""座標軸に沿った値の可視化サンプル

直線上に並んだセンサーの値を、X 座標を横軸にしてプロットします。
特定ステップの抽出には `ops.select`、描画には `plot.plot_const_x` を使います。
"""

import os

import matplotlib.pyplot as plt
import numpy as np

from tascpy.core.column import Column
from tascpy.domains.coordinate import CoordinateCollection

IMGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs")
os.makedirs(IMGS_DIR, exist_ok=True)


def create_sample_coordinate_data() -> CoordinateCollection:
    """X 軸上に等間隔に並んだ 10 個の温度センサーのデータを作成"""
    rng = np.random.default_rng(0)
    trend = np.sin(np.linspace(0, 2 * np.pi, 100)) * 2
    columns, coordinates = {}, {}
    for i in range(10):
        name = f"sensor_{i + 1}"
        values = 20 + i * 0.5 + trend + rng.normal(0, 0.5, 100)
        columns[name] = Column(ch=None, name=name, unit="℃", values=values.tolist())
        coordinates[name] = {"x": i * 2.0, "y": 0.0, "z": 0.0}
    return CoordinateCollection(step=list(range(100)), columns=columns, coordinates=coordinates)


def save(fig, filename: str) -> None:
    fig.tight_layout()
    fig.savefig(os.path.join(IMGS_DIR, filename), dpi=100)
    plt.close(fig)


def main():
    data = create_sample_coordinate_data()
    print("作成した座標コレクション:")
    print(f"- ステップ数: {len(data.step)}")
    print(f"- センサー数: {len(data.columns)}")

    points, names = data.get_coordinate_matrix()
    x_coords = points[:, 0]
    for name, x in list(zip(names, x_coords))[:5]:
        print(f"- {name}: x={x:.2f}")

    print("\n# 座標軸に沿った値の可視化")

    # 1. ステップ 50 の X 方向分布（折れ線）
    print("\n## 1. X 座標に沿った温度分布（ステップ 50）")
    fig, ax = plt.subplots(figsize=(10, 6))
    data.ops.select(indices=[50]).end().plot.plot_const_x(
        x_coords, names, ax=ax, x_label="X [mm]", y_label="温度 [℃]",
        title="温度分布（ステップ 50）", marker="o", color="red",
    )
    save(fig, "x_axis_temperature_line.png")

    # 2. ステップ 75 の X 方向分布（散布図）
    print("## 2. X 座標に沿った温度分布（ステップ 75、散布図）")
    step_75 = data.ops.select(indices=[75]).end()
    temps_75 = np.array([step_75[n].values[0] for n in names], dtype=float)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(x_coords, temps_75, s=100, color="blue")
    ax.set_xlabel("X [mm]")
    ax.set_ylabel("温度 [℃]")
    ax.set_title("温度分布（ステップ 75）")
    save(fig, "x_axis_temperature_scatter.png")

    # 3. ステップ 25 の X 方向分布（棒グラフ）
    print("## 3. X 座標に沿った温度分布（ステップ 25、棒グラフ）")
    step_25 = data.ops.select(indices=[25]).end()
    temps_25 = np.array([step_25[n].values[0] for n in names], dtype=float)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x_coords, temps_25, width=1.5, color="green")
    ax.set_xlabel("X [mm]")
    ax.set_ylabel("温度 [℃]")
    ax.set_title("温度分布（ステップ 25）")
    save(fig, "x_axis_temperature_bar.png")

    # 4. 軸の向きを入れ替え（温度を横軸、X 座標を縦軸）
    print("## 4. 温度と X 座標の関係（軸を入れ替え）")
    temps_50 = np.array([data[n].values[50] for n in names], dtype=float)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(temps_50, x_coords, marker="o", color="purple")
    ax.set_xlabel("温度 [℃]")
    ax.set_ylabel("X [mm]")
    ax.set_title("温度分布（ステップ 50、軸入れ替え）")
    save(fig, "temperature_x_axis_reversed.png")

    # 5. 選択したセンサーのみ（偶数番目）を複数ステップで比較
    print("## 5. 選択したセンサーのみの温度分布")
    selected = names[::2]
    selected_x = x_coords[::2]
    fig, ax = plt.subplots(figsize=(10, 6))
    for step_index, color in [(0, "tab:blue"), (50, "tab:orange"), (99, "tab:green")]:
        data.ops.select(columns=selected, indices=[step_index]).end().plot.plot_const_x(
            selected_x, selected, ax=ax, x_label="X [mm]", y_label="温度 [℃]",
            title="選択センサーの温度分布", marker="s", color=color, label=f"ステップ {step_index}",
        )
    ax.legend()
    save(fig, "selected_sensors_temperature.png")

    print(f"\n画像ファイルを保存しました: {IMGS_DIR}")


if __name__ == "__main__":
    main()
