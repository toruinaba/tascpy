#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""座標軸に沿った値の可視化サンプル"""

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
    # 直線上に配置された10個のセンサー
    n_sensors = 10
    sensor_columns = {}
    
    for i in range(n_sensors):
        x = i * 2.0  # X座標を等間隔に配置
        y = 0.0      # Y座標は0に固定
        z = 0.0      # Z座標も0に固定
        
        # 各センサーのデータ（時間とともに変化する値、X座標に依存）
        base_temp = 20 + (i * 0.5)  # 基本温度はX座標に応じて上昇
        noise = np.random.normal(0, 0.5, 100)  # ランダムノイズ
        trend = np.sin(np.linspace(0, 2*np.pi, 100)) * 2  # 時間変化の傾向
        
        values = base_temp + trend + noise
        
        # 列を作成
        col_name = f"sensor_{i+1}"
        sensor_columns[col_name] = Column(
            ch=None,
            name=col_name,
            unit="℃",  # 温度を想定
            values=values.tolist()
        )
    
    # 通常のコレクションを作成
    collection = ColumnCollection(steps, sensor_columns)
    
    # 座標ドメインに変換
    coordinate_collection = CoordinateCollection(
        step=collection.step, 
        columns={name: col.clone() for name, col in collection.columns.items()},
        metadata=collection.metadata.copy() if collection.metadata else {}
    )
    
    # 各センサーに座標を設定
    for i in range(n_sensors):
        x = i * 2.0
        y = 0.0
        z = 0.0
        
        col_name = f"sensor_{i+1}"
        coordinate_collection.set_column_coordinates(col_name, x=x, y=y, z=z)
    
    return coordinate_collection

# メイン処理
def main():
    # サンプルデータを作成
    coordinate_data = create_sample_coordinate_data()
    
    print("作成した座標コレクション:")
    print(f"- ステップ数: {len(coordinate_data.step)}")
    print(f"- センサー数: {len(coordinate_data.columns)}")
    
    # 座標情報を持つ列をリスト化
    columns_with_coords = coordinate_data.get_columns_with_coordinates()
    print(f"\n座標情報を持つ列: {len(columns_with_coords)} 個")
    for col in columns_with_coords[:5]:  # 最初の5つだけ表示
        x, y, z = coordinate_data.get_column_coordinates(col)
        print(f"- {col}: x={x:.2f}, y={y:.2f}, z={z}")
    
    print("\n# 座標軸に沿った値の可視化")
    
    # 1. 全センサーのX座標と温度の関係をプロット（特定のステップ）
    print("\n## 1. plot_coordinate_axis - X座標に沿った温度分布（ステップ50）")
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    plot_coordinate_axis(
        coordinate_data,
        column_names=columns_with_coords,  # すべてのセンサー列を指定
        coordinate_axis="x",               # X座標を使用
        axis_orientation="coord_value",    # X座標を横軸、値を縦軸
        plot_type="line",                  # 線グラフ
        marker="o",                        # マーカーを表示
        step_index=50,                     # ステップ50のデータを使用
        series_name="温度分布(ステップ50)",    # 系列名を指定
        color="red",                       # 線の色
        ax=ax1
    )
    plt.tight_layout()
    plt.savefig(os.path.join(IMGS_DIR, "x_axis_temperature_line.png"), dpi=100)
    plt.close()
    
    # 2. 全センサーのX座標と温度の関係を散布図でプロット（別のステップ）
    print("\n## 2. plot_coordinate_axis - X座標に沿った温度分布（ステップ75、散布図）")
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    plot_coordinate_axis(
        coordinate_data,
        column_names=columns_with_coords,
        coordinate_axis="x",
        axis_orientation="coord_value",
        plot_type="scatter",               # 散布図
        step_index=75,                     # ステップ75のデータを使用
        series_name="温度分布(ステップ75)",
        color="blue",
        s=100,                             # マーカーサイズを大きく
        ax=ax2
    )
    plt.tight_layout()
    plt.savefig(os.path.join(IMGS_DIR, "x_axis_temperature_scatter.png"), dpi=100)
    plt.close()
    
    # 3. 全センサーのX座標と温度の関係を棒グラフでプロット（別のステップ）
    print("\n## 3. plot_coordinate_axis - X座標に沿った温度分布（ステップ25、棒グラフ）")
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    plot_coordinate_axis(
        coordinate_data,
        column_names=columns_with_coords,
        coordinate_axis="x",
        axis_orientation="coord_value",
        plot_type="bar",                   # 棒グラフ
        step_index=25,                     # ステップ25のデータを使用
        series_name="温度分布(ステップ25)",
        color="green",
        ax=ax3
    )
    plt.tight_layout()
    plt.savefig(os.path.join(IMGS_DIR, "x_axis_temperature_bar.png"), dpi=100)
    plt.close()
    
    # 4. 値を横軸、X座標を縦軸にした場合（向きを変更）
    print("\n## 4. plot_coordinate_axis - 温度とX座標の関係（向きを変更）")
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    plot_coordinate_axis(
        coordinate_data,
        column_names=columns_with_coords,
        coordinate_axis="x",
        axis_orientation="value_coord",    # 値を横軸、座標を縦軸
        plot_type="line",
        marker="s",                        # 正方形マーカー
        step_index=50,
        series_name="温度分布(向きを変更)",
        color="purple",
        ax=ax4
    )
    plt.tight_layout()
    plt.savefig(os.path.join(IMGS_DIR, "temperature_x_axis_reversed.png"), dpi=100)
    plt.close()
    
    # 5. 特定のセンサーだけを選択してプロット
    print("\n## 5. plot_coordinate_axis - 選択したセンサーのみの温度分布")
    fig5, ax5 = plt.subplots(figsize=(10, 6))
    selected_sensors = ["sensor_1", "sensor_3", "sensor_5", "sensor_7", "sensor_9"]
    plot_coordinate_axis(
        coordinate_data,
        column_names=selected_sensors,      # 選択したセンサーのみ
        coordinate_axis="x",
        axis_orientation="coord_value",
        plot_type="scatter",
        marker="^",                         # 三角形マーカー
        step_index=50,
        series_name="選択センサーの温度分布",
        color="orange",
        s=150,                              # マーカーサイズをさらに大きく
        ax=ax5
    )
    plt.tight_layout()
    plt.savefig(os.path.join(IMGS_DIR, "selected_sensors_temperature.png"), dpi=100)
    plt.close()
    
    print("\n画像ファイルを保存しました。")
    print(f"保存先: {IMGS_DIR}")

if __name__ == "__main__":
    main()