"""
ColumnCollectionの数学演算操作を示すサンプルコード
"""

import os
import math
from tascpy.core.collection import ColumnCollection

# 現在のスクリプトからの相対パスでデータファイルを取得
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_CSV_PATH = os.path.join(DATA_DIR, "sample.csv")

print("-- ColumnCollectionの数学演算操作 --\n")

# サンプルデータの読み込み
try:
    # CSVファイルからデータを読み込む
    collection = ColumnCollection.from_file(
        filepath=SAMPLE_CSV_PATH, format_name="csv", auto_detect_types=True
    )
except FileNotFoundError:
    print(f"ファイル '{SAMPLE_CSV_PATH}' が見つかりません。模擬データを作成します。")
    # CSVファイルがない場合の模擬データ作成
    steps = list(range(1, 6))
    columns = {
        "Force1": [None, None, 0.0, 2.9, 2.9],
        "Force2": [None, None, 0.0, 8.8, 8.8],
        "Displacement1": [None, None, 0.00, 0.08, 0.08],
        "Displacement2": [None, None, 0.00, 0.56, 0.61],
    }
    metadata = {
        "date": ["2020/11/30", "2020/11/30", "2020/12/01", "2020/12/01", "2020/12/01"],
        "time": ["17:21:36", "17:29:40", "13:22:11", "13:38:05", "13:38:10"],
        "title": "無題",
    }
    collection = ColumnCollection(steps, columns, metadata, auto_detect_types=True)

# 初期データを表示
print("初期データ:")
print(f"Force1: {collection['Force1'].values}")
print(f"Force2: {collection['Force2'].values}")
print(f"Displacement1: {collection['Displacement1'].values}")
print(f"Displacement2: {collection['Displacement2'].values}")
print()

# 操作プロキシを取得
ops = collection.ops

print("1. 基本的な算術演算")
# 足し算: 定数加算
result = ops.add("Force1", 1.0).end()  # Force1 + 1.0
print(f"Force1 + 1.0 = {result['Force1+1.0'].values}")

# 引き算: 列同士
result = ops.subtract("Force2", "Force1").end()  # Force2 - Force1
print(f"Force2 - Force1 = {result['Force2-Force1'].values}")

# 掛け算: 定数乗算
result = ops.multiply("Displacement1", 10).end()  # Displacement1 * 10
print(f"Displacement1 * 10 = {result['Displacement1*10'].values}")

# 割り算: 列同士（ゼロ除算はNoneとして扱う）
result = ops.divide(
    "Force1", "Displacement1", handle_zero_division="none"
).end()  # Force1 / Displacement1
print(f"Force1 / Displacement1 = {result['Force1/Displacement1'].values}")
print()

print("2. 複合演算と新しい列名の指定")
# 複数の列の合計（合力）を計算し、新しい列名を指定
result = ops.add("Force1", "Force2", result_column="TotalForce").end()
print(f"TotalForce (Force1 + Force2) = {result['TotalForce'].values}")

# 変位の差分を計算（結果の列名は自動生成されない場合の例）
result = ops.subtract(
    "Displacement2", "Displacement1", result_column="DisplacementDiff"
).end()
print(f"DisplacementDiff = {result['DisplacementDiff'].values}")
print()

print("3. selectを使用して特定の列のみに演算を適用")
# selectを使用して特定の列だけを選択してから数学演算を適用する例
result = (
    ops.select(columns=["Force1", "Displacement1"])
    .divide(
        "Force1",
        "Displacement1",
        result_column="Stiffness",
        handle_zero_division="none",
    )
    .end()
)
print(f"選択した列のみで剛性計算: Force1/Displacement1 = {result['Stiffness'].values}")
print()

print("4. ステップによる選択と演算")
# selectでステップを指定して特定のステップだけに対して演算を適用する例
result = (
    ops.select(steps=[3, 4, 5])  # ステップ3,4,5のデータのみを選択
    .multiply("Force1", 2, result_column="DoubleForce")  # 荷重を2倍
    .end()
)
print(f"選択したステップの荷重を2倍: Force1*2 = {result['DoubleForce'].values}")
print()

print("5. 数式の評価")
# 数式文字列を評価して結果を計算（複合的な計算式）
# 例: 剛性 k = F/(δ+0.001) の計算、0.001は0除算回避
result = ops.evaluate(
    "(Force1+Force2)/(Displacement1+0.001)", result_column="Stiffness"
).end()
print(f"剛性 k = (F1+F2)/(D1+0.001) = {result['Stiffness'].values}")
print()

print("6. 数学関数の適用")
# 特定の列を選択して数学関数を適用するチェーンメソッド
result_sqrt = (
    ops.select(columns=["Displacement2"])
    .sqrt("Displacement2", result_column="sqrt_disp")
    .end()
)
print(f"sqrt(Displacement2) = {result_sqrt['sqrt_disp'].values}")

# べき乗の計算
result_pow = (
    ops.select(columns=["Force1"]).pow("Force1", 2, result_column="Force1^2").end()
)
print(f"Force1^2 = {result_pow['Force1^2'].values}")

# 指数関数の適用
result_exp = (
    ops.select(columns=["Displacement1"])
    .exp("Displacement1", result_column="exp_disp")
    .end()
)
print(f"exp(Displacement1) = {result_exp['exp_disp'].values}")
print()

print("7. 連鎖演算によるデータ変換と解析")
# 特定のステップだけを選択して連鎖的に複数の演算を適用
result = (
    ops.select(steps=[3, 4, 5])  # Noneを含まないステップを選択
    .add("Force1", "Force2", result_column="TotalForce")  # 合計荷重を計算
    .divide(
        "TotalForce", 2, result_column="AverageForce", handle_zero_division="none"
    )  # 平均荷重を計算
    .sqrt("AverageForce", result_column="SqrtAvgForce")  # 平均荷重の平方根
    .divide(
        "Force1",
        "SqrtAvgForce",
        result_column="NormalizedForce1",
        handle_zero_division="none",
    )  # 荷重の正規化
    .end()
)

print("連鎖演算を適用した結果:")
print(f"  選択したステップ: {result.step.values}")
print(f"  合計荷重: {result['TotalForce'].values}")
print(f"  平均荷重: {result['AverageForce'].values}")
print(f"  平均荷重の平方根: {result['SqrtAvgForce'].values}")
print(f"  正規化荷重1: {result['NormalizedForce1'].values}")
print()

print("8. 複合的なデータ解析パイプライン")
# より実践的なチェーンメソッド活用例：データのフィルタリング、変換、新しい指標の計算を一連の流れで行う
advanced_result = (
    ops.select(columns=["Force1", "Force2", "Displacement1", "Displacement2"])
    .search_by_value("Force1", ">", 0)  # 荷重が正の値のデータのみを選択
    .add("Force1", "Force2", result_column="TotalForce")  # 合計荷重
    .divide(
        "TotalForce",
        "Displacement1",
        result_column="TotalStiffness",
        handle_zero_division="none",
    )  # 全体剛性
    .evaluate(
        "(Force2/Force1) if Force1 > 0 else None", result_column="ForceRatio"
    )  # 荷重比
    .round_values(
        "TotalStiffness", decimals=2, result_column="StiffnessRounded"
    )  # 剛性値の丸め
    .end()
)

print("複合的なデータ解析パイプラインの結果:")
print(f"  処理後の行数: {len(advanced_result)}行")
print(f"  列名: {list(advanced_result.columns.keys())}")
if len(advanced_result) > 0:
    print(f"  合計荷重: {advanced_result['TotalForce'].values}")
    print(f"  全体剛性(丸め): {advanced_result['StiffnessRounded'].values}")
    print(f"  荷重比: {advanced_result['ForceRatio'].values}")
