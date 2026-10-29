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
from tascpy.domains import as_load_displacement

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
collection = tascpy.load(str(DATA_PATH), format_name="csv")  # 数値の列は自動的に Float64 になります
print(f"   - 単位: {collection.units}")

# 2. 荷重-変位ドメインに変換し、曲線生成に必要なサイクル列（"Force1_cycle"）を作成します
print("2. 荷重-変位ドメインへの変換")
ld_collection = (
    collection.ops.as_domain(as_load_displacement, load_column="Force1", displacement_column="Displacement1")
    .mark_cycles(result_column="Force1_cycle")
    .end()
)

# 3. 基本的な荷重-変位曲線をプロットします
print("3. 基本的な荷重-変位曲線のプロット")
fig1, ax1 = plt.subplots(figsize=(8, 6))

# メソッドチェーンでプロットします
ld_collection.plot.plot_load_displacement(
    ax=ax1, color="black", linewidth=1.5, label="荷重-変位データ"
)

# グラフを装飾します
ax1.set_title("基本的な荷重-変位曲線")
ax1.grid(True, linestyle="--", alpha=0.7)
ax1.legend()

# グラフを保存します
fig1.savefig(Path(__file__).parent / "imgs" / "load_displacement_basic.png")
print("   - 基本的な荷重-変位曲線を保存しました")

# 4. スケルトン曲線と累積曲線を作成します（曲線はそれぞれ新しい荷重-変位コレクションになります）
print("4. スケルトン曲線・累積曲線の作成")
skeleton_data = ld_collection.ops.to_skeleton_curve().end()
cumulative_data = ld_collection.ops.to_cumulative_curve().end()
print(f"   - スケルトン曲線の列: {skeleton_data.columns}")

# 5. 元データとスケルトン曲線を同じ Axes に重ねてプロットします
print("5. スケルトン曲線のプロット")
fig2, ax2 = plt.subplots(figsize=(8, 6))
ld_collection.plot.plot_load_displacement(ax=ax2, color="gray", alpha=0.5, label="元データ")
skeleton_data.plot.plot_load_displacement(ax=ax2, color="red", linewidth=2, label="スケルトン曲線")
ax2.set_title("スケルトン曲線")
ax2.grid(True, linestyle="--", alpha=0.7)
ax2.legend()
fig2.savefig(Path(__file__).parent / "imgs" / "skeleton_curve.png")
print("   - スケルトン曲線を保存しました")

# 6. 累積曲線をプロットします
print("6. 累積曲線のプロット")
fig3, ax3 = plt.subplots(figsize=(8, 6))
cumulative_data.plot.plot_load_displacement(ax=ax3, color="blue", linewidth=2, label="累積曲線")
ax3.set_title("累積曲線")
ax3.grid(True, linestyle="--", alpha=0.7)
ax3.legend()
fig3.savefig(Path(__file__).parent / "imgs" / "cumulative_curve.png")
print("   - 累積曲線を保存しました")

# 7. スケルトン曲線から降伏点を求めて描画します
print("7. スケルトン曲線の降伏点")
point = skeleton_data.ops.yield_point(fail_silently=True)
print(f"   - 降伏点: 変位 {point.x} {point.x_unit}, 荷重 {point.y} {point.y_unit}")
if point.metadata["is_valid"]:
    fig4, ax4 = plt.subplots(figsize=(8, 6))
    skeleton_data.plot.plot_yield_point(point, ax=ax4)
    fig4.savefig(Path(__file__).parent / "imgs" / "skeleton_yield_point.png")
    print("   - スケルトン曲線の降伏点を保存しました")

# 8. スケルトン曲線の点に対応する元データの行を取り出します
print("8. スケルトン曲線の点に対応する元データ")
source_rows = ld_collection.ops.select(steps=skeleton_data["source_step"].values.tolist()).end()
print(f"   - 取り出した行数: {len(source_rows)}（列: {source_rows.columns}）")

# サマリー情報を表示します
print("\n全てのプロットが保存されました。")
print("このサンプルコードでは以下の操作を行いました：")
print("1. 荷重-変位データの読み込み")
print("2. スケルトン曲線の作成と可視化")
print("3. 累積曲線の作成と可視化")
print("4. スケルトン曲線からの降伏点の検出")
print("5. スケルトン曲線の点に対応する元データの取り出し")
