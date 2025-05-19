"""
ColumnCollectionの列操作を示すサンプルコード
（列の追加、削除、変更とチェーンメソッドによる操作）
"""

import os
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import NumberColumn, StringColumn

# 現在のスクリプトからの相対パスでデータファイルを取得
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_CSV_PATH = os.path.join(DATA_DIR, "sample.csv")

print("-- ColumnCollectionの列操作 --\n")

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

print("初期状態:")
print(f"列名: {list(collection.columns.keys())}")
print(f"Force1データ: {collection['Force1'].values}")
print()

print("1. 新しい列の追加")
# リストから新しい列を追加 - 計測日からの経過時間（分）
elapsed_minutes = [0, 8, 1180, 1256, 1257]  # 最初の測定からの経過分数
collection.add_column("ElapsedMinutes", elapsed_minutes)

# カラムオブジェクトから新しい列を追加 - 試験識別名
test_id_column = StringColumn(
    ch="ID", name="TestID", unit="", values=["A001", "A001", "B001", "B001", "B001"]
)
collection.add_column("TestID", test_id_column)

print(f"列の追加後の列名: {list(collection.columns.keys())}")
print(f"経過時間データ: {collection['ElapsedMinutes'].values}")
print(f"試験ID: {collection['TestID'].values}")
print()

print("2. 列の削除")
# 不要な列を削除
collection.remove_column("ElapsedMinutes")
print(f"ElapsedMinutes列削除後の列名: {list(collection.columns.keys())}")
print()

print("3. 列の値の変更")
# Force1列の値を更新
original_force1 = collection["Force1"].values.copy()
collection["Force1"].values[2] = 0.1  # 3行目の値を変更
print(f"変更前のForce1: {original_force1}")
print(f"変更後のForce1: {collection['Force1'].values}")
print()

print("4. 複数の列を一度に処理")
# すべての数値列に対して処理を実行
for name, column in collection.columns.items():
    if hasattr(column, "values") and all(
        isinstance(v, (int, float)) for v in column.values if v is not None
    ):
        # 各値を四捨五入
        original_values = column.values.copy()
        column.values = [round(v, 1) if v is not None else None for v in column.values]
        print(f"{name} 列を四捨五入: {original_values} -> {column.values}")
print()

print("5. 派生列の作成")
# 直接オブジェクト操作による派生列の作成
# 荷重から応力への変換（假の例：断面積を10cm²と仮定）
area = 10.0  # cm²
force1_kn = collection["Force1"].values
stress_mpa = [
    (f * 1000 / area) if f is not None else None for f in force1_kn
]  # kN -> N -> MPa

# 変換した値を新しい列として追加
stress_column = NumberColumn(ch="σ", name="Stress", unit="MPa", values=stress_mpa)
collection.add_column("Stress", stress_column)

print(f"Force1 (kN): {collection['Force1'].values}")
print(f"応力 (MPa): {collection['Stress'].values}")
print()

print("6. 列のクローン作成と操作")
# 変位1列をクローンして新しい列を作成
disp1_column = collection["Displacement1"]
disp1_copy = disp1_column.clone()
disp1_copy.name = "Displacement1_mm"
disp1_copy.unit = "mm"

# 値を変更（例：単位変換 mm -> cm）
disp1_copy.values = [d / 10 if d is not None else None for d in disp1_copy.values]
collection.add_column("Displacement1_cm", disp1_copy)

print(f"元の変位1 (mm): {collection['Displacement1'].values}")
print(f"変換した変位1 (cm): {collection['Displacement1_cm'].values}")
print()

print("7. チェーンメソッドを使った列操作")
# チェーンメソッドによる高度な列操作
result = (
    collection.ops.select(
        columns=["Force1", "Force2", "Displacement1"]
    )  # 特定の列を選択
    .search_by_value("Displacement1", ">", 0)  # Displacement1が0より大きい行だけを選択
    .multiply("Force1", 2, result_column="Force1_x2")  # 荷重1を2倍
    .multiply(
        "Force2", 0.5, result_column="Force2_x0_5"
    )  # 荷重2を半分（小数点は使わない）
    .evaluate("Force1_x2 / Displacement1", result_column="Stiffness1")  # 剛性1を計算
    .evaluate("Force2_x0_5 / Displacement1", result_column="Stiffness2")  # 剛性2を計算
    .end()
)

print("チェーンメソッドによる列操作結果:")
print(f"生成された列: {list(result.columns.keys())}")
print(f"Force1_x2: {result['Force1_x2'].values}")
print(f"Force2_x0_5: {result['Force2_x0_5'].values}")  # 修正: Force2_x0.5 → Force2_x0_5
print(f"Stiffness1: {result['Stiffness1'].values}")
print(f"Stiffness2: {result['Stiffness2'].values}")
print()

print("8. 高度な列変換と処理")
# より複雑なチェーンメソッド操作
advanced_result = (
    result.ops.filter_out_none()  # None値を持つ行を除外
    .select(columns=["Force1", "Force1_x2", "Stiffness1"])  # 必要な列のみ選択
    .abs_values("Force1", result_column="Force1_abs")  # 絶対値を計算
    .round_values(
        "Stiffness1", decimals=1, result_column="Stiffness1_rounded"
    )  # 剛性の値を丸める
    .end()
)

print("高度な列処理結果:")
print(f"処理後の列: {list(advanced_result.columns.keys())}")
print(f"行数: {len(advanced_result)}行")
if len(advanced_result) > 0:
    print(f"Force1_abs: {advanced_result['Force1_abs'].values}")
    print(f"Stiffness1_rounded: {advanced_result['Stiffness1_rounded'].values}")
