"""
ColumnCollectionのデータ可視化を示すサンプルコード
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from tascpy.core.collection import ColumnCollection

# 現在のスクリプトからの相対パスでデータファイルを取得
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_CSV_PATH = os.path.join(DATA_DIR, "sample.csv")

def load_sample_data():
    """サンプルデータの読み込みと拡張"""
    try:
        # CSVファイルからデータを読み込む
        collection = ColumnCollection.from_file(
            filepath=SAMPLE_CSV_PATH,
            format_name="csv",
            auto_detect_types=True
        )
        
        # データの前処理（拡張を含む）
        processed_data = preprocess_for_visualization(collection)
        return processed_data
    except FileNotFoundError:
        print(f"ファイル '{SAMPLE_CSV_PATH}' が見つかりません。")
        return create_sample_data()  # ファイルが見つからない場合は模擬データを作成

def create_sample_data():
    """CSVファイルがない場合の拡張サンプルデータを作成"""
    # 試験データを拡張して、より詳細な荷重-変位曲線を生成
    steps = list(range(1, 21))
    
    # 荷重-変位データ（2つの試験体を想定）
    force1 = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 7.0, 8.0, 9.0, 9.5, 9.8, 9.9, 10.0]
    force2 = [0.0, 1.2, 2.5, 3.8, 5.0, 6.2, 7.5, 8.8, 10.0, 11.2, 12.5, 13.8, 15.0, 16.5, 17.8, 18.5, 19.2, 19.8, 19.9, 20.0]
    disp1 = [0.00, 0.02, 0.04, 0.05, 0.07, 0.09, 0.11, 0.13, 0.16, 0.20, 0.25, 0.30, 0.35, 0.42, 0.48, 0.55, 0.60, 0.62, 0.64, 0.65]
    disp2 = [0.00, 0.08, 0.15, 0.22, 0.30, 0.38, 0.45, 0.55, 0.65, 0.78, 0.90, 1.05, 1.20, 1.40, 1.60, 1.80, 1.95, 2.10, 2.15, 2.20]
    
    columns = {
        "Force1": force1,
        "Force2": force2,
        "Displacement1": disp1,
        "Displacement2": disp2
    }
    
    metadata = {
        "date": ["2020/12/01"] * 20,
        "time": [f"{13}:{22+i:02d}:00" for i in range(20)],
        "title": "荷重-変位曲線",
        "test_info": "2つの試験体の比較データ"
    }
    
    # 自動型判定を使用してコレクションを作成
    return ColumnCollection(steps, columns, metadata, auto_detect_types=True)

def preprocess_for_visualization(collection):
    """可視化のためにデータを前処理（Noneの処理、データの拡張など）"""
    # 前処理としてNoneを含まない行だけを抽出
    ops = collection.ops
    no_none = ops.filter_by_value("Force1", lambda x: x is not None).end()
    
    # 補間によりデータポイントを増やす（より滑らかなプロットのため）
    if len(no_none) < 10:  # データが少ない場合は補間
        interpolated = ops.interpolate(point_count=20).end()
        return interpolated
    
    return no_none

def demonstrate_plotting():
    """データ可視化のデモンストレーション"""
    collection = load_sample_data()
    
    print("プロット用データの概要:")
    print(f"行数: {len(collection)}")
    print(f"列名: {list(collection.columns.keys())}")
    print(f"Force1サンプル: {collection['Force1'].values[:5]}...")
    print(f"Displacement1サンプル: {collection['Displacement1'].values[:5]}...")
    print()
    
    # 操作プロキシを取得
    ops = collection.ops
    
    print("1. select操作を使ってプロット用のデータを選択")
    # プロットに必要な列だけを選択
    plot_data = ops.select(columns=["Displacement1", "Force1"]).end()
    plot_ops = plot_data.ops
    
    # 選択したデータの内容を確認
    print(f"選択した列: {list(plot_data.columns.keys())}")
    print(f"行数: {len(plot_data)}")
    print()
    
    print("2. 基本的な散布図")
    fig, ax = plt.subplots(figsize=(8, 5))
    plot_ops.plot(
        x_column="Displacement1", 
        y_column="Force1", 
        plot_type="scatter", 
        label="試験体1",
        ax=ax
    ).end()
    ax.set_title("荷重-変位関係 (散布図)")
    ax.set_xlabel("変位 (mm)")
    ax.set_ylabel("荷重 (kN)")
    plt.grid(True)
    plt.show()
    print("散布図を表示しました")
    print()
    
    print("3. 線グラフとデータの間引き")
    # データ点が多すぎる場合は間引いてプロット（selectで何点かを選択）
    sample_indices = list(range(0, len(collection), 2))  # 2点ごとに選択
    sampled_data = ops.select(indices=sample_indices).end()
    sampled_ops = sampled_data.ops
    
    fig, ax = plt.subplots(figsize=(8, 5))
    sampled_ops.plot(
        x_column="Displacement1", 
        y_column="Force1", 
        plot_type="line", 
        color="blue", 
        label="試験体1 (間引き)",
        marker="o",
        linestyle="-",
        linewidth=2,
        ax=ax
    ).end()
    ax.set_title("荷重-変位曲線 (線グラフ、間引きあり)")
    ax.set_xlabel("変位 (mm)")
    ax.set_ylabel("荷重 (kN)")
    plt.grid(True)
    plt.show()
    print("間引きデータの線グラフを表示しました")
    print()
    
    print("4. 複数グラフの重ね描き（select_stepによる段階的な選択）")
    # 前半と後半のデータだけを選択してプロット
    step_first_half = list(range(1, 11))
    step_second_half = list(range(11, 21))
    
    # 前半データを選択
    first_half = ops.select_step(steps=step_first_half).end()
    # 後半データを選択
    second_half = ops.select_step(steps=step_second_half).end()
    
    # 新しい図を作成
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 前半のデータをプロット
    first_half.ops.plot(
        x_column="Displacement1", 
        y_column="Force1", 
        plot_type="line", 
        color="blue", 
        label="試験体1 (前半)", 
        marker="o", 
        ax=ax
    ).end()
    
    # 後半のデータをプロット
    second_half.ops.plot(
        x_column="Displacement1", 
        y_column="Force1", 
        plot_type="line", 
        color="green", 
        label="試験体1 (後半)", 
        marker="s", 
        ax=ax
    ).end()
    
    # 試験体2の全データをプロット
    ops.plot(
        x_column="Displacement2", 
        y_column="Force2", 
        plot_type="line", 
        color="red", 
        label="試験体2 (全体)", 
        marker="^", 
        ax=ax
    ).end()
    
    ax.set_title("試験体1の前半/後半データと試験体2の比較")
    ax.set_xlabel("変位 (mm)")
    ax.set_ylabel("荷重 (kN)")
    ax.grid(True)
    ax.legend()
    plt.show()
    print("複数線グラフを表示しました")
    print()
    
    print("5. サブプロット（selectで列を選択）")
    # 2行1列のサブプロットを作成
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # 試験体1のデータのみを選択
    specimen1_data = ops.select(columns=["Displacement1", "Force1"]).end()
    specimen1_ops = specimen1_data.ops
    
    # 試験体2のデータのみを選択
    specimen2_data = ops.select(columns=["Displacement2", "Force2"]).end()
    specimen2_ops = specimen2_data.ops
    
    # 1つ目のサブプロット: 2つの試験体の荷重-変位曲線
    specimen1_ops.plot(
        x_column="Displacement1", 
        y_column="Force1", 
        plot_type="line", 
        color="blue", 
        label="試験体1", 
        ax=ax1
    ).end()
    specimen2_ops.plot(
        x_column="Displacement2", 
        y_column="Force2", 
        plot_type="line", 
        color="red", 
        label="試験体2", 
        ax=ax1
    ).end()
    ax1.set_title("荷重-変位曲線")
    ax1.set_xlabel("変位 (mm)")
    ax1.set_ylabel("荷重 (kN)")
    ax1.grid(True)
    ax1.legend()
    
    # 2つ目のサブプロット: 剛性（傾き）の変化
    # diff関数が未実装のため、手動で近似的な剛性（傾き）を計算
    force1_values = collection['Force1'].values
    disp1_values = collection['Displacement1'].values
    force2_values = collection['Force2'].values
    disp2_values = collection['Displacement2'].values
    
    # 手動で傾き（剛性）を計算
    stiffness1 = []
    stiffness2 = []
    disp1_for_stiffness = []
    disp2_for_stiffness = []
    
    # 前後の点から傾きを計算 (中央差分法)
    for i in range(1, len(force1_values) - 1):
        if (None not in [force1_values[i-1], force1_values[i+1], disp1_values[i-1], disp1_values[i+1]] and 
            disp1_values[i+1] - disp1_values[i-1] != 0):
            slope = (force1_values[i+1] - force1_values[i-1]) / (disp1_values[i+1] - disp1_values[i-1])
            stiffness1.append(slope)
            disp1_for_stiffness.append(disp1_values[i])
    
    for i in range(1, len(force2_values) - 1):
        if (None not in [force2_values[i-1], force2_values[i+1], disp2_values[i-1], disp2_values[i+1]] and 
            disp2_values[i+1] - disp2_values[i-1] != 0):
            slope = (force2_values[i+1] - force2_values[i-1]) / (disp2_values[i+1] - disp2_values[i-1])
            stiffness2.append(slope)
            disp2_for_stiffness.append(disp2_values[i])
    
    # 剛性グラフの描画
    ax2.plot(disp1_for_stiffness, stiffness1, 'bo-', label="試験体1の剛性")
    ax2.plot(disp2_for_stiffness, stiffness2, 'ro-', label="試験体2の剛性")
    ax2.set_title("剛性変化 (傾き dF/dx)")
    ax2.set_xlabel("変位 (mm)")
    ax2.set_ylabel("剛性 (kN/mm)")
    ax2.grid(True)
    ax2.legend()
    
    plt.tight_layout()
    plt.show()
    print("サブプロットを表示しました")
    print()
    
    print("6. select_stepを使った特定の区間のデータ変換と可視化")
    # 特定のステップ範囲だけを選択し、応力-ひずみに変換
    important_steps = list(range(5, 16))  # ステップ5～15
    step_selected = ops.select_step(steps=important_steps).end()
    step_ops = step_selected.ops
    
    # 応力-ひずみ関係の計算（モデル変換例）
    # 仮定: 断面積 = 50mm², 標点間距離 = 50mm
    area_mm2 = 50.0  # mm²
    length_mm = 50.0  # mm
    
    # 応力(MPa)とひずみ(%)の計算
    stress_strain_result = (
        step_ops.multiply("Force1", 1000)                            # kN -> N
        .divide("Force1*1000", area_mm2, result_column="Stress_MPa")  # N/mm² = MPa
        .multiply("Displacement1", 100)                         # mm -> 0.1mm
        .divide("Displacement1*100", length_mm, result_column="Strain_percent")  # % = (ΔL/L₀)*100
        .end()
    )
    
    # 応力-ひずみ線図の描画
    fig, ax = plt.subplots(figsize=(10, 6))
    stress_strain_result.ops.plot(
        x_column="Strain_percent", 
        y_column="Stress_MPa", 
        plot_type="line", 
        color="green", 
        label="選択したステップ区間",
        marker="o",
        linestyle="-",
        linewidth=2,
        ax=ax
    ).end()
    ax.set_title("選択したステップ区間の応力-ひずみ線図")
    ax.set_xlabel("ひずみ (%)")
    ax.set_ylabel("応力 (MPa)")
    plt.grid(True)
    plt.show()
    print("応力-ひずみ線図を表示しました")

if __name__ == "__main__":
    print("-- ColumnCollectionのデータ可視化 --\n")
    demonstrate_plotting()
