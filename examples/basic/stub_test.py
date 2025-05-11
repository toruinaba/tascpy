"""
スタブファイルのテスト用スクリプト

このスクリプトはPylanceの自動補完が正常に機能することを確認するためのものです。
"""

from tascpy.core.collection import ColumnCollection
import numpy as np

# サンプルデータの作成
steps = list(range(10))
columns = {
    "Force": [i * 2 for i in range(10)],
    "Displacement": [i * 0.1 for i in range(10)],
}

# コレクションの作成
collection = ColumnCollection(steps, columns, auto_detect_types=True)

# 操作プロキシを取得 (ここでPylanceの自動補完が機能するはず)
ops = collection.ops

# 数学的演算の例
# .で継続するとメソッド候補が表示されるはず
result = (
    ops.add("Force", 1.0, result_column="Force_plus_1")
    .multiply("Force", 2, result_column="Force_double")
    .divide("Force_double", "Displacement", result_column="Stiffness")
    .end()
)

# 結果の表示
print("Result columns:", list(result.columns.keys()))
print("Force_plus_1:", result["Force_plus_1"].values[:5], "...")
print("Force_double:", result["Force_double"].values[:5], "...")
print("Stiffness:", result["Stiffness"].values[:5], "...")

# ドメイン特化コレクションの作成
from tascpy.domains.load_displacement import LoadDisplacementCollection

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

# ドメイン特化操作の使用
# .で継続するとドメイン固有のメソッド候補も表示されるはず
ld_ops = ld_collection.ops
ld_result = ld_ops.end()

print("\nLoad-Displacement Domain:")
print("Domain:", ld_result.domain)
