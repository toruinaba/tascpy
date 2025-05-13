"""列合成操作のサンプルコード

このサンプルではColumnの合成操作について説明します。
tascpyのチェーンメソッドを活用して、ステップやインデックスを基準にした
2つのColumnの連結・切り替えの使用例を示します。
"""

import os
import matplotlib.pyplot as plt
import numpy as np
from tascpy.core.collection import ColumnCollection

print("-- ColumnCollection列合成操作 --\n")

# ----------------------------------------------------
# データ準備：合成操作のサンプルデータを作成
# ----------------------------------------------------
print("サンプルデータの作成...")

# サンプルデータの生成
steps = np.linspace(0, 10, 101)  # 0から10まで101ポイント
column_a = np.sin(steps)  # 正弦波
column_b = np.cos(steps * 0.5)  # 周期の異なる余弦波
condition = np.sin(steps * 2)  # 条件判定用の高周波正弦波

# ColumnCollectionの作成
collection = ColumnCollection(
    step=steps,
    columns={"sin_wave": column_a, "cos_wave": column_b, "condition": condition},
)

print(
    f"コレクションを作成しました。行数: {len(collection)}, 列数: {len(collection.columns)}"
)
print("列名:", list(collection.columns.keys()))

# ----------------------------------------------------
# 1. ステップによるカラム切り替え
# ----------------------------------------------------
print("\n1. ステップによるカラム切り替え")

# ステップ値5.0を境に2つのカラムを切り替え
step_switch_result = collection.ops.switch_by_step(
    column1="sin_wave",
    column2="cos_wave",
    threshold=5.0,  # step_thresholdではなくthresholdが正しいパラメータ名
    compare_mode="value",
    result_column="switch_at_5",
).end()

print("ステップ5.0を基準に sin_wave と cos_wave を切り替えました")
print(f"結果の列名: {list(step_switch_result.columns.keys())}")

# ----------------------------------------------------
# 2. ステップ範囲によるブレンド処理
# ----------------------------------------------------
print("\n2. ステップ範囲によるブレンド処理")

# 複数のブレンド方法を連続したチェーンメソッドで適用
blend_result = (
    collection.ops
    # 線形ブレンド（ステップ4.0〜6.0の間で徐々に切り替え）
    .blend_by_step(
        column1="sin_wave",
        column2="cos_wave",
        start=4.0,  # step_startではなくstartが正しいパラメータ名
        end=6.0,  # step_endではなくendが正しいパラメータ名
        compare_mode="value",
        blend_method="linear",  # 線形ブレンド
        result_column="linear_blend",
    )
    # S字カーブブレンド（同じステップ範囲でよりスムーズな切り替え）
    .blend_by_step(
        column1="sin_wave",
        column2="cos_wave",
        start=4.0,
        end=6.0,
        compare_mode="value",
        blend_method="smooth",  # スムーズなS字カーブブレンド
        result_column="smooth_blend",
    ).end()
)

print("ステップ4.0〜6.0間で2種類のブレンドメソッドを適用しました")
print(f"線形ブレンド結果: {blend_result['linear_blend'].name}")
print(f"スムーズブレンド結果: {blend_result['smooth_blend'].name}")

# ----------------------------------------------------
# 3. 条件による選択処理
# ----------------------------------------------------
print("\n3. 条件カラムによる選択処理")

# 条件カラムの値に基づいて、2つのカラムを動的に切り替え
conditional_result = collection.ops.conditional_select(
    column1="sin_wave",
    column2="cos_wave",
    condition_column="condition",
    threshold=0.0,
    compare=">",  # 条件波形が0より大きい場合
    result_column="conditional",
).end()

print("condition > 0 の条件に基づき sin_wave と cos_wave を切り替えました")
print(f"条件式：condition > 0 の時は sin_wave、それ以外は cos_wave を選択")
print(f"条件カラムの値サンプル: {conditional_result['condition'].values[:5]}...")

# ----------------------------------------------------
# 4. カスタム関数による合成処理
# ----------------------------------------------------
print("\n4. カスタム関数による合成処理")

# カスタム関数を用いて複数のカラムを組み合わせる
custom_result = collection.ops.custom_combine(
    column1="sin_wave",
    column2="cos_wave",
    combine_func=lambda x, y: np.sqrt(x**2 + y**2),  # ベクトル長さ計算
    func_name="vector_magnitude",
    result_column="magnitude",
).end()

print("カスタム関数（ベクトル長の計算）で sin_wave と cos_wave を合成しました")
print(f"ベクトル長の計算式: sqrt(sin_wave^2 + cos_wave^2)")
print(f"結果サンプル: {custom_result['magnitude'].values[:5]}...")

# ----------------------------------------------------
# 5. 複合操作のチェーンメソッド例
# ----------------------------------------------------
print("\n5. 複合操作のチェーンメソッド例")

# 複数の合成操作を一連のチェーンとして実行
complex_chain_result = (
    collection.ops
    # まず条件による選択
    .conditional_select(
        column1="sin_wave",
        column2="cos_wave",
        condition_column="condition",
        threshold=0.5,  # 条件を0.5に変更
        compare=">",
        result_column="temp1",
    )
    # 続いてカスタム関数による加重平均
    .custom_combine(
        column1="temp1",
        column2="cos_wave",
        combine_func=lambda x, y: 0.7 * x + 0.3 * y,  # 加重平均
        func_name="weighted_avg",
        result_column="weighted",
    )
    # 結果を別の計算に利用
    .evaluate("weighted * 2", result_column="final_result").end()  # 単純な計算式
)

print("複数の合成操作を連続してチェーンメソッドで実行しました")
print(f"最終結果の列名: final_result")
print(f"最終結果のサンプル: {complex_chain_result['final_result'].values[:5]}...")

# ----------------------------------------------------
# 結果の可視化
# ----------------------------------------------------

# 出力画像用のディレクトリパスを設定
IMGS_DIR = os.path.join(os.path.dirname(__file__), "imgs")
os.makedirs(IMGS_DIR, exist_ok=True)

# 可視化
plt.figure(figsize=(12, 12))

# 元の波形
plt.subplot(5, 1, 1)
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
plt.subplot(5, 1, 2)
plt.plot(steps, collection["sin_wave"].values, label="sin_wave", alpha=0.3)
plt.plot(steps, collection["cos_wave"].values, label="cos_wave", alpha=0.3)
plt.plot(
    steps, step_switch_result["switch_at_5"].values, label="switch_at_5", color="red"
)
plt.axvline(x=5.0, color="gray", linestyle="--", alpha=0.7)
plt.legend()
plt.title("ステップによるカラム切り替え")
plt.grid(True)

# ブレンド比較
plt.subplot(5, 1, 3)
plt.plot(steps, blend_result["linear_blend"].values, label="linear_blend")
plt.plot(steps, blend_result["smooth_blend"].values, label="smooth_blend")
plt.axvline(x=4.0, color="gray", linestyle="--", alpha=0.7)
plt.axvline(x=6.0, color="gray", linestyle="--", alpha=0.7)
plt.legend()
plt.title("異なるブレンド方法の比較")
plt.grid(True)

# 条件選択とカスタム関数
plt.subplot(5, 1, 4)
plt.plot(
    steps, conditional_result["conditional"].values, label="conditional", alpha=0.7
)
plt.plot(steps, custom_result["magnitude"].values, label="magnitude")
plt.legend()
plt.title("条件選択とカスタム関数")
plt.grid(True)

# 複合操作の結果
plt.subplot(5, 1, 5)
plt.plot(steps, complex_chain_result["temp1"].values, label="条件選択結果", alpha=0.4)
plt.plot(steps, complex_chain_result["weighted"].values, label="加重平均", alpha=0.6)
plt.plot(
    steps, complex_chain_result["final_result"].values, label="最終結果", linewidth=2
)
plt.legend()
plt.title("複合操作チェーン結果")
plt.grid(True)

plt.tight_layout()
plt.savefig(os.path.join(IMGS_DIR, "combine_example.png"))
plt.show()

print(f"\n画像ファイルを保存しました。")
print(f"保存先: {os.path.join(IMGS_DIR, 'combine_example.png')}")
