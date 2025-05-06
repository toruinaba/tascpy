"""
ColumnCollectionデータへのアクセス方法を示すサンプルコード
"""

import os
from tascpy.core.collection import ColumnCollection

# 現在のスクリプトからの相対パスでデータファイルを取得
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_CSV_PATH = os.path.join(DATA_DIR, "sample.csv")

def load_sample_data():
    """サンプルデータの読み込み"""
    try:
        # CSVファイルからデータを読み込む
        collection = ColumnCollection.from_file(
            filepath=SAMPLE_CSV_PATH,
            format_name="csv",
            auto_detect_types=True
        )
        return collection
    except FileNotFoundError:
        print(f"ファイル '{SAMPLE_CSV_PATH}' が見つかりません。")
        return create_sample_data()  # ファイルが見つからない場合は模擬データを作成

def create_sample_data():
    """CSVファイルがない場合の模擬データ作成"""
    steps = list(range(1, 6))
    columns = {
        "Force1": [None, None, 0.0, 2.9, 2.9],
        "Force2": [None, None, 0.0, 8.8, 8.8],
        "Displacement1": [None, None, 0.00, 0.08, 0.08],
        "Displacement2": [None, None, 0.00, 0.56, 0.61]
    }
    metadata = {
        "date": ["2020/11/30", "2020/11/30", "2020/12/01", "2020/12/01", "2020/12/01"],
        "time": ["17:21:36", "17:29:40", "13:22:11", "13:38:05", "13:38:10"],
        "title": "無題"
    }
    return ColumnCollection(steps, columns, metadata, auto_detect_types=True)

def demonstrate_data_access():
    """データアクセス方法のデモンストレーション"""
    collection = load_sample_data()
    
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

if __name__ == "__main__":
    print("-- ColumnCollectionデータへのアクセス方法 --\n")
    demonstrate_data_access()