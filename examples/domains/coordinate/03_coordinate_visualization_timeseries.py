#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""座標ドメインの時系列可視化サンプル"""

import os
import numpy as np
import matplotlib.pyplot as plt
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column

# 出力画像用のディレクトリパスを設定
IMGS_DIR = os.path.join(os.path.dirname(__file__), "imgs")
os.makedirs(IMGS_DIR, exist_ok=True)

# サンプルデータの作成
def create_sample_timeseries_data():
    """サンプルの時系列データを作成"""
    # ステップとタイムデータ
    n_steps = 100
    steps = list(range(n_steps))
    time_data = np.linspace(0, 10, n_steps).tolist()  # 0〜10秒
    
    # グリッド上に配置された16個のセンサー
    grid_size = 4
    sensor_columns = {}
    
    # 時間列を追加
    sensor_columns["time"] = Column(
        ch=None,
        name="time",
        unit="s",
        values=time_data
    )
    
    # 温度分布の時間的変化（移動する熱源をシミュレート）
    for i in range(grid_size):
        for j in range(grid_size):
            x = i * 3.0
            y = j * 3.0
            
            # 各センサーのデータ（移動する熱源からの距離に基づく温度変化）
            values = []
            for t in range(n_steps):
                # 熱源の位置（時間とともに移動）
                source_x = 4.5 + 4.5 * np.cos(t * 2 * np.pi / n_steps)
                source_y = 4.5 + 4.5 * np.sin(t * 2 * np.pi / n_steps)
                
                # センサーと熱源の距離
                dist = np.sqrt((x - source_x)**2 + (y - source_y)**2)
                
                # 距離に反比例する温度（+ノイズ）
                temperature = 25.0 + 50.0 / (1.0 + 0.5 * dist) + 0.5 * np.random.randn()
                values.append(temperature)
            
            # 列を作成
            col_name = f"sensor_{i+1}_{j+1}"
            sensor_columns[col_name] = Column(
                ch=None,
                name=col_name,
                unit="℃",  # 温度を想定
                values=values
            )
    
    # 通常のコレクションを作成
    collection = ColumnCollection(steps, sensor_columns)
    
    # 座標ドメインに変換
    coordinate_collection = collection.ops.as_domain("coordinate").end()
    
    # 各センサーに座標を設定
    for i in range(grid_size):
        for j in range(grid_size):
            x = i * 3.0
            y = j * 3.0
            
            col_name = f"sensor_{i+1}_{j+1}"
            coordinate_collection.set_column_coordinates(col_name, x=x, y=y, z=0.0)
    
    return coordinate_collection

# メイン処理
def main():
    # サンプルデータを作成
    timeseries_data = create_sample_timeseries_data()
    
    print("作成した時系列座標データ:")
    print(f"- ステップ数: {len(timeseries_data.step)}")
    print(f"- 列数: {len(timeseries_data.columns)}")
    print(f"- 時間範囲: {timeseries_data['time'].values[0]:.1f}〜{timeseries_data['time'].values[-1]:.1f} {timeseries_data['time'].unit}")
    
    # 座標情報を持つ列を表示
    columns_with_coords = timeseries_data.get_columns_with_coordinates()
    print(f"\n座標情報を持つ列: {len(columns_with_coords)} 個")
    
    print("\n# 時系列可視化機能のデモ")
    
    # 1. 時系列プロット
    print("\n## 1. plot_coordinate_timeseries - 通常の時系列プロット")
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    # 一部のセンサーだけを選択
    selected_sensors = ["sensor_1_1", "sensor_2_2", "sensor_3_3", "sensor_4_4"]
    selected_data = timeseries_data.ops.select_columns(
        columns=["time"] + selected_sensors
    ).end()
    
    selected_data.ops.plot_coordinate_timeseries(
        value_column="sensor_1_1",
        time_column="time",
        animate=False,
        ax=ax1
    ).end()
    plt.tight_layout()
    plt.savefig(os.path.join(IMGS_DIR, "coordinate_timeseries.png"), dpi=100)
    plt.close()
    
    # 2. 特定時点のコンター図
    print("\n## 2. 特定時点の空間分布 - 複数時点のスナップショット")
    fig2, axes = plt.subplots(2, 2, figsize=(14, 12))
    axes = axes.flatten()
    
    # 4つの時点におけるスナップショット
    time_points = [0, 25, 50, 75]  # ステップ
    titles = ["t = 0.0s", "t = 2.5s", "t = 5.0s", "t = 7.5s"]
    
    for i, (time_point, title, ax) in enumerate(zip(time_points, titles, axes)):
        step_data = timeseries_data.ops.select_step(steps=[time_point]).end()
        step_data.ops.plot_spatial_heatmap(
            value_column="sensor_1_1",  # どのセンサーを使っても、対応する時点の値が表示される
            resolution=(30, 30),
            show_points=True,
            ax=ax
        ).end()
        ax.set_title(title)
    
    plt.tight_layout()
    plt.savefig(os.path.join(IMGS_DIR, "coordinate_time_snapshots.png"), dpi=100)
    plt.close()
    
    # 3. 時間とともに変化するベクトル場
    print("\n## 3. 時間変化するベクトル場の例 - センサー間の温度勾配")
    # センサー間の温度勾配をベクトル場として可視化
    # 新しい列を作成してベクトル場を表現
    grid_size = 4
    step_data = timeseries_data.ops.select_step(steps=[50]).end()  # 中間時点を使用
    
    # 横方向と縦方向の温度勾配を計算
    grad_x = []
    grad_y = []
    
    for i in range(1, grid_size):
        for j in range(1, grid_size):
            # 現在の位置
            curr = step_data[f"sensor_{i}_{j}"].values[0]
            
            # 右側と左側の温度差（X方向勾配）
            if i < grid_size - 1:
                right = step_data[f"sensor_{i+1}_{j}"].values[0]
                dx = right - curr
            else:
                dx = 0
                
            # 上側と下側の温度差（Y方向勾配）
            if j < grid_size - 1:
                up = step_data[f"sensor_{i}_{j+1}"].values[0]
                dy = up - curr
            else:
                dy = 0
                
            grad_x.append(dx)
            grad_y.append(dy)
    
    # 勾配データをコレクションに追加
    grad_collection = step_data.clone()
    grad_collection.columns["grad_x"] = Column(
        ch=None,
        name="grad_x",
        unit="℃/m",
        values=[grad_x[0]] * len(step_data.step)  # 代表値として最初の勾配を使用
    )
    
    grad_collection.columns["grad_y"] = Column(
        ch=None,
        name="grad_y",
        unit="℃/m",
        values=[grad_y[0]] * len(step_data.step)  # 代表値として最初の勾配を使用
    )
    
    fig3, ax3 = plt.subplots(figsize=(10, 8))
    step_data.ops.plot_spatial_heatmap(
        value_column="sensor_1_1",
        resolution=(30, 30),
        show_points=False,
        ax=ax3
    ).end()
    
    # ベクトル場を重ねて表示
    grad_collection.ops.plot_vector_field(
        u_column="grad_x",
        v_column="grad_y",
        scale=0.1,
        ax=ax3,
        color="black",
        linewidth=1
    ).end()
    
    plt.tight_layout()
    plt.savefig(os.path.join(IMGS_DIR, "coordinate_gradient_field.png"), dpi=100)
    plt.close()
    
    # 4. アニメーションGIFを生成（コメントアウト - 実行時間が長くなる場合があるため）
    # アニメーションGIF用の設定
    print("\n## 4. アニメーション生成のコード例 (コメントアウト状態)")
    print("# アニメーションは実行時間が長くなる可能性があるためコメントアウトしています")
    print("# 必要に応じてコードのコメントを解除して実行してください")
    
    """
    # アニメーション生成コード
    import matplotlib.animation as animation
    
    print("\n## 4. plot_coordinate_animation - アニメーションGIF生成")
    fig4, ax4 = plt.subplots(figsize=(10, 8))
    
    # 間引いたステップでアニメーションを作成（処理を軽くするため）
    selected_steps = list(range(0, 100, 5))  # 5ステップごと
    selected_time_data = timeseries_data.ops.select_step(steps=selected_steps).end()
    
    # アニメーションの作成（座標の色が時間とともに変化）
    selected_time_data.ops.plot_coordinate_animation(
        value_column="sensor_1_1", 
        time_column="time",
        duration=5.0,
        interval=200,
        ax=ax4
    ).end()
    
    # アニメーションをGIFとして保存
    ani = animation.FuncAnimation(
        fig4, lambda i: None,  # ダミー関数
        frames=len(selected_steps),
        interval=200
    )
    ani.save(os.path.join(IMGS_DIR, "coordinate_animation.gif"), writer="pillow", dpi=80)
    plt.close()
    """
    
    print("\n画像ファイルを保存しました。")
    print(f"保存先: {IMGS_DIR}")
    
if __name__ == "__main__":
    main()