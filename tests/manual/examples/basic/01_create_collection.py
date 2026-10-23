"""
ColumnCollectionオブジェクトの作成方法を示すサンプルコード
"""

import os
import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
import tascpy

# 現在のスクリプトからの相対パスでデータファイルを取得
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_CSV_PATH = os.path.join(DATA_DIR, "sample.csv")

print("-- ColumnCollectionの作成方法 --\n")

# 方法1: Column オブジェクトから作成
print("方法1: Column オブジェクトから作成")

# ステップ値の定義
steps = list(range(1, 6))

# 列データの定義（単位・チャンネル名を列ごとに指定）
columns = {
    "Force1": Column("Force1", [None, None, 0.0, 2.9, 2.9], unit="kN", ch="CH0"),
    "Force2": Column("Force2", [None, None, 0.0, 8.8, 8.8], unit="kN", ch="CH1"),
    "Displacement1": Column("Displacement1", [None, None, 0.00, 0.08, 0.08], unit="mm", ch="CH2"),
    "Displacement2": Column("Displacement2", [None, None, 0.00, 0.56, 0.61], unit="mm", ch="CH3"),
}

# ColumnCollectionオブジェクトの作成（日付・時刻はインデックス列として渡す）
col1 = ColumnCollection(
    columns,
    step=steps,
    date=["2020/11/30", "2020/11/30", "2020/12/01", "2020/12/01", "2020/12/01"],
    time=["17:21:36", "17:29:40", "13:22:11", "13:38:05", "13:38:10"],
    metadata={"title": "無題"},
)

print(f"列の数: {len(col1.columns)}")
print(f"行の数: {len(col1)}")
print(f"列名: {col1.columns}")
print(f"単位: {col1.units}")
print(f"メタデータ: {dict(col1.metadata)}")
print()

# チェーンメソッドを使った簡単な操作例
result1 = col1.ops.select(
    columns=["Force1", "Displacement1"]
).end()  # 特定の列を選択  # チェーンを終了して結果を取得
print(f"選択された列: {result1.columns}")
print()

# 方法2: 値リストと単位の辞書から作成
print("方法2: 値リストと単位の辞書から作成")

# 列データの定義（値のリストのみ）
columns = {
    "Force1": [None, None, 0.0, 2.9, 2.9],
    "Force2": [None, None, 0.0, 8.8, 8.8],
    "Displacement1": [None, None, 0.00, 0.08, 0.08],
    "Displacement2": [None, None, 0.00, 0.56, 0.61],
}

col2 = ColumnCollection(
    columns,
    step=list(range(1, 6)),
    units={"Force1": "kN", "Force2": "kN", "Displacement1": "mm", "Displacement2": "mm"},
    metadata={"title": "無題"},
)

print(f"列の数: {len(col2.columns)}")
print(f"行の数: {len(col2)}")
print(f"列名: {col2.columns}")
print(f"列の型: {[str(col2[name].dtype) for name in col2.columns]}")
print(f"単位: {col2.units}")
print()

# チェーンメソッドを使った基本操作
result2 = (
    col2.ops.select(steps=[3, 4, 5])  # 特定のステップを選択
    .select(columns=["Force1", "Force2"])  # 特定の列を選択
    .end()
)
print(f"選択後のステップ数: {len(result2)}")
print(f"選択後の列: {result2.columns}")
print()

# 方法3: ファイルからの読み込み
print("方法3: ファイルからの読み込み")

try:
    # ファイルからコレクションを作成（CSVフォーマット）
    col3 = tascpy.load(SAMPLE_CSV_PATH, format_name="csv")

    print(f"列の数: {len(col3.columns)}")
    print(f"行の数: {len(col3)}")
    print(f"列名: {col3.columns}")
    print(f"単位: {col3.units}")
    print(f"Force1の最初の値: {col3['Force1'][0]}")
    print(f"日付データ: {col3.date[:3]}...")
    print(f"時刻データ: {col3.time[:3]}...")

    # ファイルから読み込んだデータに対するチェーンメソッド操作
    result3 = (
        col3.ops.select(columns=["Force1", "Displacement1"])  # 特定の列を選択
        .multiply(
            "Force1", 2, result_column="DoubleForce"
        )  # Force1を2倍して新しい列を作成（単位は Force1 と同じ）
        # Displacement1が正の行のみをフィルタリング（欠損の行は自動で除外）
        .filter_by_condition("Displacement1", lambda x: x > 0)
        .calculate(
            lambda DoubleForce, Displacement1: DoubleForce / Displacement1,
            result_column="Stiffness", unit="kN/mm",
        )  # 剛性を計算（引数名が列名。結果の単位は明示する）
        .end()
    )

    print("\nチェーンメソッド操作結果:")
    print(f"新たに作成された列: {result3.columns}")
    print(f"単位: {result3.units}")
    if "Stiffness" in result3:
        stiffness = result3["Stiffness"]
        print(f"Stiffnessの最初の有効値: {stiffness[stiffness.first_valid_index]} {stiffness.unit}")

except FileNotFoundError:
    print(f"ファイル '{SAMPLE_CSV_PATH}' が見つかりません。")
