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
    
    print("1. 基本的な散布図")
    plt.figure(figsize=(8, 5))
    ops.plot(
        x_column="Displacement1", 
        y_column="Force1", 
        plot_type="scatter", 
        title="荷重-変位関係 (散布図)",
        xlabel="変位 (mm)",
        ylabel="荷重 (kN)",
        label="試験体1"
    ).end()
    plt.grid(True)
    plt.show()
    print("散布図を表示しました")
    print()
    
    print("2. 線グラフ")
    plt.figure(figsize=(8, 5))
    ops.plot(
        x_column="Displacement1", 
        y_column="Force1", 
        plot_type="line", 
        color="blue", 
        title="荷重-変位曲線 (線グラフ)",
        xlabel="変位 (mm)",
        ylabel="荷重 (kN)",
        label="試験体1",
        marker="o",
        linestyle="-",
        linewidth=2
    ).end()
    plt.grid(True)
    plt.show()
    print("線グラフを表示しました")
    print()
    
    print("3. 複数グラフの重ね描き")
    # 新しい図を作成
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 複数のグラフを同じAxesに描画
    ops.plot(
        x_column="Displacement1", 
        y_column="Force1", 
        plot_type="line", 
        color="blue", 
        label="試験体1 (荷重1)", 
        marker="o", 
        ax=ax
    ).end()
    ops.plot(
        x_column="Displacement2", 
        y_column="Force2", 
        plot_type="line", 
        color="red", 
        label="試験体2 (荷重2)", 
        marker="s", 
        ax=ax
    ).end()
    
    ax.set_title("2つの試験体の荷重-変位曲線の比較")
    ax.set_xlabel("変位 (mm)")
    ax.set_ylabel("荷重 (kN)")
    ax.grid(True)
    ax.legend()
    plt.show()
    print("複数線グラフを表示しました")
    print()
    
    print("4. サブプロット")
    # 2行1列のサブプロットを作成
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # 1つ目のサブプロット: 荷重-変位曲線
    ops.plot(
        x_column="Displacement1", 
        y_column="Force1", 
        plot_type="line", 
        color="blue", 
        label="試験体1", 
        ax=ax1
    ).end()
    ops.plot(
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
    # 近似的な剛性（傾き）を計算
    stiffness_result = ops.diff("Force1", "Displacement1", result_column="Stiffness1").end()
    stiffness_result = ops.diff("Force2", "Displacement2", result_column="Stiffness2").end()
    
    stiffness_result.ops.plot(
        x_column="Displacement1", 
        y_column="Stiffness1", 
        plot_type="line", 
        color="blue", 
        label="試験体1の剛性", 
        ax=ax2
    ).end()
    stiffness_result.ops.plot(
        x_column="Displacement2", 
        y_column="Stiffness2", 
        plot_type="line", 
        color="red", 
        label="試験体2の剛性", 
        ax=ax2
    ).end()
    ax2.set_title("剛性変化 (傾き dF/dx)")
    ax2.set_xlabel("変位 (mm)")
    ax2.set_ylabel("剛性 (kN/mm)")
    ax2.grid(True)
    ax2.legend()
    
    plt.tight_layout()
    plt.show()
    print("サブプロットを表示しました")
    print()
    
    print("5. 数学変換を適用して描画")
    # 応力-ひずみ関係の計算（モデル変換例）
    # 仮定: 断面積 = 50mm², 標点間距離 = 50mm
    area_mm2 = 50.0  # mm²
    length_mm = 50.0  # mm
    
    # 応力(MPa)とひずみ(%)の計算
    stress_strain_result = (
        ops.multiply("Force1", 1000)                            # kN -> N
        .divide("Force1*1000", area_mm2, result_column="Stress_MPa")  # N/mm² = MPa
        .multiply("Displacement1", 100)                         # mm -> 0.1mm
        .divide("Displacement1*100", length_mm, result_column="Strain_percent")  # % = (ΔL/L₀)*100
        .end()
    )
    
    # 応力-ひずみ線図の描画
    plt.figure(figsize=(10, 6))
    stress_strain_result.ops.plot(
        x_column="Strain_percent", 
        y_column="Stress_MPa", 
        plot_type="line", 
        color="green", 
        title="応力-ひずみ線図",
        xlabel="ひずみ (%)",
        ylabel="応力 (MPa)",
        label="試験体1",
        marker="o",
        linestyle="-",
        linewidth=2
    ).end()
    plt.grid(True)
    plt.show()
    print("応力-ひずみ線図を表示しました")

if __name__ == "__main__":
    print("-- ColumnCollectionのデータ可視化 --\n")
    demonstrate_plotting()