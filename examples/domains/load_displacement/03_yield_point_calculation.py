"""
降伏点計算の詳細情報表示機能のサンプルコード

このサンプルでは、荷重-変位データから降伏点を計算する際に、
降伏点が見つからない場合の詳細な計算プロセス情報を取得・表示する方法を示します。
通常の成功するケースと、失敗するケースの両方を実演します。
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
from tascpy.core.column import NumberColumn, Column
from tascpy.domains.load_displacement import LoadDisplacementCollection

# ===== 降伏点計算の詳細情報表示機能のデモ =====
print("===== 降伏点計算の詳細情報表示機能のデモ =====")

# 【データの読み込み】
print("\n【データの読み込み】")

# CSVファイルからデータを読み込みます
data_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data"
)
sample_csv_path = os.path.join(data_dir, "load_displacement_sample.csv")

# CSVファイルからColumnCollectionを作成します
collection = ColumnCollection.from_file(
    filepath=sample_csv_path, format_name="csv", auto_detect_types=True
)

# 荷重-変位ドメインに変換します
ld_collection = collection.ops.as_domain(
    "load_displacement", load_column="Force1", displacement_column="Displacement1"
).end()

print(f"データ読み込み完了: {len(ld_collection)} 行 × {len(ld_collection.columns)} 列")
print(
    f"荷重列: {ld_collection.load_column}, 変位列: {ld_collection.displacement_column}"
)

# 出力ディレクトリを作成します
output_dir = os.path.join(os.path.dirname(__file__), "imgs")
os.makedirs(output_dir, exist_ok=True)

# ============================================================================
# ケース1: 通常のデータによる降伏点計算（成功例）
# ============================================================================
print("\n【ケース1: 通常データによる降伏点計算】")

# オフセット法による降伏点計算を行います
print("\nオフセット法による計算:")
offset_result = ld_collection.ops.find_yield_point(
    method="offset",
    offset_value=0.002,  # 0.2%オフセット
    debug_mode=True,
).end()

# 計算が成功したことを確認します
print("✅ 降伏点が正常に計算されました")

# メタデータから降伏点情報を取得します
# ドット記法でメタデータにアクセスします
yield_info = offset_result["analysis.yield_point"]
debug_info = offset_result["analysis.yield_point_calculation.debug_info"]

# 基本情報を表示します
print("\n【基本情報】")
print(f"使用メソッド: {yield_info['method']}")
print(
    f"降伏変位: {yield_info['displacement']:.5f} {ld_collection[ld_collection.displacement_column].unit}"
)
print(
    f"降伏荷重: {yield_info['load']:.3f} {ld_collection[ld_collection.load_column].unit}"
)
print(f"初期勾配: {yield_info['initial_slope']:.3f}")

# 計算過程の情報を表示します
print("\n【計算過程の情報】")
print(f"データ点数: {debug_info['data_stats']['data_points']}")
print(
    f"荷重範囲: {debug_info['data_stats']['min_load']:.3f} - {debug_info['data_stats']['max_load']:.3f}"
)
print(
    f"変位範囲: {debug_info['data_stats']['min_disp']:.5f} - {debug_info['data_stats']['max_disp']:.5f}"
)
print(
    f"計算範囲: {debug_info['data_range']['range_start']*100}% - {debug_info['data_range']['range_end']*100}%"
)
print(f"計算範囲の点数: {debug_info['data_range']['num_points_in_range']}")
print(f"初期勾配の品質 (R²): {debug_info['r_squared']:.3f}")

# オフセット法の詳細情報を表示します
print("\n【オフセット法の詳細】")
offset_info = debug_info["offset_method"]
print(f"オフセット値: {offset_info['offset_value']}")
print(f"オフセット量: {offset_info['offset_amount']:.5f}")
print(
    f"差分統計: 最小={offset_info['diff_stats']['min']:.3f}, "
    + f"最大={offset_info['diff_stats']['max']:.3f}, "
    + f"平均={offset_info['diff_stats']['mean']:.3f}"
)
print(f"符号変化: {'あり' if offset_info['diff_stats']['has_sign_change'] else 'なし'}")

# 交点情報を表示します
if "yield_point" in debug_info and debug_info["yield_point"]["found"]:
    yield_point = debug_info["yield_point"]
    print("\n【交点の詳細】")
    print(f"交点インデックス: {yield_point['intersection_indices']}")
    print(f"補間比率: {yield_point['intersection_ratio']:.3f}")

# オフセット法の結果を可視化します
fig1, ax1 = plt.subplots(figsize=(10, 6))

# 元のデータをプロットします
ax1.plot(
    ld_collection[ld_collection.displacement_column].values,
    ld_collection[ld_collection.load_column].values,
    "b.-",
    label="荷重-変位曲線",
)

# 初期勾配線をプロットします
initial_slope = yield_info["initial_slope"]
disp_data = ld_collection[ld_collection.displacement_column].values
x_vals = np.linspace(0, max(disp_data), 100)
ax1.plot(x_vals, initial_slope * x_vals, "k--", label=f"初期勾配 ({initial_slope:.1f})")

# 降伏点をプロットします
yield_disp = yield_info["displacement"]
yield_load = yield_info["load"]
ax1.plot(yield_disp, yield_load, "ro", markersize=8, label="降伏点")

# オフセット線をプロットします
offset_value = yield_info["parameters"]["offset_value"]
offset_line = initial_slope * x_vals - initial_slope * offset_value * max(disp_data)
ax1.plot(x_vals, offset_line, "r--", label=f"オフセット線 ({offset_value*100:.1f}%)")

# グラフを装飾します
ax1.set_title("通常データでのオフセット降伏点計算 (0.2%)")
ax1.set_xlabel(f"変位 ({ld_collection[ld_collection.displacement_column].unit})")
ax1.set_ylabel(f"荷重 ({ld_collection[ld_collection.load_column].unit})")
ax1.grid(True, linestyle="--", alpha=0.7)
ax1.legend(loc="lower right")

plt.tight_layout()

# グラフを保存します
output_path1 = os.path.join(output_dir, "yield_normal_offset.png")
plt.savefig(output_path1)
print(f"グラフを保存しました: {output_path1}")
plt.close()

# 一般降伏法による計算を行います
print("\n一般降伏法による計算:")
general_result = ld_collection.ops.find_yield_point(
    method="general",
    factor=0.33,  # 33%勾配低下
    debug_mode=True,
).end()

# 計算が成功したことを確認します
print("✅ 降伏点が正常に計算されました")

# メタデータから降伏点情報を取得します
yield_info_general = general_result["analysis.yield_point"]
debug_info_general = general_result["analysis.yield_point_calculation.debug_info"]

# 基本情報を表示します
print("\n【基本情報】")
print(f"使用メソッド: {yield_info_general['method']}")
print(
    f"降伏変位: {yield_info_general['displacement']:.5f} {ld_collection[ld_collection.displacement_column].unit}"
)
print(
    f"降伏荷重: {yield_info_general['load']:.3f} {ld_collection[ld_collection.load_column].unit}"
)
print(f"初期勾配: {yield_info_general['initial_slope']:.3f}")

# 一般降伏法の詳細情報を表示します
print("\n【一般降伏法の詳細】")
general_info = debug_info_general["general_method"]
print(f"係数: {general_info['factor']}")
print(f"閾値: {general_info['threshold']:.3f}")
print(
    f"勾配統計: 最小={general_info['slopes_stats']['min']:.3f}, "
    + f"最大={general_info['slopes_stats']['max']:.3f}, "
    + f"平均={general_info['slopes_stats']['mean']:.3f}"
)

# 降伏点情報を表示します
if "yield_point" in debug_info_general and debug_info_general["yield_point"]["found"]:
    yield_point = debug_info_general["yield_point"]
    print("\n【降伏点の詳細】")
    print(f"降伏点インデックス: {yield_point['index']}")
    print(f"降伏点での勾配: {yield_point['slope_at_point']:.3f}")

# 一般降伏法の結果を可視化します
fig2, ax2 = plt.subplots(figsize=(10, 6))

# 元のデータをプロットします
ax2.plot(
    ld_collection[ld_collection.displacement_column].values,
    ld_collection[ld_collection.load_column].values,
    "b.-",
    label="荷重-変位曲線",
)

# 初期勾配線をプロットします
initial_slope = yield_info_general["initial_slope"]
x_vals = np.linspace(0, max(disp_data), 100)
ax2.plot(x_vals, initial_slope * x_vals, "k--", label=f"初期勾配 ({initial_slope:.1f})")

# 降伏点をプロットします
yield_disp = yield_info_general["displacement"]
yield_load = yield_info_general["load"]
ax2.plot(yield_disp, yield_load, "go", markersize=8, label="降伏点")

# 係数線をプロットします
factor = yield_info_general["parameters"]["factor"]
ax2.plot(
    x_vals,
    initial_slope * factor * x_vals,
    "g--",
    label=f"勾配閾値 ({factor*100:.1f}%)",
)

# グラフを装飾します
ax2.set_title("通常データでの一般降伏点計算 (33%)")
ax2.set_xlabel(f"変位 ({ld_collection[ld_collection.displacement_column].unit})")
ax2.set_ylabel(f"荷重 ({ld_collection[ld_collection.load_column].unit})")
ax2.grid(True, linestyle="--", alpha=0.7)
ax2.legend(loc="lower right")

plt.tight_layout()

# グラフを保存します
output_path2 = os.path.join(output_dir, "yield_normal_general.png")
plt.savefig(output_path2)
print(f"グラフを保存しました: {output_path2}")
plt.close()

# ============================================================================
# ケース2: 完全弾性データによる降伏点計算（失敗例）
# ============================================================================
print("\n\n【ケース2: 完全弾性データによる降伏点計算】")

# 線形（完全弾性）データを作成します（降伏点が見つからないケース）
linear_data = ld_collection.clone()

# 荷重と変位のデータを取得します
disp_column = linear_data.displacement_column
load_column = linear_data.load_column
disp_data = linear_data[disp_column].values.copy()

# 完全な線形関係にするために荷重データを修正します
stiffness = 5.0  # 一定の勾配
load_data = [d * stiffness for d in disp_data]

# 修正した荷重データをコレクションに反映します
linear_data.columns[load_column] = Column(
    ch=linear_data.columns[load_column].ch,
    name=load_column,
    unit=linear_data.columns[load_column].unit,
    values=load_data,
    metadata=linear_data.columns[load_column].metadata,
)

# データの説明をメタデータに追加します
if linear_data.metadata is None:
    linear_data.metadata = {}
linear_data.metadata["description"] = "Modified data (linear)"

print(f"生成したデータのタイプ: {linear_data.metadata['description']}")

# オフセット法による計算を試みます（失敗するケース）
print("\nオフセット法による計算（失敗するケース）:")

# fail_silently=True でエラーを抑制して処理を継続します
linear_offset_result = linear_data.ops.find_yield_point(
    method="offset",
    offset_value=0.002,
    debug_mode=True,
    fail_silently=True,
).end()

# 計算が失敗した場合の詳細情報を表示します
calc_info = linear_offset_result["analysis.yield_point_calculation"]
debug_info = calc_info["debug_info"]

print("\n【計算失敗の詳細情報】")
print(f"失敗理由: {calc_info['reason']}")
print(f"使用メソッド: {debug_info['method']}")

print("\n【計算過程の情報】")
print(f"データ点数: {debug_info['data_stats']['data_points']}")
print(
    f"荷重範囲: {debug_info['data_stats']['min_load']:.3f} - {debug_info['data_stats']['max_load']:.3f}"
)
print(
    f"変位範囲: {debug_info['data_stats']['min_disp']:.5f} - {debug_info['data_stats']['max_disp']:.5f}"
)

if "initial_slope" in debug_info:
    print(f"初期勾配: {debug_info['initial_slope']:.3f}")
    print(f"初期勾配の品質 (R²): {debug_info['r_squared']:.3f}")

    # オフセット法の詳細情報を表示します
    print("\n【オフセット法の詳細】")
    offset_info = debug_info["offset_method"]
    print(f"オフセット値: {offset_info['offset_value']}")
    print(f"オフセット量: {offset_info['offset_amount']:.5f}")
    print(
        f"差分統計: 最小={offset_info['diff_stats']['min']:.3f}, "
        + f"最大={offset_info['diff_stats']['max']:.3f}, "
        + f"平均={offset_info['diff_stats']['mean']:.3f}"
    )
    print(
        f"符号変化: {'あり' if offset_info['diff_stats']['has_sign_change'] else 'なし'}"
    )

    # 交点がない場合の理由分析を表示します
    if not offset_info["diff_stats"]["has_sign_change"]:
        if offset_info["diff_stats"]["min"] > 0:
            print("※ すべての点がオフセット線より上にあるため交点がありません")
        elif offset_info["diff_stats"]["max"] < 0:
            print("※ すべての点がオフセット線より下にあるため交点がありません")

# 線形データの結果を可視化します
fig3, ax3 = plt.subplots(figsize=(10, 6))

# 元のデータをプロットします
ax3.plot(
    linear_data[disp_column].values,
    linear_data[load_column].values,
    "b.-",
    label="荷重-変位曲線",
)

# 初期勾配線をプロットします
initial_slope = debug_info["initial_slope"]
disp_data = linear_data[disp_column].values
x_vals = np.linspace(0, max(disp_data), 100)
ax3.plot(x_vals, initial_slope * x_vals, "k--", label=f"初期勾配 ({initial_slope:.1f})")

# オフセット線をプロットします
offset_value = debug_info["parameters"]["offset_value"]
offset_line = initial_slope * x_vals - initial_slope * offset_value * max(disp_data)
ax3.plot(x_vals, offset_line, "r--", label=f"オフセット線 ({offset_value*100:.1f}%)")

# サンプルポイントを表示します
if "evaluation_points" in debug_info["offset_method"]:
    points = debug_info["offset_method"]["evaluation_points"]
    sample_disps = [p["displacement"] for p in points]
    sample_loads = [p["load"] for p in points]
    ax3.scatter(
        sample_disps, sample_loads, color="cyan", s=30, alpha=0.6, label="評価ポイント"
    )

# グラフを装飾します
ax3.set_title("線形データでのオフセット降伏点計算 (失敗例)")
ax3.set_xlabel(f"変位 ({linear_data[disp_column].unit})")
ax3.set_ylabel(f"荷重 ({linear_data[load_column].unit})")
ax3.grid(True, linestyle="--", alpha=0.7)
ax3.legend(loc="lower right")

plt.tight_layout()

# グラフを保存します
output_path3 = os.path.join(output_dir, "yield_linear_offset_failed.png")
plt.savefig(output_path3)
print(f"グラフを保存しました: {output_path3}")
plt.close()

# ============================================================================
# ケース3: 交点なしデータによる降伏点計算（失敗例）
# ============================================================================
print("\n\n【ケース3: 交点なしデータによる降伏点計算】")

# 交点がないデータを作成します
no_intersection_data = ld_collection.clone()

# 荷重と変位のデータを取得します
disp_column = no_intersection_data.displacement_column
load_column = no_intersection_data.load_column
disp_data = no_intersection_data[disp_column].values.copy()

# 交点がない関係にするため、荷重データを修正します
stiffness = 5.0
offset = 2.0  # 大きなオフセット
load_data = [(d * stiffness - offset) for d in disp_data]

# 修正した荷重データをコレクションに反映します
no_intersection_data.columns[load_column] = Column(
    ch=no_intersection_data.columns[load_column].ch,
    name=load_column,
    unit=no_intersection_data.columns[load_column].unit,
    values=load_data,
    metadata=no_intersection_data.columns[load_column].metadata,
)

# データの説明をメタデータに追加します
if no_intersection_data.metadata is None:
    no_intersection_data.metadata = {}
no_intersection_data.metadata["description"] = "Modified data (no_intersection)"

print(f"生成したデータのタイプ: {no_intersection_data.metadata['description']}")

# オフセット法による計算を試みます（交点なしのケース）
print("\nオフセット法による計算（交点なしのケース）:")

# fail_silently=True でエラーを抑制して処理を継続します
no_int_result = no_intersection_data.ops.find_yield_point(
    method="offset",
    offset_value=0.002,
    debug_mode=True,
    fail_silently=True,
).end()

# 計算が失敗した場合の詳細情報を表示します
calc_info = no_int_result["analysis.yield_point_calculation"]
debug_info = calc_info["debug_info"]

print("\n【計算失敗の詳細情報】")
print(f"失敗理由: {calc_info['reason']}")
print(f"使用メソッド: {debug_info['method']}")

# 交点なしデータの結果を可視化します
fig4, ax4 = plt.subplots(figsize=(10, 6))

# 元のデータをプロットします
ax4.plot(
    no_intersection_data[disp_column].values,
    no_intersection_data[load_column].values,
    "b.-",
    label="荷重-変位曲線",
)

# 初期勾配線をプロットします
if "initial_slope" in debug_info:
    initial_slope = debug_info["initial_slope"]
    disp_data = no_intersection_data[disp_column].values
    x_vals = np.linspace(0, max(disp_data), 100)
    ax4.plot(
        x_vals, initial_slope * x_vals, "k--", label=f"初期勾配 ({initial_slope:.1f})"
    )

    # オフセット線をプロットします
    offset_value = debug_info["parameters"]["offset_value"]
    offset_line = initial_slope * x_vals - initial_slope * offset_value * max(disp_data)
    ax4.plot(
        x_vals, offset_line, "r--", label=f"オフセット線 ({offset_value*100:.1f}%)"
    )

# グラフを装飾します
ax4.set_title("交点なしデータでのオフセット降伏点計算 (失敗例)")
ax4.set_xlabel(f"変位 ({no_intersection_data[disp_column].unit})")
ax4.set_ylabel(f"荷重 ({no_intersection_data[load_column].unit})")
ax4.grid(True, linestyle="--", alpha=0.7)
ax4.legend(loc="lower right")

plt.tight_layout()

# グラフを保存します
output_path4 = os.path.join(output_dir, "yield_no_intersection_failed.png")
plt.savefig(output_path4)
print(f"グラフを保存しました: {output_path4}")
plt.close()

# ============================================================================
# ケース4: 弾性に近いデータでの閾値調整による計算
# ============================================================================
print("\n\n【ケース4: 弾性に近いデータでの閾値調整による計算】")

# わずかに非線形性のあるデータを作成します
elastic_data = ld_collection.clone()

# 荷重と変位のデータを取得します
disp_column = elastic_data.displacement_column
load_column = elastic_data.load_column
disp_data = elastic_data[disp_column].values.copy()

# わずかに非線形性を持たせた荷重データを作成します
stiffness = 5.0
load_data = []
for i in range(len(disp_data)):
    # わずかに非線形性を持たせます
    load_data.append(
        disp_data[i] * stiffness * (1 - 0.01 * disp_data[i] / max(disp_data))
    )

# 修正した荷重データをコレクションに反映します
elastic_data.columns[load_column] = Column(
    ch=elastic_data.columns[load_column].ch,
    name=load_column,
    unit=elastic_data.columns[load_column].unit,
    values=load_data,
    metadata=elastic_data.columns[load_column].metadata,
)

# データの説明をメタデータに追加します
if elastic_data.metadata is None:
    elastic_data.metadata = {}
elastic_data.metadata["description"] = "Modified data (elastic)"

print(f"生成したデータのタイプ: {elastic_data.metadata['description']}")

# 小さなオフセット値での計算（失敗する可能性が高い）
print("\n小さなオフセット値 (0.1%) での計算:")

# 小さなオフセット値で計算を試みます
small_offset_result = elastic_data.ops.find_yield_point(
    method="offset",
    offset_value=0.001,  # 0.1%オフセット（小さい）
    debug_mode=True,
    fail_silently=True,
).end()

# 計算結果を取得します
if "yield_point" in small_offset_result["analysis"]:
    print("✅ 降伏点が正常に計算されました")
    yield_info = small_offset_result["analysis.yield_point"]
    success = True
else:
    print("❌ 降伏点計算に失敗しました")
    calc_info = small_offset_result["analysis.yield_point_calculation"]
    print(f"失敗理由: {calc_info['reason']}")
    success = False

# 小さなオフセット値の結果を可視化します
fig5, ax5 = plt.subplots(figsize=(10, 6))

# 元のデータをプロットします
ax5.plot(
    elastic_data[disp_column].values,
    elastic_data[load_column].values,
    "b.-",
    label="荷重-変位曲線",
)

# デバッグ情報を取得します
if success:
    debug_info = small_offset_result["analysis.yield_point_calculation.debug_info"]
else:
    debug_info = small_offset_result["analysis.yield_point_calculation.debug_info"]

# 初期勾配線をプロットします
if "initial_slope" in debug_info:
    initial_slope = debug_info["initial_slope"]
    disp_data = elastic_data[disp_column].values
    x_vals = np.linspace(0, max(disp_data), 100)
    ax5.plot(
        x_vals, initial_slope * x_vals, "k--", label=f"初期勾配 ({initial_slope:.1f})"
    )

    # オフセット線をプロットします
    offset_value = 0.001  # 0.1%
    offset_line = initial_slope * x_vals - initial_slope * offset_value * max(disp_data)
    ax5.plot(
        x_vals, offset_line, "r--", label=f"オフセット線 ({offset_value*100:.1f}%)"
    )

# 降伏点をプロットします（成功した場合）
if success:
    yield_disp = yield_info["displacement"]
    yield_load = yield_info["load"]
    ax5.plot(yield_disp, yield_load, "ro", markersize=8, label="降伏点")

# グラフを装飾します
ax5.set_title("弾性に近いデータでの小さなオフセット値計算")
ax5.set_xlabel(f"変位 ({elastic_data[disp_column].unit})")
ax5.set_ylabel(f"荷重 ({elastic_data[load_column].unit})")
ax5.grid(True, linestyle="--", alpha=0.7)
ax5.legend(loc="lower right")

plt.tight_layout()

# グラフを保存します
output_path5 = os.path.join(output_dir, "yield_elastic_small_offset.png")
plt.savefig(output_path5)
print(f"グラフを保存しました: {output_path5}")
plt.close()

# 大きなオフセット値での計算（成功する可能性が高い）
print("\n大きなオフセット値 (1.0%) での計算:")

# 大きなオフセット値で計算を試みます
large_offset_result = elastic_data.ops.find_yield_point(
    method="offset",
    offset_value=0.01,  # 1.0%オフセット（大きい）
    debug_mode=True,
    fail_silently=True,
).end()

# 計算結果を取得します
if "yield_point" in large_offset_result["analysis"]:
    print("✅ 降伏点が正常に計算されました")
    yield_info = large_offset_result["analysis.yield_point"]
    success = True

    # 基本情報を表示します
    print("\n【基本情報】")
    print(f"使用メソッド: {yield_info['method']}")
    print(
        f"降伏変位: {yield_info['displacement']:.5f} {elastic_data[elastic_data.displacement_column].unit}"
    )
    print(
        f"降伏荷重: {yield_info['load']:.3f} {elastic_data[elastic_data.load_column].unit}"
    )
    print(f"初期勾配: {yield_info['initial_slope']:.3f}")
else:
    print("❌ 降伏点計算に失敗しました")
    calc_info = large_offset_result["analysis.yield_point_calculation"]
    print(f"失敗理由: {calc_info['reason']}")
    success = False

# 大きなオフセット値の結果を可視化します
fig6, ax6 = plt.subplots(figsize=(10, 6))

# 元のデータをプロットします
ax6.plot(
    elastic_data[disp_column].values,
    elastic_data[load_column].values,
    "b.-",
    label="荷重-変位曲線",
)

# デバッグ情報を取得します
if success:
    debug_info = large_offset_result["analysis.yield_point_calculation.debug_info"]
else:
    debug_info = large_offset_result["analysis.yield_point_calculation.debug_info"]

# 初期勾配線をプロットします
if "initial_slope" in debug_info:
    initial_slope = debug_info["initial_slope"]
    disp_data = elastic_data[disp_column].values
    x_vals = np.linspace(0, max(disp_data), 100)
    ax6.plot(
        x_vals, initial_slope * x_vals, "k--", label=f"初期勾配 ({initial_slope:.1f})"
    )

    # オフセット線をプロットします
    offset_value = 0.01  # 1.0%
    offset_line = initial_slope * x_vals - initial_slope * offset_value * max(disp_data)
    ax6.plot(
        x_vals, offset_line, "r--", label=f"オフセット線 ({offset_value*100:.1f}%)"
    )

# 降伏点をプロットします（成功した場合）
if success:
    yield_disp = yield_info["displacement"]
    yield_load = yield_info["load"]
    ax6.plot(yield_disp, yield_load, "ro", markersize=8, label="降伏点")

# グラフを装飾します
ax6.set_title("弾性に近いデータでの大きなオフセット値計算")
ax6.set_xlabel(f"変位 ({elastic_data[disp_column].unit})")
ax6.set_ylabel(f"荷重 ({elastic_data[load_column].unit})")
ax6.grid(True, linestyle="--", alpha=0.7)
ax6.legend(loc="lower right")

plt.tight_layout()

# グラフを保存します
output_path6 = os.path.join(output_dir, "yield_elastic_large_offset.png")
plt.savefig(output_path6)
print(f"グラフを保存しました: {output_path6}")
plt.close()

print("\n===== デモ完了 =====")
