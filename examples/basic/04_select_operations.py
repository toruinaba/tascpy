"""
ColumnCollectionの選択操作（select, select_step）を示すサンプルコード
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
        "title": "選択操作のサンプル",
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


def demonstrate_select_operations():
    """選択操作のデモンストレーション"""
    collection = load_sample_data()

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

    print("4. ステップ値による選択 (select_step)")
    # 特定のステップ値を持つ行を選択
    result = ops.select_step(steps=[1, 4, 7, 10]).end()
    print(f"選択された行のステップ値: {result.step.values}")
    print(f"Force1データ: {result['Force1'].values}")
    print()

    print("5. 列とステップの両方を選択 (select_step)")
    # 特定の列と特定のステップ値を持つ行を選択
    result = ops.select_step(
        columns=["Displacement1", "Displacement2"], steps=[3, 6, 9]
    ).end()
    print(f"選択された列: {list(result.columns.keys())}")
    print(f"選択された行のステップ値: {result.step.values}")
    print(f"Displacement1データ: {result['Displacement1'].values}")
    print(f"Displacement2データ: {result['Displacement2'].values}")
    print()

    print("6. 存在しないステップの扱い")
    # 存在しないステップを指定した場合（存在するステップのみが選択され、存在しないステップは無視される）
    result = ops.select_step(steps=[1, 4, 99]).end()
    print(f"選択された行のステップ値: {result.step.values}")
    print(
        f"メタデータの'missing_steps': {result.metadata.get('missing_steps', 'なし')}"
    )
    print()

    print("7. 選択操作と他の操作の組み合わせ")
    # 選択した後に数学演算を適用
    result = (
        ops.select(columns=["Force1", "Displacement1"])  # まず列を選択
        .select_step(steps=[4, 6, 8, 10])  # 次に特定のステップの行を選択
        .divide(
            "Force1",
            "Displacement1",
            result_column="Stiffness",
            handle_zero_division="none",
        )  # 剛性を計算
        .end()
    )

    print(f"選択後の処理結果:")
    print(f"  選択された列: {list(result.columns.keys())}")
    print(f"  選択された行のステップ値: {result.step.values}")
    print(f"  計算された剛性: {result['Stiffness'].values}")
    print()

    print("8. 日付による選択の例")
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


if __name__ == "__main__":
    print("-- ColumnCollectionの選択操作 --\n")
    demonstrate_select_operations()
