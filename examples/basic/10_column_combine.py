"""列合成操作のサンプルコード

このサンプルではColumnの合成操作について説明します。
特にステップやインデックスを基準にした2つのColumnの連結・切り替えの使用例を示します。
"""

import matplotlib.pyplot as plt
import numpy as np
from tascpy.core.collection import ColumnCollection


def main():
    """列合成操作のサンプルを実行"""
    # サンプルデータの作成
    steps = np.linspace(0, 10, 101)  # 0から10まで101ポイント
    column_a = np.sin(steps)  # 正弦波
    column_b = np.cos(steps * 0.5)  # 周期の異なる余弦波
    condition = np.sin(steps * 2)  # 条件判定用の高周波正弦波

    # ColumnCollectionの作成
    collection = ColumnCollection(
        step=steps,
        columns={"sin_wave": column_a, "cos_wave": column_b, "condition": condition},
    )

    # 1. ステップによるカラム切り替え
    result1 = collection.ops.switch_by_step(
        column1="sin_wave",
        column2="cos_wave",
        step_threshold=5.0,  # ステップ5.0で切り替え
        compare_mode="value",
        result_column="switch_at_5",
    ).end()

    # 2. ステップ範囲によるブレンド
    result2 = (
        collection.ops.blend_by_step(
            column1="sin_wave",
            column2="cos_wave",
            step_start=4.0,  # ステップ4.0から
            step_end=6.0,  # ステップ6.0まで徐々にブレンド
            compare_mode="value",
            blend_method="linear",  # 線形ブレンド
            result_column="linear_blend",
        )
        .blend_by_step(
            column1="sin_wave",
            column2="cos_wave",
            step_start=4.0,
            step_end=6.0,
            compare_mode="value",
            blend_method="smooth",  # スムーズなS字カーブブレンド
            result_column="smooth_blend",
        )
        .end()
    )

    # 3. 条件による選択
    result3 = collection.ops.conditional_select(
        column1="sin_wave",
        column2="cos_wave",
        condition_column="condition",
        threshold=0.0,
        compare=">",  # 条件波形が0より大きい場合
        result_column="conditional",
    ).end()

    # 4. カスタム関数による合成
    result4 = collection.ops.custom_combine(
        column1="sin_wave",
        column2="cos_wave",
        combine_func=lambda x, y: np.sqrt(x**2 + y**2),  # ベクトル長さ
        func_name="vector_magnitude",
        result_column="magnitude",
    ).end()

    # 結果の可視化
    plt.figure(figsize=(12, 10))

    # 元の波形
    plt.subplot(4, 1, 1)
    plt.plot(steps, collection["sin_wave"].values, label="sin_wave")
    plt.plot(steps, collection["cos_wave"].values, label="cos_wave")
    plt.plot(
        steps,
        collection["condition"].values,
        label="condition",
        linestyle="--",
        alpha=0.5,
    )
    plt.axvline(x=5.0, color="gray", linestyle="--", alpha=0.7)
    plt.legend()
    plt.title("元の波形")
    plt.grid(True)

    # ステップ切り替え
    plt.subplot(4, 1, 2)
    plt.plot(steps, collection["sin_wave"].values, label="sin_wave", alpha=0.3)
    plt.plot(steps, collection["cos_wave"].values, label="cos_wave", alpha=0.3)
    plt.plot(steps, result1["switch_at_5"].values, label="switch_at_5", color="red")
    plt.axvline(x=5.0, color="gray", linestyle="--", alpha=0.7)
    plt.legend()
    plt.title("ステップによるカラム切り替え")
    plt.grid(True)

    # ブレンド比較
    plt.subplot(4, 1, 3)
    plt.plot(steps, result2["linear_blend"].values, label="linear_blend")
    plt.plot(steps, result2["smooth_blend"].values, label="smooth_blend")
    plt.axvline(x=4.0, color="gray", linestyle="--", alpha=0.7)
    plt.axvline(x=6.0, color="gray", linestyle="--", alpha=0.7)
    plt.legend()
    plt.title("異なるブレンド方法の比較")
    plt.grid(True)

    # 条件選択とカスタム関数
    plt.subplot(4, 1, 4)
    plt.plot(steps, result3["conditional"].values, label="conditional", alpha=0.7)
    plt.plot(steps, result4["magnitude"].values, label="magnitude")
    plt.legend()
    plt.title("条件選択とカスタム関数")
    plt.grid(True)

    plt.tight_layout()
    plt.savefig("combine_example.png")
    plt.show()


if __name__ == "__main__":
    main()
