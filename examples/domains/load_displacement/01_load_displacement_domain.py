"""
荷重-変位ドメインの活用例を示すサンプルコード

このサンプルでは、CSVファイルから荷重-変位データを読み込み、
ColumnCollectionからLoadDisplacementCollectionへの変換と、
荷重-変位ドメイン特有の解析操作をチェーンメソッドで行う方法を示します。
"""

import os
import numpy as np
import matplotlib.pyplot as plt

# tascpyをインポート
import tascpy
from tascpy.core.collection import ColumnCollection

# ===== CSVファイルからデータを読み込み =====
print("===== CSVファイルからデータを読み込み =====")

# プロジェクトルートからの相対パスでデータファイルを取得
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../../"))
data_dir = os.path.join(project_root, "examples/data")
sample_csv_path = os.path.join(data_dir, "load_displacement_sample.csv")

print(f"CSVファイルパス: {sample_csv_path}")

# CSVファイルからColumnCollectionを作成
collection = ColumnCollection.from_file(
    filepath=sample_csv_path, format_name="csv", auto_detect_types=True
)

print(f"読み込んだデータの形状: {len(collection)} 行 × {len(collection.columns)} 列")
print(f"列名: {list(collection.columns.keys())}")

# 荷重と変位のカラム名を設定
force_column = "Force1"
disp_column = "Displacement1"

# 最初と最後のいくつかのデータを表示
print("\n荷重データ (最初の5行):")
print(collection[force_column].values[:5])

print("\n変位データ (最初の5行):")
print(collection[disp_column].values[:5])

# ===== LoadDisplacementCollectionへの変換 =====
print("\n===== LoadDisplacementCollectionへの変換 =====")

# チェーンメソッドを使用して荷重-変位ドメインに変換
ld_collection = collection.ops.as_domain(
    "load_displacement", load_column=force_column, displacement_column=disp_column
).end()

print(f"変換後のドメイン: {ld_collection.domain}")
print(f"荷重カラム: {ld_collection.load_column}")
print(f"変位カラム: {ld_collection.displacement_column}")

# 利用可能なメソッドを確認
print("\n利用可能なメソッド:")
available_methods = [
    method for method in dir(ld_collection.ops) if not method.startswith("_")
]
print(f"メソッド数: {len(available_methods)}")
print(f"一部のメソッド例: {available_methods[:10]}...")

# ===== 荷重-変位曲線の基本可視化 =====
print("\n===== 荷重-変位曲線の基本可視化 =====")

# まず図とサブプロットを作成
fig, ax = plt.subplots(figsize=(10, 6))

# チェーンメソッドを使用した基本プロット - .end()を呼び出さない
ld_collection.ops.plot_load_displacement(ax=ax)

# プロットの詳細設定
ax.set_title("荷重-変位曲線 (基本)")
ax.grid(True)
ax.legend()

# 図の保存
output_dir = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(output_dir, "imgs"), exist_ok=True)
output_path = os.path.join(output_dir, "imgs/load_displacement_basic.png")
plt.savefig(output_path)
plt.close()

print(f"基本荷重-変位曲線の図を保存しました: {output_path}")

# ===== 傾き（接線剛性）の計算 =====
print("\n===== 傾き（接線剛性）の計算 =====")

# チェーンメソッドで接線剛性を計算
slopes_collection = ld_collection.ops.calculate_slopes(
    result_column="Tangent_Stiffness"
).end()

slope_column = "Tangent_Stiffness"
slope_values = [
    s if s is not None else float("nan") for s in slopes_collection[slope_column].values
]

print(f"接線剛性の列名: {slope_column}")
valid_slopes = [s for s in slope_values if not np.isnan(s)]
if valid_slopes:
    print(f"接線剛性の範囲: {min(valid_slopes):.3f} ～ {max(valid_slopes):.3f}")

# ===== 初期剛性の計算（線形領域からの推定） =====
print("\n===== 初期剛性の計算 =====")

# calculate_stiffnessは直接浮動小数点の剛性値を返す
stiffness = ld_collection.ops.calculate_stiffness(
    range_start=0.1,  # 初期10%（荷重範囲の相対位置）
    range_end=0.4,  # 40%まで（荷重範囲の相対位置）
    method="linear_regression",
)

print(
    f"線形回帰による初期剛性: {stiffness:.3f} {ld_collection[ld_collection.load_column].unit}/{ld_collection[ld_collection.displacement_column].unit}"
)

# 異なる範囲での初期剛性計算
stiffness_alt = ld_collection.ops.calculate_stiffness(
    range_start=0.0,  # 最小荷重から
    range_end=0.2,  # 最大荷重の20%まで
    method="linear_regression",
)

print(
    f"小さい範囲での初期剛性: {stiffness_alt:.3f} {ld_collection[ld_collection.load_column].unit}/{ld_collection[ld_collection.displacement_column].unit}"
)

# ===== 降伏点の解析 =====
print("\n===== 降伏点の解析 =====")

# チェーンメソッドでオフセット法による降伏点の特定
yield_offset_result = ld_collection.ops.find_yield_point(
    method="offset",
    range_start=0.05,  # 荷重の5%から (より初期部分を使用)
    range_end=0.25,  # 荷重の25%まで (非線形になる前の範囲)
    offset_value=1.0,  # 1.0%オフセット（荷重変形関係のスケールに合わせて調整）
    result_prefix="yield_offset",
).end()

# 結果を取得
yield_disp_offset = yield_offset_result["yield_offset_displacement"].values[0]
yield_load_offset = yield_offset_result["yield_offset_load"].values[0]
initial_slope_offset = yield_offset_result.metadata["analysis"]["yield_point"][
    "initial_slope"
]

print(f"オフセット法による降伏点:")
print(
    f"  変位 = {yield_disp_offset:.3f} {ld_collection[ld_collection.displacement_column].unit}"
)
print(
    f"  荷重 = {yield_load_offset:.3f} {ld_collection[ld_collection.load_column].unit}"
)
print(f"  初期勾配 = {initial_slope_offset:.3f}")

# チェーンメソッドで一般降伏法による降伏点を特定します
yield_general_result = ld_collection.ops.find_yield_point(
    method="general",
    range_start=0.05,  # オフセット法と同じ設定です
    range_end=0.25,  # オフセット法と同じ設定です
    factor=0.25,  # 初期勾配の25%を降伏点と定義します
    result_prefix="yield_general",
).end()

# ドット記法を使って結果を取得します（__getitem__メソッド活用）
yield_disp_general = yield_general_result["yield_general_displacement"].values[0]
yield_load_general = yield_general_result["yield_general_load"].values[0]
initial_slope_general = yield_general_result["analysis.yield_point.initial_slope"]

print(f"一般降伏法による降伏点:")
print(
    f"  変位 = {yield_disp_general:.3f} {ld_collection[ld_collection.displacement_column].unit}"
)
print(
    f"  荷重 = {yield_load_general:.3f} {ld_collection[ld_collection.load_column].unit}"
)
print(f"  初期勾配 = {initial_slope_general:.3f}")

# ===== 解析結果の可視化 =====
print("\n===== 解析結果の可視化 =====")

# 複数のサブプロットを使った可視化
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 9))

# 荷重-変位曲線と降伏点のプロット (ax1)
# チェーンメソッドとして扱わず、直接プロット結果を受け取る
ld_collection.ops.plot_load_displacement(ax=ax1)

# 降伏点をプロット
ax1.plot(
    yield_disp_offset,
    yield_load_offset,
    "ro",
    markersize=8,
    label=f"オフセット降伏点 ({yield_load_offset:.2f} {ld_collection[ld_collection.load_column].unit})",
)

ax1.plot(
    yield_disp_general,
    yield_load_general,
    "go",
    markersize=8,
    label=f"一般降伏点 ({yield_load_general:.2f} {ld_collection[ld_collection.load_column].unit})",
)

# 初期剛性ラインの表示
disp_data = ld_collection[ld_collection.displacement_column].values
x_vals = np.linspace(0, max(disp_data) * 0.6, 100)
ax1.plot(
    x_vals,
    initial_slope_offset * x_vals,
    "k--",
    label=f"初期勾配 ({initial_slope_offset:.1f})",
)

# オフセットラインの表示
offset_value = yield_offset_result.metadata["analysis"]["yield_point"]["parameters"][
    "offset_value"
]
ax1.plot(
    x_vals,
    initial_slope_offset * x_vals
    - initial_slope_offset * offset_value * max(disp_data),
    "r--",
    label=f"オフセットライン ({offset_value*100:.1f}%)",
)

# 一般降伏法のラインの表示
factor = yield_general_result.metadata["analysis"]["yield_point"]["parameters"][
    "factor"
]
ax1.plot(
    x_vals,
    initial_slope_general * factor * x_vals,
    "g--",
    label=f"勾配低下ライン ({factor*100:.1f}%)",
)

ax1.set_title("荷重-変位曲線と降伏点解析")
ax1.set_xlabel(f"変位 ({ld_collection[ld_collection.displacement_column].unit})")
ax1.set_ylabel(f"荷重 ({ld_collection[ld_collection.load_column].unit})")
ax1.grid(True)
ax1.legend(loc="lower right")

# 接線剛性の変化プロット (ax2)
valid_indices = [i for i, s in enumerate(slope_values) if not np.isnan(s)]
valid_disps = [disp_data[i] for i in valid_indices]
valid_slopes = [slope_values[i] for i in valid_indices]

ax2.plot(valid_disps, valid_slopes, "g.-", label="接線剛性")

ax2.axhline(
    y=initial_slope_offset,
    color="k",
    linestyle="--",
    label=f"初期勾配 ({initial_slope_offset:.1f})",
)
ax2.axhline(
    y=initial_slope_offset * 0.333,
    color="g",
    linestyle="--",
    label="33.3%初期勾配",
)

ax2.set_title("変位と接線剛性の関係")
ax2.set_xlabel(f"変位 ({ld_collection[ld_collection.displacement_column].unit})")
ax2.set_ylabel(
    f"接線剛性 ({ld_collection[ld_collection.load_column].unit}/{ld_collection[ld_collection.displacement_column].unit})"
)
ax2.grid(True)
ax2.legend(loc="upper right")

plt.tight_layout()

# 図の保存
output_path = os.path.join(output_dir, "imgs/load_displacement_analysis.png")
plt.savefig(output_path)
plt.close()

print(f"解析結果の図を保存しました: {output_path}")

# ===== チェーンメソッドによる複雑な解析と可視化 =====
print("\n===== チェーンメソッドによる複雑な解析と可視化 =====")

# 複数の降伏点定義を比較するためのメソッドパラメータ
methods = [
    {"method": "offset", "offset_value": 1.0, "result_prefix": "yield_offset_small"},
    {
        "method": "offset",
        "offset_value": 2.0,
        "result_prefix": "yield_offset_standard",
    },
    {"method": "offset", "offset_value": 5.0, "result_prefix": "yield_offset_large"},
    {"method": "general", "factor": 0.33, "result_prefix": "yield_general_33"},
    {"method": "general", "factor": 0.50, "result_prefix": "yield_general_50"},
]

# チェーンメソッドで降伏点比較分析を実行
fig, ax = plt.subplots(figsize=(10, 7))
ld_collection.ops.compare_yield_methods(methods=methods, ax=ax)

plt.title("様々な降伏点定義方法の比較")
plt.tight_layout()
output_path = os.path.join(output_dir, "imgs/plot_yield_comparison.png")
plt.savefig(output_path)
plt.close()
print(f"複数の降伏点定義方法の比較プロットを保存: {output_path}")

# ===== 実用的なレポート用プロット - チェーンメソッドでのワークフロー =====
print("\n===== 実用的なレポート用プロット - チェーンメソッドでのワークフロー =====")

# チェーンメソッドを活用した完全なワークフローの例
# 1. データの選択
# 2. 前処理と異常値の除去
# 3. 複数の降伏点解析を一度に実行
# 4. 結果の可視化までをチェーンで連続実行

report_collection = (
    ld_collection.ops
    # 前処理: 異常値の除去と平滑化
    .search_by_value(force_column, ">", 0)  # 正の荷重値のみ抽出
    .moving_average(
        column=disp_column, window_size=3, result_column="Disp_Smooth"
    )  # 変位データの平滑化
    .moving_average(
        column=force_column, window_size=3, result_column="Force_Smooth"
    )  # 荷重データの平滑化
    # 平滑化したカラムを使用して新しいドメインコレクションを作成
    .as_domain(
        "load_displacement",
        load_column="Force_Smooth",
        displacement_column="Disp_Smooth",
    )
    # 複数の降伏点解析を実行
    .find_yield_point(
        method="offset",
        offset_value=1.0,  # 1.0%オフセット（荷重変形関係のスケールに合わせて調整）
        result_prefix="yield_offset_std",
    )
    .find_yield_point(
        method="general", factor=0.33, result_prefix="yield_general_std"  # 33%勾配低下
    )
    .end()
)

# 結果データから降伏点の情報を取得
offset_yield_point = {
    "displacement": report_collection["yield_offset_std_displacement"].values[0],
    "load": report_collection["yield_offset_std_load"].values[0],
}

general_yield_point = {
    "displacement": report_collection["yield_general_std_displacement"].values[0],
    "load": report_collection["yield_general_std_load"].values[0],
}

print("前処理と降伏点解析の結果:")
print(
    f"オフセット法 (0.2%): 変位 = {offset_yield_point['displacement']:.3f}, 荷重 = {offset_yield_point['load']:.3f}"
)
print(
    f"一般降伏法 (33%): 変位 = {general_yield_point['displacement']:.3f}, 荷重 = {general_yield_point['load']:.3f}"
)

# レポート用の図を生成
fig, axs = plt.subplots(2, 2, figsize=(14, 10))
plt.suptitle("荷重-変位解析レポート", fontsize=16)

# 1. 基本的な荷重-変位曲線 (左上)
report_collection.ops.plot_load_displacement(ax=axs[0, 0])
axs[0, 0].set_title("荷重-変位曲線 (平滑化済み)")

# 2. オフセット法の降伏点詳細 (右上)
# パラメータとプロットパラメータを分離して渡す
report_collection.ops.plot_load_displacement(ax=axs[0, 1])
axs[0, 1].scatter(
    offset_yield_point["displacement"],
    offset_yield_point["load"],
    color="red",
    marker="o",
    s=100,
    label="0.2%オフセット降伏点",
)
axs[0, 1].set_title("0.2%オフセット降伏解析")

# 3. 一般降伏法の降伏点詳細 (左下)
# 同様にパラメータを分離
report_collection.ops.plot_load_displacement(ax=axs[1, 0])
axs[1, 0].scatter(
    general_yield_point["displacement"],
    general_yield_point["load"],
    color="green",
    marker="^",
    s=100,
    label="33%勾配低下点",
)
axs[1, 0].set_title("一般降伏法 (33%勾配低下)")

# 4. 両方の降伏点を1つのプロットで比較 (右下)
# オリジナルデータプロット
axs[1, 1].plot(
    report_collection[report_collection.displacement_column].values,
    report_collection[report_collection.load_column].values,
    "b-",
    linewidth=1.5,
    label="荷重-変位データ",
)

# 降伏点プロット
axs[1, 1].scatter(
    [offset_yield_point["displacement"]],
    [offset_yield_point["load"]],
    color="red",
    s=100,
    marker="o",
    label=f'オフセット法 ({offset_yield_point["load"]:.1f})',
)

axs[1, 1].scatter(
    [general_yield_point["displacement"]],
    [general_yield_point["load"]],
    color="green",
    s=100,
    marker="^",
    label=f'一般降伏法 ({general_yield_point["load"]:.1f})',
)

axs[1, 1].set_title("降伏点の比較")
axs[1, 1].set_xlabel(
    f"変位 ({report_collection[report_collection.displacement_column].unit})"
)
axs[1, 1].set_ylabel(f"荷重 ({report_collection[report_collection.load_column].unit})")
axs[1, 1].grid(True)
axs[1, 1].legend(loc="lower right")

# レイアウト調整と保存
plt.tight_layout(rect=[0, 0, 1, 0.95])  # suptitleのスペースを確保
output_path = os.path.join(output_dir, "imgs/load_displacement_report_chain.png")
plt.savefig(output_path)
plt.close()

print(f"チェーンメソッドベースの実用的なレポート用プロットを保存: {output_path}")
print("\n全てのサンプルコードの実行が完了しました。")
