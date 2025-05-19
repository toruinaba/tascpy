"""
ColumnCollectionのフィルタリングと検索を示すサンプルコード
"""

import os
from tascpy.core.collection import ColumnCollection

# 現在のスクリプトからの相対パスでデータファイルを取得
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_CSV_PATH = os.path.join(DATA_DIR, "sample.csv")

print("-- ColumnCollectionのフィルタリングと検索 --\n")

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
        "title": "フィルタリングと検索のサンプル",
    }
    collection = ColumnCollection(steps, columns, metadata, auto_detect_types=True)

# データの基本情報を表示
print(f"読み込んだデータ: {len(collection)}行, {len(collection.columns)}列")
print(f"Force1データ: {collection['Force1'].values}")
print(f"日付: {collection.date}")
print()

# 操作プロキシを取得
ops = collection.ops

print("1. 値によるフィルタリング")
# 特定の値でフィルタリング - チェーンメソッドを使用
result = ops.filter_by_value("Force1", lambda x: x is not None).end()
print(f"Force1がNoneでない行: {len(result)}行")
print(f"  Force1値: {result['Force1'].values}")
print()

print("2. チェーンメソッドによる列の選択とフィルタリング")
# 特定の列を選択してからフィルタリング - チェーンメソッドを一連の流れで実行
result = (
    ops.select(columns=["Force1", "Displacement1"])
    .filter_by_value("Force1", lambda x: x is not None and x > 1.0)
    .end()
)
print(f"選択した列でForce1が1.0より大きい行: {len(result)}行")
print(f"  選択された列: {list(result.columns.keys())}")
print(f"  Force1値: {result['Force1'].values}")
print(f"  Displacement1値: {result['Displacement1'].values}")
print()

print("3. 比較演算子による検索")
# 値での比較検索 - チェーンメソッド使用
result = ops.search_by_value("Force1", ">", 5.0).end()
print(f"Force1が5.0より大きい行: {len(result)}行")
print(f"  Force1値: {result['Force1'].values}")
print(f"  対応するステップ: {result.step.values}")
print()

print("4. 値の範囲による検索")
# 値の範囲で検索 - チェーンメソッド使用
result = ops.search_by_range("Displacement1", 0.1, 0.5).end()
print(f"Displacement1が0.1～0.5の範囲の行: {len(result)}行")
print(f"  Displacement1値: {result['Displacement1'].values}")
print(f"  Force1値: {result['Force1'].values}")
print()

print("5. ステップ値の範囲による検索")
# ステップ値の範囲で検索 - チェーンメソッド使用
result = ops.search_by_step_range(3, 6).end()
print(f"ステップ3～6の行: {len(result)}行")
print(f"  ステップ値: {result.step.values}")
print(f"  Force1値: {result['Force1'].values}")
print()

print("6. ステップ選択と値のフィルタリングを組み合わせたチェーンメソッド")
# 特定のステップを選択してから値でフィルタリング - 一つのチェーンで実行
result = (
    ops.select(steps=[2, 3, 4, 5])
    .filter_by_value("Force1", lambda x: x is not None)
    .end()
)
print(f"選択したステップでForce1がNoneでない行: {len(result)}行")
print(f"  ステップ値: {result.step.values}")
print(f"  Force1値: {result['Force1'].values}")
print()

print("7. 条件関数による複合検索")


# 条件関数を使用した検索 - 2つの条件の組み合わせ
def condition_func(row):
    force_ok = row["Force1"] is not None and row["Force1"] > 2.0
    disp_ok = row["Displacement1"] is not None and row["Displacement1"] < 0.5
    return force_ok and disp_ok


# 条件関数を使用したチェーンメソッド
result = ops.search_by_condition(condition_func).end()
print(f"Force1>2.0かつDisplacement1<0.5の行: {len(result)}行")
print(f"  Force1値: {result['Force1'].values}")
print(f"  Displacement1値: {result['Displacement1'].values}")
print()

print("8. メタデータによる検索とフィルタリングの組み合わせ")


# メタデータ（日付）に基づく条件関数
def date_condition(row):
    # row_data辞書には列の値は含まれるが、stepやメタデータは含まれない
    # 現在の行のステップ値を推測するため、同じ値を持つ行を探す
    for i, step_val in enumerate(collection.step.values):
        all_match = True
        for col_name, col_val in row.items():
            if collection[col_name].values[i] != col_val:
                all_match = False
                break
        if all_match:
            # 一致する行が見つかった
            date = collection.date[i]
            return date == "2020/12/02"
    return False  # 一致する行が見つからなかった


# 複数の操作を一つのチェーンメソッドで実行
result = (
    ops.select(steps=list(range(3, 11)))  # ステップ3から10を選択
    .search_by_condition(date_condition)  # 日付条件で検索
    .end()
)

print(f"選択したステップから2020/12/02のデータを検索: {len(result)}行")
print(f"  日付: {result.date}")
print(f"  Force1値: {result['Force1'].values}")
print()

print("9. 上位N件の検索")
# Force1の上位3件を検索 - チェーンメソッド使用
result = ops.search_top_n("Force1", 3).end()
print(f"Force1が最大の上位3件:")
for i in range(len(result)):
    step = result.step.values[i]
    force = result["Force1"].values[i]
    date = result.date[i]
    print(f"  ステップ{step}: {force}kN ({date})")
print()

print("10. Noneの処理と複合検索の組み合わせ")
# Noneを含む行を検索し、別の操作と組み合わせる
result = ops.search_missing_values(["Force1"]).end()  # Force1がNoneの行を検索
print(f"Force1がNoneの行: {len(result)}行")
print(f"  ステップ値: {result.step.values}")
print(f"  日付: {result.date}")
print()

print("11. 複数の検索条件を組み合わせた高度なチェーンメソッド")
# 複数の検索とフィルタリング操作を組み合わせたチェーンメソッド
advanced_result = (
    ops.search_by_value("Force1", ">", 2.0)  # Force1が2.0より大きい行を選択
    .search_by_range(
        "Displacement1", 0.0, 0.5
    )  # その中からDisplacement1が0～0.5の行を選択
    .select(columns=["Force1", "Displacement1", "Force2"])  # 必要な列のみ選択
    .evaluate("Force1 / Displacement1", result_column="Stiffness")  # 剛性を計算
    .end()
)

print("複数の検索条件と計算を組み合わせた結果:")
print(f"  処理後の行数: {len(advanced_result)}行")
print(f"  選択された列: {list(advanced_result.columns.keys())}")
print(f"  Force1値: {advanced_result['Force1'].values}")
print(f"  剛性値: {advanced_result['Stiffness'].values}")
print()

print("12. データのカテゴリ分析")
# 有効なデータのみ選択（Force1が値を持ち、0より大きい）
valid_data = ops.search_by_value("Force1", ">", 0.0).end()

# 日付ごとにデータを分類して表示
print("日付ごとのデータ分析:")

# 出現する日付をユニークに取得
unique_dates = set()
for date in collection.date:
    unique_dates.add(date)

# 日付ごとにデータを取得して統計情報を計算
for date in sorted(unique_dates):
    # 各日付のデータを収集（ステップとForce1の値）
    date_steps = []
    date_forces = []

    for i, d in enumerate(collection.date):
        if d == date and i < len(collection["Force1"].values):
            force = collection["Force1"].values[i]
            if force is not None and force > 0:
                date_steps.append(collection.step.values[i])
                date_forces.append(force)

    # 平均荷重を計算
    avg_force = sum(date_forces) / len(date_forces) if date_forces else 0

    print(f"  {date}: {len(date_forces)}行, 平均Force1 = {avg_force:.2f}kN")
