"""
ColumnCollectionオブジェクトの作成方法を示すサンプルコード
"""

import os
import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import NumberColumn, StringColumn

# 現在のスクリプトからの相対パスでデータファイルを取得
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_CSV_PATH = os.path.join(DATA_DIR, "sample.csv")

# 方法1: 直接インスタンス化
def create_collection_directly():
    """列オブジェクトを直接作成してCollectionを構築"""
    # ステップ値の定義
    steps = list(range(1, 6))
    
    # 列データの定義
    columns = {
        "Force1": NumberColumn(
            ch="CH0", 
            name="Force1", 
            unit="kN", 
            values=[None, None, 0.0, 2.9, 2.9]
        ),
        "Force2": NumberColumn(
            ch="CH1", 
            name="Force2", 
            unit="kN", 
            values=[None, None, 0.0, 8.8, 8.8]
        ),
        "Displacement1": NumberColumn(
            ch="CH2", 
            name="Displacement1", 
            unit="mm", 
            values=[None, None, 0.00, 0.08, 0.08]
        ),
        "Displacement2": NumberColumn(
            ch="CH3", 
            name="Displacement2", 
            unit="mm", 
            values=[None, None, 0.00, 0.56, 0.61]
        )
    }
    
    # メタデータの定義
    metadata = {
        "date": ["2020/11/30", "2020/11/30", "2020/12/01", "2020/12/01", "2020/12/01"],
        "time": ["17:21:36", "17:29:40", "13:22:11", "13:38:05", "13:38:10"],
        "title": "無題"
    }
    
    # ColumnCollectionオブジェクトの作成
    collection = ColumnCollection(
        step=steps,
        columns=columns,
        metadata=metadata
    )
    
    return collection

# 方法2: 値リストからの自動型判定を使用
def create_collection_with_auto_detection():
    """値のリストから自動型判定でCollectionを構築"""
    # ステップ値の定義
    steps = list(range(1, 6))
    
    # 列データの定義（値のリストのみ）
    columns = {
        "Force1": [None, None, 0.0, 2.9, 2.9],
        "Force2": [None, None, 0.0, 8.8, 8.8],
        "Displacement1": [None, None, 0.00, 0.08, 0.08],
        "Displacement2": [None, None, 0.00, 0.56, 0.61]
    }
    
    # メタデータの定義
    metadata = {
        "date": ["2020/11/30", "2020/11/30", "2020/12/01", "2020/12/01", "2020/12/01"],
        "time": ["17:21:36", "17:29:40", "13:22:11", "13:38:05", "13:38:10"],
        "title": "無題",
        "channels": {
            "Force1": {"ch": "CH0", "unit": "kN"},
            "Force2": {"ch": "CH1", "unit": "kN"},
            "Displacement1": {"ch": "CH2", "unit": "mm"},
            "Displacement2": {"ch": "CH3", "unit": "mm"}
        }
    }
    
    # 自動型判定を使用
    collection = ColumnCollection(
        step=steps,
        columns=columns,
        metadata=metadata,
        auto_detect_types=True  # 型の自動判定を有効化
    )
    
    return collection

# 方法3: ファイルからの読み込み
def create_collection_from_file(filepath=SAMPLE_CSV_PATH):
    """CSVファイルからコレクションを作成"""
    try:
        # ファイルからコレクションを作成（CSVフォーマット）
        collection = ColumnCollection.from_file(
            filepath=filepath,
            format_name="csv",  # CSVフォーマットを指定
            auto_detect_types=True
        )
        return collection
    except FileNotFoundError:
        print(f"ファイル '{filepath}' が見つかりません。")
        return None
    except Exception as e:
        print(f"ファイル読み込み中にエラーが発生しました: {str(e)}")
        return None

# 実行例
if __name__ == "__main__":
    print("-- ColumnCollectionの作成方法 --\n")
    
    # 方法1: 直接インスタンス化
    col1 = create_collection_directly()
    print("方法1: 直接インスタンス化")
    print(f"列の数: {len(col1.columns)}")
    print(f"行の数: {len(col1)}")
    print(f"列名: {list(col1.columns.keys())}")
    print(f"メタデータ: {col1.metadata}")
    print()
    
    # 方法2: 値リストからの自動型判定を使用
    col2 = create_collection_with_auto_detection()
    print("方法2: 値リストからの自動型判定")
    print(f"列の数: {len(col2.columns)}")
    print(f"行の数: {len(col2)}")
    print(f"列名: {list(col2.columns.keys())}")
    print(f"列の型: {[type(col).__name__ for col in col2.columns.values()]}")
    print(f"メタデータ: {col2.metadata}")
    print()
    
    # 方法3: ファイルからの読み込み
    print("方法3: ファイルからの読み込み")
    col3 = create_collection_from_file()
    if col3:
        print(f"列の数: {len(col3.columns)}")
        print(f"行の数: {len(col3)}")
        print(f"列名: {list(col3.columns.keys())}")
        print(f"Force1の最初の値: {col3['Force1'].values[0]}")
        print(f"日付データ: {col3.date[:3]}...")
        print(f"時刻データ: {col3.time[:3]}...")
    else:
        print("ファイルからの読み込みに失敗しました。")