"""
ColumnCollectionのデータ変換を示すサンプルコード

このサンプルではtascpyのメソッドチェーンを活用して、データの様々な変換操作を実行します。
単位変換、数学的変換、正規化、微分・積分などを連続的に実行する方法を示します。
"""

import os
import math
from tascpy.core.collection import ColumnCollection

# 現在のスクリプトからの相対パスでデータファイルを取得
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
# sample.csvからload_displacement_sample.csvに変更
SAMPLE_CSV_PATH = os.path.join(DATA_DIR, "load_displacement_sample.csv")

print("-- ColumnCollectionのデータ変換 --\n")

# ----------------------------------------------------
# データの準備
# ----------------------------------------------------

# CSVファイルからデータを読み込む
try:
    collection = ColumnCollection.from_file(
        filepath=SAMPLE_CSV_PATH, format_name="csv", auto_detect_types=True
    )
    print("CSVファイルからデータを読み込みました")
except FileNotFoundError:
    # サンプルファイルがない場合は模擬データを作成
    print(f"ファイル '{SAMPLE_CSV_PATH}' が見つかりません。模擬データを作成します。")
    # 模擬データの作成
    steps = list(range(1, 16))  # より多くのデータポイントを作成
    columns = {
        "Force1": [
            None,
            None,
            0.0,
            2.9,
            2.9,
            3.5,
            5.0,
            7.2,
            9.1,
            10.0,
            12.0,
            13.5,
            15.0,
            16.2,
            18.0,
        ],
        "Force2": [
            None,
            None,
            0.0,
            8.8,
            8.8,
            10.2,
            12.5,
            15.8,
            18.3,
            20.0,
            22.0,
            24.0,
            26.0,
            27.5,
            29.0,
        ],
        "Displacement1": [
            None,
            None,
            0.00,
            0.08,
            0.08,
            0.12,
            0.25,
            0.38,
            0.52,
            0.65,
            0.75,
            0.85,
            0.95,
            1.05,
            1.15,
        ],
        "Displacement2": [
            None,
            None,
            0.00,
            0.56,
            0.61,
            0.75,
            1.10,
            1.45,
            1.82,
            2.20,
            2.50,
            2.80,
            3.10,
            3.30,
            3.50,
        ],
    }
    metadata = {
        "date": ["2020/11/30"] * 2
        + ["2020/12/01"] * 3
        + ["2020/12/02"] * 3
        + ["2020/12/03"] * 2
        + ["2020/12/04"] * 5,
        "time": [
            "17:21:36",
            "17:29:40",
            "13:22:11",
            "13:38:05",
            "13:38:10",
            "09:15:00",
            "10:30:00",
            "14:45:00",
            "08:20:00",
            "09:00:00",
            "10:00:00",
            "11:00:00",
            "12:00:00",
            "13:00:00",
            "14:00:00",
        ],
        "title": "無題",
    }
    collection = ColumnCollection(steps, columns, metadata, auto_detect_types=True)

# データの初期状態を表示
print("\n初期データ:")
print(f"行数: {len(collection)}")
print(f"カラム: {list(collection.columns.keys())}")
print(f"Force1の例: {collection['Force1'].values[:5]}...")
print(f"Displacement1の例: {collection['Displacement1'].values[:5]}...")

# ----------------------------------------------------
# 1. 前処理：欠損値のフィルタリング
# ----------------------------------------------------
print("\n1. 前処理：欠損値(None)のフィルタリングとゼロ置換")

# フィルタリング条件を緩和: None値を持つデータも含めて処理する
# 代わりにNoneをゼロに置き換える前処理に重点を置く
preprocessed = collection.clone()
columns_to_convert = ["Force1", "Force2", "Displacement1", "Displacement2"]
for column in columns_to_convert:
    if column in preprocessed.columns:
        preprocessed.columns[column].values = [
            0 if v is None else v for v in preprocessed.columns[column].values
        ]

print(f"処理後の行数: {len(preprocessed)}")
print(f"処理後のForce1: {preprocessed['Force1'].values}")
print(f"処理後のDisplacement1: {preprocessed['Displacement1'].values}")

# ----------------------------------------------------
# 2. 単位変換：チェーンメソッドを活用
# ----------------------------------------------------
print("\n2. 単位変換：チェーンメソッドを活用")

# メソッドチェーンで複数の操作を一度に実行
# selectで関連する列だけを選択し、そのまま単位変換の処理チェーンにつなげる
unit_converted = (
    preprocessed.ops.select(columns=["Force1", "Displacement1"])
    .multiply("Force1", 1000, result_column="Force1_N")  # kN -> N （1000倍）
    .multiply(
        "Displacement1", 0.001, result_column="Displacement1_m"
    )  # mm -> m （0.001倍）
    .end()
)

print("単位変換の結果:")
print(f"力の単位変換: kN -> N")
print(f"  元データ (kN): {unit_converted['Force1'].values[:5]}...")
print(f"  変換後 (N): {unit_converted['Force1_N'].values[:5]}...")
print(f"変位の単位変換: mm -> m")
print(f"  元データ (mm): {unit_converted['Displacement1'].values[:5]}...")
print(f"  変換後 (m): {unit_converted['Displacement1_m'].values[:5]}...")

# ----------------------------------------------------
# 3. 特定ステップの選択と処理
# ----------------------------------------------------
print("\n3. 特定ステップの選択と処理")

# 特定のステップだけを選択し、その後チェーンで変換処理
step_indices = list(range(3, 8))  # 3から7のステップを選択
step_result = (
    preprocessed.ops.select_step(steps=step_indices)
    .multiply("Force1", 1000, result_column="Force1_N")  # kN -> N
    .multiply("Displacement1", 0.001, result_column="Displacement1_m")  # mm -> m
    .end()
)

print(f"選択したステップ値: {step_result.step.values}")
print(f"  変換後Force1_N: {step_result['Force1_N'].values}")
print(f"  変換後Displacement1_m: {step_result['Displacement1_m'].values}")

# ----------------------------------------------------
# 4. 物理量の計算：応力・ひずみ計算
# ----------------------------------------------------
print("\n4. 物理量の計算：応力・ひずみ計算")

# 全データで単位変換したコレクションを用意
full_converted = (
    preprocessed.ops.multiply("Force1", 1000, result_column="Force1_N")
    .multiply("Displacement1", 0.001, result_column="Displacement1_m")
    .end()
)

# 物理量の計算をチェーンメソッドで実行
area_mm2 = 50.0  # 断面積 (mm²)
area_m2 = area_mm2 * 1e-6  # 断面積 (m²)
length_m = 0.05  # 初期長さ (m)

physical_result = (
    full_converted.ops
    # 応力計算 (σ = F/A)
    .divide("Force1_N", area_m2, result_column="Stress_Pa")  # Pa = N/m²
    .divide("Stress_Pa", 1e6, result_column="Stress_MPa")  # MPa = Pa/1e6
    # ひずみ計算 (ε = ΔL/L)
    .divide("Displacement1_m", length_m, result_column="Strain")  # 無次元
    .multiply("Strain", 100, result_column="Strain_percent")  # % = 無次元 * 100
    .end()
)

print(f"応力計算: σ = F/A (断面積 = {area_mm2} mm²)")
print(f"  応力 (MPa): {physical_result['Stress_MPa'].values[:5]}...")
print(f"ひずみ計算: ε = ΔL/L (初期長さ = {length_m*1000} mm)")
print(f"  ひずみ (%): {physical_result['Strain_percent'].values[:5]}...")

# ----------------------------------------------------
# 5. 特定データの対数変換
# ----------------------------------------------------
print("\n5. 特定データの対数変換")

# 特定のステップを選択して対数変換を適用するチェーンメソッド
# 微分計算などの演算のために有効なデータポイントに限定する
important_steps = [6, 7, 8, 9, 10]  # 重要なステップ
log_result = (
    physical_result.ops.select_step(steps=important_steps)
    .search_by_value("Strain", ">", 0.0)  # 対数計算のため正の値のみ選択
    .log("Strain", base=math.e, result_column="LogStrain")
    .log("Stress_Pa", base=10, result_column="LogStress")
    .end()
)

print(f"選択したステップの対数変換:")
print(f"  選択したステップ: {log_result.step.values}")
print(f"  対数ひずみ: {log_result['LogStrain'].values}")
print(f"  対数応力: {log_result['LogStress'].values}")

# ----------------------------------------------------
# 6. データの正規化
# ----------------------------------------------------
print("\n6. データの正規化")

# 正規化計算のために十分なデータを確保（初期のNone値を変換済み）
norm_data = preprocessed.ops.select_step(
    steps=range(3, 15)
).end()  # 有効なデータのみを選択

# 単一のチェーンでデータ正規化の複数の手法を適用
norm_result = (
    norm_data.ops.normalize(
        "Displacement1", method="minmax", result_column="Disp_norm_minmax"
    )
    .normalize("Force1", method="zscore", result_column="Force_norm_zscore")
    .end()
)

print(f"変位の正規化（Min-Max法: [0,1]範囲）")
print(f"  元データ: {norm_result['Displacement1'].values[:5]}...")
print(f"  正規化後: {norm_result['Disp_norm_minmax'].values[:5]}...")
print(f"荷重の正規化（Z-score法: 平均0、標準偏差1）")
print(f"  元データ: {norm_result['Force1'].values[:5]}...")
print(f"  正規化後: {norm_result['Force_norm_zscore'].values[:5]}...")

# ----------------------------------------------------
# 7. 累積計算
# ----------------------------------------------------
print("\n7. 累積計算")

# 累積和計算のデモ（実装されていない場合は手動で計算）
try:
    cum_result = norm_data.ops.cumsum(
        "Displacement1", result_column="Cumulative_Displacement"
    ).end()

    print(f"変位の累積和:")
    print(f"  元データ: {norm_data['Displacement1'].values[:5]}...")
    print(f"  累積和: {cum_result['Cumulative_Displacement'].values[:5]}...")
except AttributeError:
    print("累積和機能は未実装のためスキップします")
    # 手動での累積和計算
    disp_values = norm_data["Displacement1"].values
    cumsum_values = []
    running_sum = 0
    for val in disp_values:
        running_sum += val
        cumsum_values.append(running_sum)

    print(f"手動計算による変位の累積和:")
    print(f"  元データ: {disp_values[:5]}...")
    print(f"  累積和: {cumsum_values[:5]}...")

# ----------------------------------------------------
# 8. 微分と積分（実装されていたら）
# ----------------------------------------------------
print("\n8. 微分と積分（近似計算）")

try:
    # 微分計算のために有効なデータポイントを確保
    # Force1とDisplacement1の値が有意であるデータのみを選択
    calc_data = (
        norm_data.ops.search_by_value("Force1", ">", 0)
        .search_by_value("Displacement1", ">", 0)
        .end()
    )

    # 荷重変位曲線の微分と積分をチェーンメソッドで連続実行
    calculus_result = (
        calc_data.ops.diff("Force1", "Displacement1", result_column="Stiffness_dF_dx")
        .integrate(
            "Force1", "Displacement1", method="trapezoid", result_column="Energy"
        )
        .end()
    )

    print(f"剛性計算（微分: dF/dx）:")
    print(f"  元の荷重: {calc_data['Force1'].values}")
    print(f"  元の変位: {calc_data['Displacement1'].values}")
    print(f"  剛性: {calculus_result['Stiffness_dF_dx'].values}")
    print(f"エネルギー計算（積分: ∫F·dx）:")
    print(f"  エネルギー: {calculus_result['Energy'].values}")
except AttributeError:
    print("微分・積分機能は未実装のためスキップします")
except ValueError as e:
    print(f"微分・積分計算でエラーが発生しました: {str(e)}")
    print(
        "微分計算には少なくとも2点、積分計算にはいくつかの有効なデータポイントが必要です"
    )
    print("データセットが小さすぎるか、値の変動が不十分な可能性があります")

# ----------------------------------------------------
# 9. 複合操作の例：変換・計算・フィルタリング
# ----------------------------------------------------
print("\n9. 複合操作の例：変換・計算・フィルタリング")

try:
    # 複数の操作を単一のチェーンで実行する例
    # 十分なデータポイントが利用可能であることを確認
    complex_result = (
        preprocessed.ops
        # 単位変換
        .multiply("Force1", 1000, result_column="Force1_N")
        .multiply("Displacement1", 0.001, result_column="Displacement1_m")
        # 物理量計算
        .divide("Force1_N", area_m2, result_column="Stress_Pa")
        .divide("Displacement1_m", length_m, result_column="Strain")
        # 特定の値でフィルタリング（エラー防止のため緩い条件に）
        .search_by_value("Stress_Pa", ">=", 0)
        # 追加演算
        .multiply("Stress_Pa", 0.000001, result_column="Stress_MPa")
        .end()
    )

    # 条件を満たすデータがある場合のみ対数変換を実行
    if len(complex_result) > 0 and any(s > 0 for s in complex_result["Strain"].values):
        # 正の値のみを対象にして対数変換
        positive_strain = (
            complex_result.ops.search_by_value("Strain", ">", 0.0)
            .log("Strain", base=math.e, result_column="LogStrain")
            .end()
        )

        print("複合処理の結果:")
        print(f"  処理後の行数: {len(positive_strain)}")
        print(f"  選択されたステップ: {positive_strain.step.values}")
        print(f"  応力値 (MPa): {positive_strain['Stress_MPa'].values[:5]}...")
        print(f"  対数ひずみ: {positive_strain['LogStrain'].values[:5]}...")
    else:
        print(
            "複合処理の結果: 条件を満たすデータがないため対数変換はスキップされました"
        )
        print(f"  処理後の行数: {len(complex_result)}")
        print(f"  選択されたステップ: {complex_result.step.values}")
        print(f"  応力値 (MPa): {complex_result['Stress_MPa'].values[:5]}...")
except Exception as e:
    print(f"複合操作の実行中にエラーが発生しました: {str(e)}")
