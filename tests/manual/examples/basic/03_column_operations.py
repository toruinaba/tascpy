"""
ColumnCollectionの列操作を示すサンプルコード
（列の追加、削除、変更とチェーンメソッドによる操作）

ColumnCollection は不変 (immutable) です。列の追加・削除・変更はすべて
新しいコレクションを返すので、結果を変数に代入して使います。
"""

import os
import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
import tascpy

# 現在のスクリプトからの相対パスでデータファイルを取得
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_CSV_PATH = os.path.join(DATA_DIR, "sample.csv")

print("-- ColumnCollectionの列操作 --\n")

# サンプルデータの読み込み
try:
    # CSVファイルからデータを読み込む
    collection = tascpy.load(SAMPLE_CSV_PATH, format_name="csv")
except FileNotFoundError:
    print(f"ファイル '{SAMPLE_CSV_PATH}' が見つかりません。模擬データを作成します。")
    # CSVファイルがない場合の模擬データ作成
    collection = ColumnCollection(
        {
            "Force1": [None, None, 0.0, 2.9, 2.9],
            "Force2": [None, None, 0.0, 8.8, 8.8],
            "Displacement1": [None, None, 0.00, 0.08, 0.08],
            "Displacement2": [None, None, 0.00, 0.56, 0.61],
        },
        step=list(range(1, 6)),
        units={"Force1": "kN", "Force2": "kN", "Displacement1": "mm", "Displacement2": "mm"},
    )

print("初期状態:")
print(f"列名: {collection.columns}")
print(f"単位: {collection.units}")
print(f"Force1データ: {collection['Force1'].values}")
print()

print("1. 新しい列の追加")
# リストから新しい列を追加 - 計測日からの経過時間（分）
elapsed_minutes = [0, 8, 1180, 1256, 1257]  # 最初の測定からの経過分数
collection = collection.with_column("ElapsedMinutes", elapsed_minutes, unit="min")

# カラムオブジェクトから新しい列を追加 - 試験識別名
test_id_column = Column("TestID", ["A001", "A001", "B001", "B001", "B001"], ch="ID")
collection = collection.with_column("TestID", test_id_column)

print(f"列の追加後の列名: {collection.columns}")
print(f"経過時間データ: {collection['ElapsedMinutes'].values} [{collection['ElapsedMinutes'].unit}]")
print(f"試験ID: {collection['TestID'].values}")
print()

print("2. 列の削除")
# 不要な列を削除
collection = collection.drop("ElapsedMinutes")
print(f"ElapsedMinutes列削除後の列名: {collection.columns}")
print()

print("3. 列の値の変更")
# Force1列の3行目の値を更新した新しいコレクションを作る（単位などのメタは引き継がれる）
original_force1 = collection["Force1"].values
updated_force1 = original_force1.copy()
updated_force1[2] = 0.1
collection = collection.with_column("Force1", updated_force1)
print(f"変更前のForce1: {original_force1}")
print(f"変更後のForce1: {collection['Force1'].values} [{collection['Force1'].unit}]")
print()

print("4. 複数の列を一度に処理")
# すべての数値列の値を四捨五入
for name in collection.columns:
    column = collection[name]
    if column.is_numeric:
        collection = collection.with_column(name, np.round(column.values, 1))
        print(f"{name} 列を四捨五入: {column.values} -> {collection[name].values}")
print()

print("5. 派生列の作成")
# 直接値を計算して派生列を作成
# 荷重から応力への変換（仮の例：断面積を10cm²と仮定）
area = 10.0  # cm²
stress_mpa = collection["Force1"].values * 1000 / area  # 欠損 (NaN) はそのまま欠損になる

# 変換した値を新しい列として追加（単位は自動では決まらないので明示する）
collection = collection.with_column("Stress", stress_mpa, unit="MPa", ch="σ")

print(f"Force1 (kN): {collection['Force1'].values}")
print(f"応力 (MPa): {collection['Stress'].values}")
print()

print("6. 既存の列から別単位の列を作成")
# 単位変換 mm -> cm（tascpy は単位を自動変換しないため、変換後の単位を明示する）
collection = collection.with_column(
    "Displacement1_cm", collection["Displacement1"].values / 10, unit="cm"
)

print(f"元の変位1 (mm): {collection['Displacement1'].values}")
print(f"変換した変位1 (cm): {collection['Displacement1_cm'].values}")
print(f"単位: {collection.units}")
print()

print("7. チェーンメソッドを使った列操作")
# チェーンメソッドによる高度な列操作
result = (
    collection.ops.select(
        columns=["Force1", "Force2", "Displacement1"]
    )  # 特定の列を選択
    .filter_by_condition("Displacement1", lambda x: x > 0)  # Displacement1が0より大きい行だけを選択
    .multiply("Force1", 2, result_column="Force1_x2")  # 荷重1を2倍（単位は kN のまま）
    .multiply(
        "Force2", 0.5, result_column="Force2_x0_5"
    )  # 荷重2を半分
    .calculate(lambda Force1_x2, Displacement1: Force1_x2 / Displacement1,
               result_column="Stiffness1", unit="kN/mm")  # 剛性1を計算
    .calculate(lambda Force2_x0_5, Displacement1: Force2_x0_5 / Displacement1,
               result_column="Stiffness2", unit="kN/mm")  # 剛性2を計算
    .end()
)

print("チェーンメソッドによる列操作結果:")
print(f"生成された列: {result.columns}")
print(f"単位: {result.units}")
print(f"Force1_x2: {result['Force1_x2'].values}")
print(f"Force2_x0_5: {result['Force2_x0_5'].values}")
print(f"Stiffness1: {result['Stiffness1'].values}")
print(f"Stiffness2: {result['Stiffness2'].values}")
print()

print("8. 高度な列変換と処理")
# より複雑なチェーンメソッド操作
advanced_result = (
    result.ops.filter_out_none()  # 欠損値を持つ行を除外
    .select(columns=["Force1", "Force1_x2", "Stiffness1"])  # 必要な列のみ選択
    .abs("Force1", result_column="Force1_abs")  # 絶対値を計算
    .round(
        "Stiffness1", decimals=1, result_column="Stiffness1_rounded"
    )  # 剛性の値を丸める
    .end()
)

print("高度な列処理結果:")
print(f"処理後の列: {advanced_result.columns}")
print(f"行数: {len(advanced_result)}行")
if len(advanced_result) > 0:
    print(f"Force1_abs: {advanced_result['Force1_abs'].values}")
    print(f"Stiffness1_rounded: {advanced_result['Stiffness1_rounded'].values}")
