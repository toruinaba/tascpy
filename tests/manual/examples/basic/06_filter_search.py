"""
ColumnCollectionのフィルタリングと検索を示すサンプルコード
"""

import os
import numpy as np
from tascpy.core.collection import ColumnCollection, concat
import tascpy

# 現在のスクリプトからの相対パスでデータファイルを取得
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_CSV_PATH = os.path.join(DATA_DIR, "sample.csv")

print("-- ColumnCollectionのフィルタリングと検索 --\n")

# サンプルデータの読み込みと拡張
try:
    # CSVファイルからデータを読み込む
    collection = tascpy.load(SAMPLE_CSV_PATH, format_name="csv")

    # サンプルデータに追加の行を連結して拡張する
    last_step = int(collection.step.max())
    extra = ColumnCollection(
        {
            "Force1": [3.5, 5.0, 7.2, 9.1, 10.0],
            "Force2": [10.2, 12.5, 15.8, 18.3, 20.0],
            "Displacement1": [0.12, 0.25, 0.38, 0.52, 0.65],
            "Displacement2": [0.75, 1.10, 1.45, 1.82, 2.20],
        },
        step=list(range(last_step + 1, last_step + 6)),
        date=["2020/12/02", "2020/12/02", "2020/12/02", "2020/12/03", "2020/12/03"],
        time=["09:15:00", "10:30:00", "14:45:00", "08:20:00", "09:00:00"],
    )
    # 列メタ（単位など）は最初に現れたコレクションのものが使われる
    collection = concat([collection, extra])

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
    collection = ColumnCollection(
        columns,
        step=steps,
        date=metadata.pop("date"),
        time=metadata.pop("time"),
        units={"Force1": "kN", "Force2": "kN", "Displacement1": "mm", "Displacement2": "mm"},
        metadata=metadata,
    )

# データの基本情報を表示
print(f"読み込んだデータ: {len(collection)}行, {len(collection.columns)}列")
print(f"Force1データ: {collection['Force1'].values}")
print(f"日付: {collection.date}")
print(f"単位: {collection.units}")
print()

# 操作プロキシを取得
ops = collection.ops

print("1. 値によるフィルタリング")
# 特定の値と一致する行を抽出 - filter_by_value は値の一致で判定する
result = ops.filter_by_value("Force1", 2.9).end()
print(f"Force1が2.9の行: {len(result)}行")
print(f"  Force1値: {result['Force1'].values}")
print()

print("2. チェーンメソッドによる列の選択とフィルタリング")
# 特定の列を選択してからフィルタリング - チェーンメソッドを一連の流れで実行
result = (
    ops.select(columns=["Force1", "Displacement1"])
    .filter_by_condition("Force1", lambda x: x > 1.0)
    .end()
)
print(f"選択した列でForce1が1.0より大きい行: {len(result)}行")
print(f"  選択された列: {result.columns}")
print(f"  Force1値: {result['Force1'].values}")
print(f"  Displacement1値: {result['Displacement1'].values}")
print()

print("3. 比較演算子による検索")
# 値での比較検索 - チェーンメソッド使用
result = ops.filter_by_condition("Force1", lambda x: x > 5.0).end()
print(f"Force1が5.0より大きい行: {len(result)}行")
print(f"  Force1値: {result['Force1'].values}")
print(f"  対応するステップ: {result.step}")
print()

print("4. 値の範囲による検索")
# 値の範囲で絞り込む - filter_by_condition に範囲条件を渡す
result = ops.filter_by_condition("Displacement1", lambda x: 0.1 <= x <= 0.5).end()
print(f"Displacement1が0.1～0.5の範囲の行: {len(result)}行")
print(f"  Displacement1値: {result['Displacement1'].values}")
print(f"  Force1値: {result['Force1'].values}")
print()

print("5. ステップ値の範囲による検索")
# ステップ値の範囲で選択 - select にステップ値のリストを渡す
step_range = [s for s in collection.step if 3 <= s <= 6]
result = ops.select(steps=step_range).end()
print(f"ステップ3～6の行: {len(result)}行")
print(f"  ステップ値: {result.step}")
print(f"  Force1値: {result['Force1'].values}")
print()

print("6. ステップ選択と欠損値の除外を組み合わせたチェーンメソッド")
# 特定のステップを選択してから Force1 が欠損している行を除外 - 一つのチェーンで実行
result = (
    ops.select(steps=[2, 3, 4, 5])
    .filter_out_none(columns=["Force1"])
    .end()
)
print(f"選択したステップでForce1がNoneでない行: {len(result)}行")
print(f"  ステップ値: {result.step}")
print(f"  Force1値: {result['Force1'].values}")
print()

print("7. 複数列の条件による複合検索")
# 複数列にまたがる条件は、条件ごとに filter_by_condition を連ねる
result = (
    ops.filter_by_condition("Force1", lambda x: x > 2.0)
    .filter_by_condition("Displacement1", lambda x: x < 0.5)
    .end()
)
print(f"Force1>2.0かつDisplacement1<0.5の行: {len(result)}行")
print(f"  Force1値: {result['Force1'].values}")
print(f"  Displacement1値: {result['Displacement1'].values}")
print()

print("8. 日付による検索とフィルタリングの組み合わせ")
# 日付はインデックス列 (collection.date) に保持されているため、該当する行インデックスを求めて select に渡す
date_indices = [i for i, d in enumerate(collection.date) if d == "2020/12/02"]
result = (
    ops.select(indices=date_indices)
    .select(steps=[s for s in collection.step if 3 <= s <= 10])  # ステップ3から10を選択
    .end()
)
print(f"選択したステップから2020/12/02のデータを検索: {len(result)}行")
print(f"  ステップ値: {result.step}")
print(f"  Force1値: {result['Force1'].values}")
print()

print("9. 上位N件の検索")
# Force1の上位3件の行インデックスを NumPy で求めて select に渡す
force1 = collection["Force1"].values  # 欠損は NaN
top_indices = sorted(np.argsort(np.nan_to_num(force1, nan=-np.inf))[::-1][:3].tolist())
result = ops.select(indices=top_indices).end()
print("Force1が最大の上位3件:")
for i in range(len(result)):
    print(f"  ステップ{result.step[i]}: {result['Force1'][i]}{result['Force1'].unit} ({result.date[i]})")
print()

print("10. 欠損値を含む行の抽出")
# Force1が欠損している行インデックスを求めて select に渡す
missing_indices = np.where(np.isnan(force1))[0].tolist()
result = ops.select(indices=missing_indices).end()
print(f"Force1がNoneの行: {len(result)}行")
print(f"  ステップ値: {result.step}")
print(f"  日付: {result.date}")
print()

print("11. 複数の検索条件を組み合わせた高度なチェーンメソッド")
# 複数の検索とフィルタリング操作を組み合わせたチェーンメソッド
advanced_result = (
    ops.filter_by_condition("Force1", lambda x: x > 2.0)  # Force1が2.0より大きい行を選択
    .filter_by_condition(
        "Displacement1", lambda x: 0.0 <= x <= 0.5
    )  # その中からDisplacement1が0～0.5の行を選択
    .select(columns=["Force1", "Displacement1", "Force2"])  # 必要な列のみ選択
    .calculate(lambda Force1, Displacement1: Force1 / Displacement1,
               result_column="Stiffness", unit="kN/mm")  # 剛性を計算
    .end()
)

print("複数の検索条件と計算を組み合わせた結果:")
print(f"  処理後の行数: {len(advanced_result)}行")
print(f"  選択された列: {advanced_result.columns}")
print(f"  Force1値: {advanced_result['Force1'].values}")
print(f"  剛性値: {advanced_result['Stiffness'].values}")
print()

print("12. データのカテゴリ分析")
# 有効なデータのみ選択（Force1が値を持ち、0より大きい）
valid_data = ops.filter_by_condition("Force1", lambda x: x > 0.0).end()  # 欠損の行は自動で除外

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
            force = collection["Force1"][i]  # 欠損は None
            if force is not None and force > 0:
                date_steps.append(collection.step[i])
                date_forces.append(force)

    # 平均荷重を計算
    avg_force = sum(date_forces) / len(date_forces) if date_forces else 0

    print(f"  {date}: {len(date_forces)}行, 平均Force1 = {avg_force:.2f}kN")
