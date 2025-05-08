#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
スケルトン曲線と累積曲線のプロット例

荷重-変位データから特殊曲線を生成し、それらをプロットする方法を示します。
"""

import os
import csv
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ライブラリのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# tascpyのインポート
import tascpy
from tascpy.core.collection import ColumnCollection
from tascpy.operations.load_displacement.curves import (
    create_skeleton_curve,
    create_cumulative_curve,
)
from tascpy.operations.load_displacement.plot import (
    plot_load_displacement,
    plot_skeleton_curve,
    plot_cumulative_curve,
    plot_multiple_curves,
)

# サンプルデータのパス
DATA_PATH = Path(__file__).parent.parent / "data" / "load_displacement_sample.csv"


def plot_special_curves():
    """荷重-変位データの特殊曲線を作成しプロットするサンプル"""
    print("■ 荷重-変位データの特殊曲線プロットサンプル")

    # データの読み込み
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
    )

    # カラム型の自動判定
    collection = collection.auto_detect_column_types()

    # 荷重-変位ドメインに変換
    print("2. 荷重-変位ドメインへの変換")
    ld_collection = collection.ops.as_domain(
        "load_displacement", load_column="Force1", displacement_column="Displacement1"
    ).end()

    # 基本的な荷重-変位曲線をプロット
    print("3. 基本的な荷重-変位曲線のプロット")
    fig1, ax1 = plot_load_displacement(
        ld_collection, color="black", linewidth=1.5, label="荷重-変位データ"
    )

    # グラフを装飾
    ax1.set_title("基本的な荷重-変位曲線")
    ax1.grid(True, linestyle="--", alpha=0.7)
    ax1.legend()

    # グラフを保存
    fig1.savefig(Path(__file__).parent / "load_displacement_basic.png")
    print("   - 基本的な荷重-変位曲線を保存しました")

    # スケルトン曲線の作成
    print("4. スケルトン曲線の作成")
    skeleton_data = create_skeleton_curve(ld_collection)

    # スケルトン曲線のプロット
    print("5. スケルトン曲線のプロット")
    fig2, ax2 = plot_skeleton_curve(
        skeleton_data,
        plot_original=True,
        original_kwargs={"color": "gray", "alpha": 0.5, "label": "元データ"},
        skeleton_kwargs={"color": "red", "linewidth": 2, "label": "スケルトン曲線"},
    )

    # グラフを装飾
    ax2.set_title("スケルトン曲線")
    ax2.grid(True, linestyle="--", alpha=0.7)
    ax2.legend()

    # グラフを保存
    fig2.savefig(Path(__file__).parent / "skeleton_curve.png")
    print("   - スケルトン曲線を保存しました")

    # 累積曲線の作成
    print("6. 累積曲線の作成")
    cumulative_data = create_cumulative_curve(ld_collection)

    # 累積曲線のプロット
    print("7. 累積曲線のプロット")
    fig3, ax3 = plot_cumulative_curve(
        cumulative_data,
        plot_original=True,
        original_kwargs={"color": "gray", "alpha": 0.5, "label": "元データ"},
        cumulative_kwargs={"color": "blue", "linewidth": 2, "label": "累積曲線"},
    )

    # グラフを装飾
    ax3.set_title("累積曲線")
    ax3.grid(True, linestyle="--", alpha=0.7)
    ax3.legend()

    # グラフを保存
    fig3.savefig(Path(__file__).parent / "cumulative_curve.png")
    print("   - 累積曲線を保存しました")

    # 複数曲線を同時にプロット
    print("8. 複数曲線を同時にプロット")

    # スケルトン曲線と累積曲線の両方を含むデータを作成
    combined_data = create_cumulative_curve(skeleton_data)

    # 複数曲線プロットの設定
    curves = [
        {
            "type": "original",
            "kwargs": {"color": "gray", "alpha": 0.4, "label": "元データ"},
        },
        {
            "type": "skeleton",
            "kwargs": {"color": "red", "linewidth": 2, "label": "スケルトン曲線"},
        },
        {
            "type": "cumulative",
            "kwargs": {"color": "blue", "linewidth": 2, "label": "累積曲線"},
        },
    ]

    # 複数曲線のプロット
    fig4, ax4 = plot_multiple_curves(combined_data, curves=curves)

    # グラフを装飾
    ax4.set_title("複数曲線の比較")
    ax4.grid(True, linestyle="--", alpha=0.7)
    ax4.legend()

    # グラフを保存
    fig4.savefig(Path(__file__).parent / "multiple_special_curves.png")
    print("   - 複数曲線の比較プロットを保存しました")

    # 2x2のサブプロットを作成して別々に表示
    print("9. カスタマイズしたサブプロット表示")
    fig5, axs = plt.subplots(2, 2, figsize=(12, 10))

    # 元の荷重-変位曲線
    plot_load_displacement(ld_collection, ax=axs[0, 0], color="black")
    axs[0, 0].set_title("元の荷重-変位曲線")
    axs[0, 0].grid(True, linestyle="--", alpha=0.7)

    # スケルトン曲線（元データなし）
    plot_skeleton_curve(
        skeleton_data,
        ax=axs[0, 1],
        plot_original=False,
        skeleton_kwargs={"color": "red", "linewidth": 2},
    )
    axs[0, 1].set_title("スケルトン曲線のみ")
    axs[0, 1].grid(True, linestyle="--", alpha=0.7)

    # 累積曲線（元データなし）
    plot_cumulative_curve(
        cumulative_data,
        ax=axs[1, 0],
        plot_original=False,
        cumulative_kwargs={"color": "blue", "linewidth": 2},
    )
    axs[1, 0].set_title("累積曲線のみ")
    axs[1, 0].grid(True, linestyle="--", alpha=0.7)

    # 複数曲線（スケルトンと累積を比較）
    limited_curves = [
        {
            "type": "skeleton",
            "kwargs": {"color": "red", "linewidth": 2, "label": "スケルトン曲線"},
        },
        {
            "type": "cumulative",
            "kwargs": {"color": "blue", "linewidth": 2, "label": "累積曲線"},
        },
    ]
    plot_multiple_curves(combined_data, curves=limited_curves, ax=axs[1, 1])
    axs[1, 1].set_title("特殊曲線の比較")
    axs[1, 1].grid(True, linestyle="--", alpha=0.7)
    axs[1, 1].legend()

    # 全体タイトルの設定
    fig5.suptitle("荷重-変位データの特殊曲線解析", fontsize=16)
    fig5.tight_layout(rect=[0, 0, 1, 0.96])  # suptitleのスペースを確保

    # グラフを保存
    fig5.savefig(Path(__file__).parent / "special_curves_comparison.png")
    print("   - カスタマイズしたサブプロット表示を保存しました")

    print("\n全てのプロットが保存されました。")
    print("このサンプルコードでは以下の操作を行いました：")
    print("1. 荷重-変位データの読み込み")
    print("2. スケルトン曲線の作成と可視化")
    print("3. 累積曲線の作成と可視化")
    print("4. 複数曲線を同時に表示する方法")
    print("5. カスタマイズしたサブプロット表示")


if __name__ == "__main__":
    plot_special_curves()
