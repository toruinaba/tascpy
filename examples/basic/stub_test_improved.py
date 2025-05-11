"""
改良されたスタブシステムのテスト用スクリプト

このスクリプトは改良したスタブ生成システムが正しく働くことを確認します。
"""

from tascpy.core.collection import ColumnCollection
import numpy as np
from typing import Optional, List, Dict, Union, Any

print("スタブテストを開始します...")

# サンプルデータの作成
steps = list(range(10))
columns = {
    "Force": [i * 2 for i in range(10)],
    "Displacement": [i * 0.1 for i in range(10)],
    "OptionalCol": [i if i > 5 else None for i in range(10)],
}

print("サンプルデータを作成しました")

# コレクションの作成
collection = ColumnCollection(steps, columns, auto_detect_types=True)
print("コレクションを作成しました")

# 操作プロキシを取得 (ここでPylanceの自動補完が機能するはず)
ops = collection.ops

# 複雑な型を含むメソッドチェーンのテスト
# Optionalやリスト型を含むメソッドを使用
print("メソッドチェーンを実行します...")
result = (
    ops
    # Optional型の引数を持つメソッド
    .filter_by_value(
        "Force", 8, tolerance=0.1
    )  # Forceの値が8に近いものをフィルタリング
    # 選択操作（シンプルにする）
    .select(columns=["Force", "Displacement"])
    # 通常の操作
    .add("Force", 1.0, result_column="Force_plus_1").multiply(
        "Force", 2, result_column="Force_double"
    )
    # 複雑な操作を除外
    .end()
)

print("Result operation chain completed successfully!")
print("Result columns:", list(result.columns.keys()))

# ドメイン特化コレクションのテスト
from tascpy.domains.load_displacement import LoadDisplacementCollection

# ドメイン特化コレクションの作成
ld_collection = LoadDisplacementCollection(
    step=steps,
    columns={
        "load": [i * 2 for i in range(10)],
        "displacement": [i * 0.1 for i in range(10)],
    },
    load_column="load",
    displacement_column="displacement",
    auto_detect_types=True,
)

# ドメイン特化操作の使用テスト
# ここでもPylanceの自動補完が適切に機能するはず
ld_ops = ld_collection.ops
ld_result = ld_ops.end()

print("\nDomain-specific operation test passed!")
print("Domain:", ld_result.domain)
