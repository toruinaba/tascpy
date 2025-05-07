"""
ColumnCollectionのフィルタリングと検索を示すサンプルコード
"""

import os
from tascpy.core.collection import ColumnCollection

# 現在のスクリプトからの相対パスでデータファイルを取得
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_CSV_PATH = os.path.join(DATA_DIR, "sample.csv")


def load_sample_data():
    """サンプルデータの読み込みと拡張"""
    try:
        # CSVファイルからデータを読み込む
        collection = ColumnCollection.from_file(
            filepath=SAMPLE_CSV_PATH, format_name="csv", auto_detect_types=True
        )

        # サンプルデータにさらにいくつかの行を追加
        collection_extended = extend_sample_data(collection)
        return collection_extended
    except FileNotFoundError:
        print(f"ファイル '{SAMPLE_CSV_PATH}' が見つかりません。")
        return create_sample_data()  # ファイルが見つからない場合は模擬データを作成


def create_sample_data():
    """CSVファイルがない場合の模擬データ作成（拡張版）"""
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
        "title": "無題",
    }
    return ColumnCollection(steps, columns, metadata, auto_detect_types=True)


def extend_sample_data(collection):
    """サンプルデータに行を追加して拡張する"""
    extended = collection.clone()

    # 追加の行データを準備
    new_steps = list(
        range(max(extended.step.values) + 1, max(extended.step.values) + 6)
    )
    new_force1 = [3.5, 5.0, 7.2, 9.1, 10.0]
    new_force2 = [10.2, 12.5, 15.8, 18.3, 20.0]
    new_disp1 = [0.12, 0.25, 0.38, 0.52, 0.65]
    new_disp2 = [0.75, 1.10, 1.45, 1.82, 2.20]
    new_dates = ["2020/12/02", "2020/12/02", "2020/12/02", "2020/12/03", "2020/12/03"]
    new_times = ["09:15:00", "10:30:00", "14:45:00", "08:20:00", "09:00:00"]

    # 新しいコレクションを作成（既存のデータと新しいデータを結合）
    steps = extended.step.values + new_steps

    columns = {}
    for col_name in extended.columns.keys():
        col = extended.columns[col_name]
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
        columns[col_name] = new_col

    # メタデータも更新
    metadata = extended.metadata.copy()
    if "date" in metadata:
        metadata["date"] = metadata["date"] + new_dates
    if "time" in metadata:
        metadata["time"] = metadata["time"] + new_times

    # 拡張されたコレクションを返す
    return ColumnCollection(steps, columns, metadata)


def demonstrate_filter_search():
    """フィルタリングと検索のデモンストレーション"""
    collection = load_sample_data()

    # データの基本情報を表示
    print(f"読み込んだデータ: {len(collection)}行, {len(collection.columns)}列")
    print(f"Force1データ: {collection['Force1'].values}")
    print(f"日付: {collection.date}")
    print()

    # 操作プロキシを取得
    ops = collection.ops

    print("1. 値によるフィルタリング")
    # 特定の値でフィルタリング - Noneでない値のみ抽出
    result = ops.filter_by_value("Force1", lambda x: x is not None).end()
    print(f"Force1がNoneでない行: {len(result)}行")
    print(f"  Force1値: {result['Force1'].values}")
    print()

    print("2. selectを使った特定の列の選択とフィルタリング")
    # 特定の列だけを選択してからフィルタリング
    selected_cols = ops.select(columns=["Force1", "Displacement1"]).end()
    selected_ops = selected_cols.ops
    result = selected_ops.filter_by_value(
        "Force1", lambda x: x is not None and x > 1.0
    ).end()
    print(f"選択した列でForce1が1.0より大きい行: {len(result)}行")
    print(f"  選択された列: {list(result.columns.keys())}")
    print(f"  Force1値: {result['Force1'].values}")
    print(f"  Displacement1値: {result['Displacement1'].values}")
    print()

    print("3. 比較演算子による検索")
    # 値での比較検索
    result = ops.search_by_value("Force1", ">", 5.0).end()
    print(f"Force1が5.0より大きい行: {len(result)}行")
    print(f"  Force1値: {result['Force1'].values}")
    print(f"  対応するステップ: {result.step.values}")
    print()

    print("4. 値の範囲による検索")
    # 値の範囲で検索
    result = ops.search_by_range("Displacement1", 0.1, 0.5).end()
    print(f"Displacement1が0.1～0.5の範囲の行: {len(result)}行")
    print(f"  Displacement1値: {result['Displacement1'].values}")
    print(f"  Force1値: {result['Force1'].values}")
    print()

    print("5. ステップ値の範囲による検索")
    # ステップ値の範囲で検索
    result = ops.search_by_step_range(3, 6).end()
    print(f"ステップ3～6の行: {len(result)}行")
    print(f"  ステップ値: {result.step.values}")
    print(f"  Force1値: {result['Force1'].values}")
    print()

    print("6. select_stepを使った特定のステップの選択")
    # 特定のステップだけを選択
    step_selected = ops.select_step(steps=[2, 3, 4, 5]).end()
    step_ops = step_selected.ops

    # 選択したステップに対してさらにフィルタリング
    result = step_ops.filter_by_value("Force1", lambda x: x is not None).end()
    print(f"選択したステップでForce1がNoneでない行: {len(result)}行")
    print(f"  ステップ値: {result.step.values}")
    print(f"  Force1値: {result['Force1'].values}")
    print()

    print("7. 条件関数による検索")

    # 条件関数を使用した検索 - 2つの条件の組み合わせ
    def condition_func(row):
        force_ok = row["Force1"] is not None and row["Force1"] > 2.0
        disp_ok = row["Displacement1"] is not None and row["Displacement1"] < 0.5
        return force_ok and disp_ok

    result = ops.search_by_condition(condition_func).end()
    print(f"Force1>2.0かつDisplacement1<0.5の行: {len(result)}行")
    print(f"  Force1値: {result['Force1'].values}")
    print(f"  Displacement1値: {result['Displacement1'].values}")
    print()

    print("8. メタデータによる検索")

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

    # selectとfilter_by_functionの組み合わせ
    step_selected = ops.select_step(
        steps=list(range(3, 11))
    ).end()  # ステップ3から10を選択
    step_ops = step_selected.ops
    result = step_ops.search_by_condition(date_condition).end()

    print(f"選択したステップから2020/12/02のデータを検索: {len(result)}行")
    print(f"  日付: {result.date}")
    print(f"  Force1値: {result['Force1'].values}")
    print()

    print("9. 上位N件の検索")
    # Force1の上位3件を検索
    result = ops.search_top_n("Force1", 3).end()
    print(f"Force1が最大の上位3件:")
    for i in range(len(result)):
        step = result.step.values[i]
        force = result["Force1"].values[i]
        date = result.date[i]
        print(f"  ステップ{step}: {force}kN ({date})")
    print()

    print("10. Noneの処理")
    # Noneを含む行を検索
    result = ops.search_missing_values(["Force1"]).end()
    print(f"Force1がNoneの行: {len(result)}行")
    print(f"  ステップ値: {result.step.values}")
    print(f"  日付: {result.date}")


if __name__ == "__main__":
    print("-- ColumnCollectionのフィルタリングと検索 --\n")
    demonstrate_filter_search()
