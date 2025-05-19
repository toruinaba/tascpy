"""
ColumnCollectionデータへのアクセス方法を示すサンプルコード
"""

import os
from tascpy.core.collection import ColumnCollection

# 現在のスクリプトからの相対パスでデータファイルを取得
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_CSV_PATH = os.path.join(DATA_DIR, "sample.csv")

print("-- ColumnCollectionデータへのアクセス方法 --\n")

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

# データの基本情報を表示
print(f"読み込んだデータ: {len(collection)}行, {len(collection.columns)}列")
print(f"列名: {list(collection.columns.keys())}")
print()

print("1. 列全体へのアクセス")
# 列名で列全体にアクセス
force1_column = collection["Force1"]
print(f"Force1列: {force1_column.values}")

# 列の属性へのアクセス
print(f"Force1のチャンネル名: {force1_column.ch}")
print(f"Force1の単位: {force1_column.unit}")

# ステップ列へのアクセス
steps = collection.step.values
print(f"ステップ値: {steps}")
print()

print("2. 単一要素へのアクセス")
# インデックスで行にアクセスし、それから列名で値にアクセス
first_row = collection[0]
print(f"最初の行: {first_row}")
print(f"最初の行のForce1値: {first_row['Force1']}")  # None

# 特定の行、特定の列のデータにアクセス
force2_at_row3 = collection.columns["Force2"].values[2]
print(f"3行目のForce2値: {force2_at_row3}")  # 0.0

# 別の方法で特定のセルにアクセス
disp2_at_row4 = collection[3]["Displacement2"]
print(f"4行目のDisplacement2値: {disp2_at_row4}")  # 0.56
print()

print("3. スライスによる複数行の取得")
# スライスで行の範囲を取得
rows_3_to_5 = collection[2:5]
print(f"3行目から5行目のコレクション: {len(rows_3_to_5)}行")
for i in range(len(rows_3_to_5)):
    row = rows_3_to_5[i]
    print(f"  行 {i+3}: Force1={row['Force1']}, Displacement1={row['Displacement1']}")
print()

print("4. head()およびtail()メソッド")
# 最初の2行を取得
head_rows = collection.head(2)
print(f"head(2)の結果: {len(head_rows)}行")
print(f"  Force1値: {head_rows['Force1'].values}")

# 最後の2行を取得
tail_rows = collection.tail(2)
print(f"tail(2)の結果: {len(tail_rows)}行")
print(f"  Force1値: {tail_rows['Force1'].values}")
print()

print("5. メタデータへのアクセス")
# メタデータへのアクセス
print(f"タイトル: {collection.metadata.get('title', 'なし')}")
print(f"日付情報: {collection.date}")
print(f"時間情報: {collection.time}")

# 日付と時間の組み合わせ
for i in range(min(3, len(collection))):  # 最初の3行だけ表示
    print(f"  行 {i+1}: {collection.date[i]} {collection.time[i]}")
print()

print("6. チェーンメソッドを使ったデータ抽出と処理")
# 特定のステップと列を選択し、データ変換を行う例
result = (
    collection.ops.select(steps=[3, 4, 5])  # 特定のステップを選択
    .select(columns=["Force1", "Displacement1"])  # 特定の列を選択
    .filter_out_none()  # None値を含む行を除外
    .end()
)

print(f"チェーンメソッド処理後のデータ: {len(result)}行, {len(result.columns)}列")
print(f"選択された列: {list(result.columns.keys())}")
print(f"Force1値: {result['Force1'].values}")
print(f"Displacement1値: {result['Displacement1'].values}")
print()

print("7. 複数のチェーンメソッドを使った高度な分析")
# Force1とDisplacement1の関係を分析する例
analysis_result = (
    result.ops.search_by_value("Force1", ">", 1.0)  # Force1が1.0より大きい行を選択
    .multiply("Force1", 10, result_column="Force1_kgf")  # 単位変換 (kN→kgf)
    .divide("Force1_kgf", "Displacement1", result_column="Stiffness")  # 剛性を計算
    .end()
)

print(f"分析結果: {len(analysis_result)}行")
print(f"作成された列: {list(analysis_result.columns.keys())}")

if len(analysis_result) > 0:
    # 結果を表示
    for i in range(len(analysis_result)):
        row = analysis_result[i]
        step = row["step"]
        force = row["Force1"]
        disp = row["Displacement1"]
        stiff = row["Stiffness"]
        print(
            f"  ステップ {step}: Force1={force}kN, Displacement1={disp}mm, 剛性={stiff:.1f}kgf/mm"
        )
