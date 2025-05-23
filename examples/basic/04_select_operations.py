"""
ColumnCollectionの選択操作（select）を示すサンプルコード

selectは統合された関数で、列名、行インデックス、またはステップ値による選択をサポートします
"""

import os
from tascpy.core.collection import ColumnCollection

# 現在のスクリプトからの相対パスでデータファイルを取得
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_CSV_PATH = os.path.join(DATA_DIR, "sample.csv")

print("-- ColumnCollectionの選択操作 --\n")

# サンプルデータの読み込みと拡張
try:
    # CSVファイルからデータを読み込む
    collection = ColumnCollection.from_file(
        filepath=SAMPLE_CSV_PATH, format_name="csv", auto_detect_types=True
    )

    # サンプルデータに追加の行を追加して拡張
    # 追加の行データを準備
    new_steps = list(
        range(max(collection.step.values) + 1, max(collection.step.values) + 6)
    )
    new_force1 = [3.5, 5.0, 7.2, 9.1, 10.0]
    new_force2 = [10.2, 12.5, 15.8, 18.3, 20.0]
    new_disp1 = [0.12, 0.25, 0.38, 0.52, 0.65]
    new_disp2 = [0.75, 1.10, 1.45, 1.82, 2.20]
    new_dates = ["2020/12/02", "2020/12/02", "2020/12/02", "2020/12/03", "2020/12/03"]
    new_times = ["09:15:00", "10:30:00", "14:45:00", "08:20:00", "09:00:00"]

    # 新しいコレクションを作成（既存のデータと新しいデータを結合）
    extended_steps = collection.step.values + new_steps

    extended_columns = {}
    for col_name in collection.columns.keys():
        col = collection.columns[col_name]
        if col_name == "Force1":
            new_values = col.values + new_force1
        elif col_name == "Force2":
            new_values = col.values + new_force2
        elif col_name == "Displacement1":
            new_values = col.values + new_disp1
        elif col_name == "Displacement2":
            new_values = col.values + new_disp2
        else:
            new_values = col.values + [None] * len(new_steps)

        # 同じ型のカラムを作成
        new_col = col.clone()
        new_col.values = new_values
        extended_columns[col_name] = new_col

    # メタデータも更新
    extended_metadata = collection.metadata.copy()
    if "date" in extended_metadata:
        extended_metadata["date"] = extended_metadata["date"] + new_dates
    if "time" in extended_metadata:
        extended_metadata["time"] = extended_metadata["time"] + new_times

    # 拡張されたコレクションを作成
    collection = ColumnCollection(extended_steps, extended_columns, extended_metadata)

except FileNotFoundError:
    print(f"ファイル '{SAMPLE_CSV_PATH}' が見つかりません。模擬データを作成します。")
    # CSVファイルがない場合の模擬データ作成（拡張版）
    steps = list(range(1, 11))
    columns = {
        "Force1": [None, None, 0.0, 2.9, 2.9, 3.5, 5.0, 7.2, 9.1, 10.0],
        "Force2": [None, None, 0.0, 8.8, 8.8, 10.2, 12.5, 15.8, 18.3, 20.0],
        "Displacement1": [None, None, 0.00, 0.08, 0.08, 0.12, 0.25, 0.38, 0.52, 0.65],
        "Displacement2": [None, None, 0.00, 0.56, 0.61, 0.75, 1.10, 1.45, 1.82, 2.20],
    }
    metadata = {
        "date": [
            "2020/11/30",
            "2020/11/30",
            "2020/12/01",
            "2020/12/01",
            "2020/12/01",
            "2020/12/02",
            "2020/12/02",
            "2020/12/02",
            "2020/12/03",
            "2020/12/03",
        ],
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
        ],
        "title": "選択操作のサンプル",
    }
    collection = ColumnCollection(steps, columns, metadata, auto_detect_types=True)

# データの基本情報を表示
print(f"読み込んだデータ: {len(collection)}行, {len(collection.columns)}列")
print(f"列名: {list(collection.columns.keys())}")
print(f"ステップ値: {collection.step.values}")
print()

# 操作プロキシを取得
ops = collection.ops

print("1. 列の選択 (select)")
# 特定の列のみを選択
result = ops.select(columns=["Force1", "Displacement1"]).end()
print(f"選択された列: {list(result.columns.keys())}")
print(f"行数: {len(result)}行")
print(f"Force1のデータ: {result['Force1'].values[:5]}...")  # 最初の5要素のみ表示
print()

print("2. 行の選択 (select)")
# 特定の行インデックスを選択
result = ops.select(indices=[0, 3, 6, 9]).end()
print(f"選択された行のステップ値: {result.step.values}")
print(f"選択された行のForce1: {result['Force1'].values}")
print()

print("3. 列と行の両方を選択 (select)")
# 特定の列と行の両方を選択
result = ops.select(columns=["Force1", "Force2"], indices=[2, 4, 6, 8]).end()
print(f"選択された列: {list(result.columns.keys())}")
print(f"選択された行のステップ値: {result.step.values}")
print(f"Force1データ: {result['Force1'].values}")
print(f"Force2データ: {result['Force2'].values}")
print()

print("4. ステップ値による選択 (select with steps)")
# 特定のステップ値を持つ行を選択
result = ops.select(steps=[1, 4, 7, 10]).end()
print(f"選択された行のステップ値: {result.step.values}")
print(f"Force1データ: {result['Force1'].values}")
print()

print("5. 列とステップの両方を選択 (select)")
# 特定の列と特定のステップ値を持つ行を選択
result = ops.select(columns=["Displacement1", "Displacement2"], steps=[3, 6, 9]).end()
print(f"選択された列: {list(result.columns.keys())}")
print(f"選択された行のステップ値: {result.step.values}")
print(f"Displacement1データ: {result['Displacement1'].values}")
print(f"Displacement2データ: {result['Displacement2'].values}")
print()

print("6. by_step_valueとtoleranceオプションの使用")
# ステップ値に近い値を許容範囲を指定して選択
result = ops.select(steps=[1.1, 3.9, 6.95], tolerance=0.1).end()
print(f"選択された行のステップ値（許容範囲あり）: {result.step.values}")

# インデックスとして処理（by_step_value=False）
result_by_index = ops.select(steps=[1, 3, 5], by_step_value=False).end()
print(f"インデックス [1,3,5] での選択（ステップ値）: {result_by_index.step.values}")
print()

print("7. 存在しないステップの扱い")
# 存在しないステップを指定した場合（存在するステップのみが選択され、存在しないステップは無視される）
result = ops.select(steps=[1, 4, 99]).end()
print(f"選択された行のステップ値: {result.step.values}")
print(f"メタデータの'missing_steps': {result.metadata.get('missing_steps', 'なし')}")
print()

print("8. 統合されたselectを使った操作チェーン")
# 一度に列とステップを選択し、その後に演算を適用
result = (
    ops.select(columns=["Force1", "Displacement1"], steps=[4, 6, 8, 10])
    .search_by_value("Displacement1", ">", 0)  # ゼロ除算を回避するためのフィルタリング
    .divide("Force1", "Displacement1", result_column="Stiffness")
    .end()
)

print(f"統合selectでの選択後の処理結果:")
print(f"  選択された列: {list(result.columns.keys())}")
print(f"  選択された行のステップ値: {result.step.values}")
print(f"  計算された剛性: {result['Stiffness'].values}")
print()

print("9. 日付による選択の例")
# まず特定の日付に対応する行インデックスを特定
date_indices = [
    i for i, date in enumerate(collection.date) if date.startswith("2020/12/02")
]

# 特定された行インデックスでデータを選択
result = ops.select(indices=date_indices).end()
print(f"2020/12/02のデータ: {len(result)}行")
print(f"  ステップ値: {result.step.values}")
print(f"  Force1データ: {result['Force1'].values}")
print(f"  日付: {result.date}")
print()

print("10. 複数の選択操作を組み合わせたチェーンメソッド")
# 複数のフィルタリングと選択を組み合わせたチェーンメソッドの例
advanced_result = (
    collection.ops.search_by_value("Force1", ">", 2.0)  # Force1が2.0より大きい行を選択
    .select(columns=["Force1", "Force2", "Displacement1"])  # 必要な列のみ選択
    .select(indices=[0, 2, 4])  # 選択された結果からさらに特定の行を選択
    .multiply("Force1", 2, result_column="Force1_Double")  # 力を2倍に
    .end()
)

print("複数の選択操作を組み合わせた結果:")
print(f"  行数: {len(advanced_result)}行")
print(f"  列: {list(advanced_result.columns.keys())}")
print(f"  Force1: {advanced_result['Force1'].values}")
print(f"  Force1_Double: {advanced_result['Force1_Double'].values}")
print()
