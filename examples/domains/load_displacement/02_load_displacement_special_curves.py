#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
スケルトン曲線と累積曲線のプロット例

荷重-変位データから特殊曲線を生成し、それらをプロットする方法を示します。
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ライブラリのパスを追加します
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# tascpyをインポートします
import tascpy
from tascpy.core.collection import ColumnCollection
from tascpy.domains.load_displacement import LoadDisplacementCollection

# サンプルデータのパスを設定します
DATA_PATH = (
    Path(__file__).parent.parent.parent / "data" / "load_displacement_sample.csv"
)

# 結果の保存先ディレクトリを作成します
os.makedirs(Path(__file__).parent / "imgs", exist_ok=True)

# ■ 荷重-変位データの特殊曲線プロットサンプル
print("■ 荷重-変位データの特殊曲線プロットサンプル")

# 1. サンプルデータの読み込みを行います
print("1. サンプルデータの読み込み")
collection = ColumnCollection.from_file(
    str(DATA_PATH),
    format_name="csv",
    delimiter=",",
    title_row=0,
    ch_row=1,
    name_row=2,
    unit_row=3,
    data_start_row=4,
    step_col=0,
    date_col=1,
    time_col=2,
    data_start_col=3,
).auto_detect_column_types()  # メソッドチェーンでカラム型の自動判定を行います

# 2. 荷重-変位ドメインに変換します
print("2. 荷重-変位ドメインへの変換")
ld_collection = collection.ops.as_domain(
    "load_displacement", load_column="Force1", displacement_column="Displacement1"
).end()

# 3. 基本的な荷重-変位曲線をプロットします
print("3. 基本的な荷重-変位曲線のプロット")
fig1, ax1 = plt.subplots(figsize=(8, 6))

# メソッドチェーンでプロットします
ld_collection.ops.plot_load_displacement(
    ax=ax1, color="black", linewidth=1.5, label="荷重-変位データ"
)

# グラフを装飾します
ax1.set_title("基本的な荷重-変位曲線")
ax1.grid(True, linestyle="--", alpha=0.7)
ax1.legend()

# グラフを保存します
fig1.savefig(Path(__file__).parent / "imgs" / "load_displacement_basic.png")
print("   - 基本的な荷重-変位曲線を保存しました")

# 4. スケルトン曲線の作成を行います
print("4. スケルトン曲線の作成")
# メソッドチェーンでスケルトン曲線を作成します
skeleton_data = ld_collection.ops.create_skeleton_curve().end()

# 5. スケルトン曲線のプロットを行います
print("5. スケルトン曲線のプロット")
fig2, ax2 = plt.subplots(figsize=(8, 6))

# メソッドチェーンでスケルトン曲線をプロットします
skeleton_data.ops.plot_skeleton_curve(
    ax=ax2,
    plot_original=True,
    original_kwargs={"color": "gray", "alpha": 0.5, "label": "元データ"},
    skeleton_kwargs={"color": "red", "linewidth": 2, "label": "スケルトン曲線"},
)

# グラフを装飾します
ax2.set_title("スケルトン曲線")
ax2.grid(True, linestyle="--", alpha=0.7)
ax2.legend()

# グラフを保存します
fig2.savefig(Path(__file__).parent / "imgs" / "skeleton_curve.png")
print("   - スケルトン曲線を保存しました")

# 6. 累積曲線の作成を行います
print("6. 累積曲線の作成")
# メソッドチェーンで累積曲線を作成します
cumulative_data = ld_collection.ops.create_cumulative_curve().end()

# 7. 累積曲線のプロットを行います
print("7. 累積曲線のプロット")
fig3, ax3 = plt.subplots(figsize=(8, 6))

# メソッドチェーンで累積曲線をプロットします
cumulative_data.ops.plot_cumulative_curve(
    ax=ax3,
    plot_original=True,
    original_kwargs={"color": "gray", "alpha": 0.5, "label": "元データ"},
    cumulative_kwargs={"color": "blue", "linewidth": 2, "label": "累積曲線"},
)

# グラフを装飾します
ax3.set_title("累積曲線")
ax3.grid(True, linestyle="--", alpha=0.7)
ax3.legend()

# グラフを保存します
fig3.savefig(Path(__file__).parent / "imgs" / "cumulative_curve.png")
print("   - 累積曲線を保存しました")

# 8. 複数曲線を同時にプロットします
print("8. 複数曲線を同時にプロット")

# スケルトン曲線と累積曲線の両方を含むデータを作成します
# メソッドチェーンを活用して処理を連続して行います
combined_data = (
    ld_collection.ops.create_skeleton_curve().create_cumulative_curve().end()
)

# 複数曲線を1つのグラフにプロットします
fig4, ax4 = plt.subplots(figsize=(8, 6))

# 元データをプロットします
combined_data.ops.plot_load_displacement(
    ax=ax4, color="gray", alpha=0.4, label="元データ"
)

# __getitem__メソッドを使用して曲線データにアクセスします
skeleton_curve = combined_data["curves.skeleton_curve"]
ax4.plot(
    skeleton_curve["x"],
    skeleton_curve["y"],
    color="red",
    linewidth=2,
    label="スケルトン曲線",
)

# __getitem__メソッドを使用して累積曲線データにアクセスします
cumulative_curve = combined_data["curves.cumulative_curve"]
ax4.plot(
    cumulative_curve["x"],
    cumulative_curve["y"],
    color="blue",
    linewidth=2,
    label="累積曲線",
)

# グラフを装飾します
ax4.set_title("複数曲線の比較")
ax4.grid(True, linestyle="--", alpha=0.7)
ax4.legend()

# グラフを保存します
fig4.savefig(Path(__file__).parent / "imgs" / "multiple_special_curves.png")
print("   - 複数曲線の比較プロットを保存しました")

# 9. カスタマイズしたサブプロット表示を作成します
print("9. カスタマイズしたサブプロット表示")
fig5, axs = plt.subplots(2, 2, figsize=(12, 10))

# 元の荷重-変位曲線をプロットします
ld_collection.ops.plot_load_displacement(ax=axs[0, 0], color="black")
axs[0, 0].set_title("元の荷重-変位曲線")
axs[0, 0].grid(True, linestyle="--", alpha=0.7)

# スケルトン曲線（元データなし）をプロットします
skeleton_data.ops.plot_skeleton_curve(
    ax=axs[0, 1],
    plot_original=False,
    skeleton_kwargs={"color": "red", "linewidth": 2},
)
axs[0, 1].set_title("スケルトン曲線のみ")
axs[0, 1].grid(True, linestyle="--", alpha=0.7)

# 累積曲線（元データなし）をプロットします
cumulative_data.ops.plot_cumulative_curve(
    ax=axs[1, 0],
    plot_original=False,
    cumulative_kwargs={"color": "blue", "linewidth": 2},
)
axs[1, 0].set_title("累積曲線のみ")
axs[1, 0].grid(True, linestyle="--", alpha=0.7)

# 複数曲線（スケルトンと累積を比較）をプロットします
# __getitem__メソッドを使用してスケルトン曲線データにアクセス
skeleton_curve = combined_data["curves.skeleton_curve"]
axs[1, 1].plot(
    skeleton_curve["x"],
    skeleton_curve["y"],
    color="red",
    linewidth=2,
    label="スケルトン曲線",
)

# __getitem__メソッドを使用して累積曲線データにアクセス
cumulative_curve = combined_data["curves.cumulative_curve"]
axs[1, 1].plot(
    cumulative_curve["x"],
    cumulative_curve["y"],
    color="blue",
    linewidth=2,
    label="累積曲線",
)

# グラフを装飾します
axs[1, 1].set_title("特殊曲線の比較")
axs[1, 1].grid(True, linestyle="--", alpha=0.7)
axs[1, 1].legend()

# 全体タイトルを設定します
fig5.suptitle("荷重-変位データの特殊曲線解析", fontsize=16)
fig5.tight_layout(rect=[0, 0, 1, 0.96])  # suptitleのスペースを確保

# グラフを保存します
fig5.savefig(Path(__file__).parent / "imgs" / "special_curves_comparison.png")
print("   - カスタマイズしたサブプロット表示を保存しました")

# サマリー情報を表示します
print("\n全てのプロットが保存されました。")
print("このサンプルコードでは以下の操作を行いました：")
print("1. 荷重-変位データの読み込み")
print("2. スケルトン曲線の作成と可視化")
print("3. 累積曲線の作成と可視化")
print("4. 複数曲線を同時に表示する方法")
print("5. カスタマイズしたサブプロット表示")
