"""
ColumnCollectionのデータ可視化を示すサンプルコード

このサンプルではtascpyライブラリのプロット機能を活用し、
チェーンメソッドを用いてデータの可視化をシンプルかつ効果的に行う方法を示します。
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from tascpy.core.collection import ColumnCollection

# 現在のスクリプトからの相対パスでデータファイルを取得
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_CSV_PATH = os.path.join(DATA_DIR, "load_displacement_sample.csv")

print("-- ColumnCollectionのデータ可視化 --\n")

# ----------------------------------------------------
# データの準備
# ----------------------------------------------------

# CSVファイルからデータを読み込む
try:
    print("CSVファイルからデータを読み込みます...")
    collection = ColumnCollection.from_file(
        filepath=SAMPLE_CSV_PATH, format_name="csv", auto_detect_types=True
    )

    # 試験体2のデータがない場合、合成データを作成して追加
    if "Force2" not in collection.columns:
        print("試験体2のデータが見つかりません。合成データを作成します...")
        # 既存データから試験体2用の合成データを作成
        if "Force1" in collection.columns and "Displacement1" in collection.columns:
            # Force1とDisplacement1からスケーリングしたデータを作成
            force1_values = collection["Force1"].values
            disp1_values = collection["Displacement1"].values

            # 2倍の力でほぼ同じ変位（剛性が大きい材料を模擬）
            force2_values = [
                val * 1.8 if val is not None else None for val in force1_values
            ]
            # 0.8倍の変位（より強い材料を模擬）
            disp2_values = [
                val * 0.85 if val is not None else None for val in disp1_values
            ]

            # 新しいカラムを追加
            collection = collection.clone()
            collection.add_column("Force2", force2_values)
            collection.add_column("Displacement2", disp2_values)
            print("  試験体2の合成データを追加しました")
except FileNotFoundError:
    print(f"ファイル '{SAMPLE_CSV_PATH}' が見つかりません。模擬データを作成します。")
    # 試験データを作成（荷重-変位曲線を想定）
    steps = list(range(1, 21))

    # 荷重-変位データ（2つの試験体を想定）
    force1 = [
        0.0,
        0.5,
        1.0,
        1.5,
        2.0,
        2.5,
        3.0,
        3.5,
        4.0,
        4.5,
        5.0,
        5.5,
        6.0,
        7.0,
        8.0,
        9.0,
        9.5,
        9.8,
        9.9,
        10.0,
    ]
    force2 = [
        0.0,
        1.2,
        2.5,
        3.8,
        5.0,
        6.2,
        7.5,
        8.8,
        10.0,
        11.2,
        12.5,
        13.8,
        15.0,
        16.5,
        17.8,
        18.5,
        19.2,
        19.8,
        19.9,
        20.0,
    ]
    disp1 = [
        0.00,
        0.02,
        0.04,
        0.05,
        0.07,
        0.09,
        0.11,
        0.13,
        0.16,
        0.20,
        0.25,
        0.30,
        0.35,
        0.42,
        0.48,
        0.55,
        0.60,
        0.62,
        0.64,
        0.65,
    ]
    disp2 = [
        0.00,
        0.08,
        0.15,
        0.22,
        0.30,
        0.38,
        0.45,
        0.55,
        0.65,
        0.78,
        0.90,
        1.05,
        1.20,
        1.40,
        1.60,
        1.80,
        1.95,
        2.10,
        2.15,
        2.20,
    ]

    columns = {
        "Force1": force1,
        "Force2": force2,
        "Displacement1": disp1,
        "Displacement2": disp2,
    }

    metadata = {
        "date": ["2020/12/01"] * 20,
        "time": [f"{13}:{22+i:02d}:00" for i in range(20)],
        "title": "荷重-変位曲線",
        "test_info": "2つの試験体の比較データ",
    }

    # 自動型判定を使用してコレクションを作成
    collection = ColumnCollection(steps, columns, metadata, auto_detect_types=True)

# データの前処理（None値を含まないデータに変換）
print("データの前処理を行います...")

# ops プロパティからメソッドチェーンを開始できるようにする
ops = collection.ops

# None値を含む行を除外するフィルタリング
if "Force1" in collection.columns and any(
    x is None for x in collection["Force1"].values
):
    collection = ops.filter_by_value("Force1", lambda x: x is not None).end()

# データが少ない場合は補間でポイントを増やす
if len(collection) < 10:
    collection = ops.interpolate(point_count=20).end()
    print("データポイントが少ないため、補間処理によりポイント数を増やしました")

# データの概要を表示
print("\nプロット用データの概要:")
print(f"行数: {len(collection)}")
print(f"列名: {list(collection.columns.keys())}")
print(f"Force1サンプル: {collection['Force1'].values[:5]}...")
print(f"Displacement1サンプル: {collection['Displacement1'].values[:5]}...")
print()

# ----------------------------------------------------
# 1. 基本的な散布図による可視化
# ----------------------------------------------------
print("1. 基本的な散布図")
# チェーンメソッドでプロット用のデータを選択し、散布図を作成
fig, ax = plt.subplots(figsize=(8, 5))

# メソッドチェーンで必要な列だけを選択してから散布図をプロット
# axを渡すことでplt.showは呼び出されない
(
    collection.ops.select(columns=["Displacement1", "Force1"])
    .plot(
        x_column="Displacement1",
        y_column="Force1",
        plot_type="scatter",
        label="試験体1",
        ax=ax,
    )
    .end()
)

# グラフの装飾
ax.set_title("荷重-変位関係 (散布図)")
ax.set_xlabel("変位 (mm)")
ax.set_ylabel("荷重 (kN)")
plt.grid(True)
# 明示的にplt.showを呼び出して表示
plt.show()
print("散布図を表示しました")
print()

# ----------------------------------------------------
# 2. 線グラフとデータの間引き
# ----------------------------------------------------
print("2. 線グラフとデータの間引き")
# データ点が多すぎる場合は間引いてプロットするテクニック

# メソッドチェーンでデータを間引いてから線グラフをプロット
fig, ax = plt.subplots(figsize=(8, 5))

# チェーンメソッドの特徴を活かし、データの選択と可視化を一連の流れで実現
# axを渡すことでplt.showは呼び出されない
(
    collection.ops.select(
        indices=list(range(0, len(collection), 2))
    )  # 2点ごとに選択して間引く
    .plot(
        x_column="Displacement1",
        y_column="Force1",
        plot_type="line",
        color="blue",
        label="試験体1 (間引き)",
        marker="o",
        linestyle="-",
        linewidth=2,
        ax=ax,
    )
    .end()
)

# グラフの装飾
ax.set_title("荷重-変位曲線 (線グラフ、間引きあり)")
ax.set_xlabel("変位 (mm)")
ax.set_ylabel("荷重 (kN)")
plt.grid(True)
# 明示的にplt.showを呼び出して表示
plt.show()
print("間引きデータの線グラフを表示しました")
print()

# ----------------------------------------------------
# 3. 複数グラフの重ね描き（select_stepによる段階的な選択）
# ----------------------------------------------------
print("3. 複数グラフの重ね描き（select_stepによる段階的な選択）")

# データを前半と後半に分けるためのステップ定義
step_first_half = list(range(1, 11))  # 前半ステップ
step_second_half = (
    list(range(11, 21))
    if len(collection.step.values) >= 20
    else list(range(11, len(collection.step.values) + 1))
)  # 後半ステップ

# 新しい図を作成
fig, ax = plt.subplots(figsize=(10, 6))

# 前半データを選択してプロット（メソッドチェーンで操作）
# axを渡すことでplt.showは呼び出されない
(
    collection.ops.select_step(steps=step_first_half)
    .plot(
        x_column="Displacement1",
        y_column="Force1",
        plot_type="line",
        color="blue",
        label="試験体1 (前半)",
        marker="o",
        ax=ax,
    )
    .end()
)

# 後半データを選択してプロット（メソッドチェーンで操作）
# axを渡すことでplt.showは呼び出されない
(
    collection.ops.select_step(steps=step_second_half)
    .plot(
        x_column="Displacement1",
        y_column="Force1",
        plot_type="line",
        color="green",
        label="試験体1 (後半)",
        marker="s",
        ax=ax,
    )
    .end()
)

# 試験体2の全データをプロット（メソッドチェーンで操作）
# axを渡すことでplt.showは呼び出されない
if "Force2" in collection.columns and "Displacement2" in collection.columns:
    (
        collection.ops.plot(
            x_column="Displacement2",
            y_column="Force2",
            plot_type="line",
            color="red",
            label="試験体2 (全体)",
            marker="^",
            ax=ax,
        ).end()
    )

# グラフの装飾
ax.set_title("試験体1の前半/後半データと試験体2の比較")
ax.set_xlabel("変位 (mm)")
ax.set_ylabel("荷重 (kN)")
ax.grid(True)
ax.legend()
# 明示的にplt.showを呼び出して表示
plt.show()
print("複数線グラフを表示しました")
print()

# ----------------------------------------------------
# 4. サブプロット（複数のグラフを組み合わせた可視化）
# ----------------------------------------------------
print("4. サブプロット（selectで列を選択）")
# 2行1列のサブプロットを作成
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# チェーンメソッドで試験体1のデータを選択してプロット
# axを渡すことでplt.showは呼び出されない
(
    collection.ops.select(columns=["Displacement1", "Force1"])
    .plot(
        x_column="Displacement1",
        y_column="Force1",
        plot_type="line",
        color="blue",
        label="試験体1",
        ax=ax1,
    )
    .end()
)

# 試験体2のデータが存在する場合はチェーンメソッドでプロット
# axを渡すことでplt.showは呼び出されない
if "Force2" in collection.columns and "Displacement2" in collection.columns:
    (
        collection.ops.select(columns=["Displacement2", "Force2"])
        .plot(
            x_column="Displacement2",
            y_column="Force2",
            plot_type="line",
            color="red",
            label="試験体2",
            ax=ax1,
        )
        .end()
    )

# 上部サブプロットの装飾
ax1.set_title("荷重-変位曲線")
ax1.set_xlabel("変位 (mm)")
ax1.set_ylabel("荷重 (kN)")
ax1.grid(True)
ax1.legend()

# 下部サブプロット: 剛性（傾き）の変化
# チェーンメソッドでdiff操作を実行（実装されている場合）
try:
    # 試験体1の剛性
    stiffness_data1 = (
        collection.ops.select(columns=["Displacement1", "Force1"])
        .diff("Force1", "Displacement1", result_column="Stiffness1")
        .end()
    )

    # 試験体1の剛性をプロット
    ax2.plot(
        stiffness_data1["Displacement1"].values[1:],
        stiffness_data1["Stiffness1"].values,
        "bo-",
        label="試験体1の剛性",
    )

    # 試験体2の剛性（存在する場合）
    if "Force2" in collection.columns and "Displacement2" in collection.columns:
        stiffness_data2 = (
            collection.ops.select(columns=["Displacement2", "Force2"])
            .diff("Force2", "Displacement2", result_column="Stiffness2")
            .end()
        )

        # 試験体2の剛性をプロット
        ax2.plot(
            stiffness_data2["Displacement2"].values[1:],
            stiffness_data2["Stiffness2"].values,
            "ro-",
            label="試験体2の剛性",
        )

except (AttributeError, ValueError):
    # diffメソッドが実装されていない場合や値が不十分な場合は手動で近似計算
    print("diffメソッドが利用できないため、手動で剛性を計算します")

    # 試験体1の剛性を計算（中央差分法）
    force1_values = collection["Force1"].values
    disp1_values = collection["Displacement1"].values

    stiffness1 = []
    disp1_for_stiffness = []

    # 前後の点から傾きを計算
    for i in range(1, len(force1_values) - 1):
        if (
            None
            not in [
                force1_values[i - 1],
                force1_values[i + 1],
                disp1_values[i - 1],
                disp1_values[i + 1],
            ]
            and disp1_values[i + 1] - disp1_values[i - 1] != 0
        ):

            slope = (force1_values[i + 1] - force1_values[i - 1]) / (
                disp1_values[i + 1] - disp1_values[i - 1]
            )
            stiffness1.append(slope)
            disp1_for_stiffness.append(disp1_values[i])

    # 試験体1の剛性をプロット
    ax2.plot(disp1_for_stiffness, stiffness1, "bo-", label="試験体1の剛性")

    # 試験体2の剛性を計算（存在する場合）
    if "Force2" in collection.columns and "Displacement2" in collection.columns:
        force2_values = collection["Force2"].values
        disp2_values = collection["Displacement2"].values

        stiffness2 = []
        disp2_for_stiffness = []

        for i in range(1, len(force2_values) - 1):
            if (
                None
                not in [
                    force2_values[i - 1],
                    force2_values[i + 1],
                    disp2_values[i - 1],
                    disp2_values[i + 1],
                ]
                and disp2_values[i + 1] - disp2_values[i - 1] != 0
            ):

                slope = (force2_values[i + 1] - force2_values[i - 1]) / (
                    disp2_values[i + 1] - disp2_values[i - 1]
                )
                stiffness2.append(slope)
                disp2_for_stiffness.append(disp2_values[i])

        # 試験体2の剛性をプロット
        ax2.plot(disp2_for_stiffness, stiffness2, "ro-", label="試験体2の剛性")

# 下部サブプロットの装飾
ax2.set_title("剛性変化 (傾き dF/dx)")
ax2.set_xlabel("変位 (mm)")
ax2.set_ylabel("剛性 (kN/mm)")
ax2.grid(True)
ax2.legend()

plt.tight_layout()
# 明示的にplt.showを呼び出して表示
plt.show()
print("サブプロットを表示しました")
print()

# ----------------------------------------------------
# 5. 特定区間の選択と変換（応力-ひずみ変換）
# ----------------------------------------------------
print("5. select_stepを使った特定の区間のデータ変換と可視化")

# 計算に必要な定数を定義
area_mm2 = 50.0  # 断面積 (mm²)
length_mm = 50.0  # 標点間距離 (mm)

# 特定のステップ範囲だけを選択し、チェーンメソッドで応力-ひずみに変換する例
# データの中間部分（有効データが含まれる）に注目
step_middle = list(range(5, min(16, len(collection.step.values) + 1)))

# チェーンメソッドの連鎖で、選択→変換→プロットまでを一気に行う
fig, ax = plt.subplots(figsize=(10, 6))

# チェーンメソッドによるデータ変換の流れを示す
# 複数の変換操作を一連のチェーンとして実行
# axを渡すことでplt.showは呼び出されない
(
    collection.ops.select_step(steps=step_middle)  # まず特定ステップのデータを選択
    .multiply("Force1", 1000)  # kN -> N に変換
    .divide("Force1*1000", area_mm2, result_column="Stress_MPa")  # N/mm² = MPa に変換
    .multiply("Displacement1", 100)  # mm -> 0.1mm に変換（分かりやすくするため）
    .divide(
        "Displacement1*100", length_mm, result_column="Strain_percent"
    )  # % = (ΔL/L₀)*100 に変換
    .plot(  # 変換データをそのままプロット
        x_column="Strain_percent",
        y_column="Stress_MPa",
        plot_type="line",
        color="green",
        label="選択したステップ区間",
        marker="o",
        linestyle="-",
        linewidth=2,
        ax=ax,
    )
    .end()
)

# グラフの装飾
ax.set_title("選択したステップ区間の応力-ひずみ線図")
ax.set_xlabel("ひずみ (%)")
ax.set_ylabel("応力 (MPa)")
plt.grid(True)
# 明示的にplt.showを呼び出して表示
plt.show()
print("応力-ひずみ線図を表示しました")

# ----------------------------------------------------
# 6. 複合可視化（カスタム図の作成）
# ----------------------------------------------------
print("\n6. 複合可視化（カスタム図の作成）")

# 複雑な図を作成する例として、荷重変位曲線とその微分（剛性）を同時表示
# 2つの独立したサブプロットを使用する方法に変更
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# 主軸（上側）: 荷重-変位曲線
# axを渡すことでplt.showは呼び出されない
(
    collection.ops.plot(
        x_column="Displacement1",
        y_column="Force1",
        plot_type="line",
        color="blue",
        label="荷重-変位曲線",
        marker="o",
        linestyle="-",
        ax=ax1,
    ).end()
)

# 装飾（上のプロット）
ax1.set_ylabel("荷重 (kN)", color="blue")
ax1.tick_params(axis="y", labelcolor="blue")
ax1.grid(True)
ax1.set_title("荷重-変位曲線と剛性の比較")
ax1.legend(loc="upper left")

# 下側プロット: 傾き（剛性）を表示
try:
    # チェーンメソッドでdiff操作を実行（実装されている場合）
    stiffness_data = collection.ops.diff(
        "Force1", "Displacement1", result_column="Stiffness"
    ).end()

    # 剛性をプロット
    ax2.plot(
        stiffness_data["Displacement1"].values[1:],
        stiffness_data["Stiffness"].values,
        "r-o",
        label="剛性",
    )

except (AttributeError, ValueError):
    # 手動で剛性を計算
    force_values = collection["Force1"].values
    disp_values = collection["Displacement1"].values

    stiffness = []
    disp_for_stiffness = []

    for i in range(1, len(force_values) - 1):
        if (
            None
            not in [
                force_values[i - 1],
                force_values[i + 1],
                disp_values[i - 1],
                disp_values[i + 1],
            ]
            and disp_values[i + 1] - disp_values[i - 1] != 0
        ):

            slope = (force_values[i + 1] - force_values[i - 1]) / (
                disp_values[i + 1] - disp_values[i - 1]
            )
            stiffness.append(slope)
            disp_for_stiffness.append(disp_values[i])

    # 剛性をプロット
    ax2.plot(disp_for_stiffness, stiffness, "r-o", label="剛性")

# 装飾（下のプロット）
ax2.set_xlabel("変位 (mm)")
ax2.set_ylabel("剛性 (kN/mm)", color="red")
ax2.tick_params(axis="y", labelcolor="red")
ax2.grid(True)
ax2.legend(loc="upper right")

plt.tight_layout()
# 明示的にplt.showを呼び出して表示
plt.show()
print("複合グラフを表示しました")
