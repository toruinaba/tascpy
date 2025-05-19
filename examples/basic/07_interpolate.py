"""
ColumnCollectionのデータ補間を示すサンプルコード
"""

import os
import numpy as np
from tascpy.core.collection import ColumnCollection

# 現在のスクリプトからの相対パスでデータファイルを取得
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_CSV_PATH = os.path.join(DATA_DIR, "sample.csv")

print("-- ColumnCollectionのデータ補間 --\n")

# サンプルデータの読み込みと前処理
try:
    # CSVファイルからデータを読み込む
    collection = ColumnCollection.from_file(
        filepath=SAMPLE_CSV_PATH, format_name="csv", auto_detect_types=True
    )

    # Noneデータを含まない行だけを抽出（補間に影響するため）
    collection = collection.ops.filter_by_value("Force1", lambda x: x is not None).end()

    # フィルタリング後のデータが少なすぎないかチェック
    if len(collection) < 2:
        print(
            "警告: 補間には少なくとも2点以上のデータが必要です。サンプルデータを作成します。"
        )
        # 不等間隔なステップ値
        steps = [3, 4, 5, 7, 10]

        # 列データの定義（測定データの間隔が不均一な場合を想定）
        columns = {
            "Force1": [0.0, 2.9, 2.9, 5.0, 10.0],
            "Force2": [0.0, 8.8, 8.8, 12.5, 20.0],
            "Displacement1": [0.00, 0.08, 0.08, 0.25, 0.65],
            "Displacement2": [0.00, 0.56, 0.61, 1.10, 2.20],
        }

        # メタデータの定義
        metadata = {
            "date": [
                "2020/12/01",
                "2020/12/01",
                "2020/12/01",
                "2020/12/02",
                "2020/12/03",
            ],
            "time": ["13:22:11", "13:38:05", "13:38:10", "10:30:00", "09:00:00"],
            "test_condition": "不等間隔なサンプルデータ",
        }

        # 自動型判定を使用してコレクションを作成
        collection = ColumnCollection(steps, columns, metadata, auto_detect_types=True)

except FileNotFoundError:
    print(
        f"ファイル '{SAMPLE_CSV_PATH}' が見つかりません。サンプルデータを作成します。"
    )
    # 不等間隔なステップ値
    steps = [3, 4, 5, 7, 10]

    # 列データの定義（測定データの間隔が不均一な場合を想定）
    columns = {
        "Force1": [0.0, 2.9, 2.9, 5.0, 10.0],
        "Force2": [0.0, 8.8, 8.8, 12.5, 20.0],
        "Displacement1": [0.00, 0.08, 0.08, 0.25, 0.65],
        "Displacement2": [0.00, 0.56, 0.61, 1.10, 2.20],
    }

    # メタデータの定義
    metadata = {
        "date": ["2020/12/01", "2020/12/01", "2020/12/01", "2020/12/02", "2020/12/03"],
        "time": ["13:22:11", "13:38:05", "13:38:10", "10:30:00", "09:00:00"],
        "test_condition": "不等間隔なサンプルデータ",
    }

    # 自動型判定を使用してコレクションを作成
    collection = ColumnCollection(steps, columns, metadata, auto_detect_types=True)

# None値が含まれているかチェック
contains_none = any(v is None for v in collection["Displacement1"].values)
if contains_none:
    print(
        "警告: Displacement1列にNone値が含まれているため、None値を除外したデータを準備します"
    )
    # None値を含まない行だけを抽出
    valid_indices = [
        i for i, v in enumerate(collection["Displacement1"].values) if v is not None
    ]
    if len(valid_indices) < 2:
        print("警告: 有効なデータが不足しています。サンプルデータを使用します")
        # 不等間隔なステップ値
        steps = [3, 4, 5, 7, 10]
        # 列データの定義（測定データの間隔が不均一な場合を想定）
        columns = {
            "Force1": [0.0, 2.9, 2.9, 5.0, 10.0],
            "Force2": [0.0, 8.8, 8.8, 12.5, 20.0],
            "Displacement1": [0.00, 0.08, 0.08, 0.25, 0.65],
            "Displacement2": [0.00, 0.56, 0.61, 1.10, 2.20],
        }
        # メタデータの定義
        metadata = {
            "date": [
                "2020/12/01",
                "2020/12/01",
                "2020/12/01",
                "2020/12/02",
                "2020/12/03",
            ],
            "time": ["13:22:11", "13:38:05", "13:38:10", "10:30:00", "09:00:00"],
            "test_condition": "不等間隔なサンプルデータ",
        }
        # 自動型判定を使用してコレクションを作成
        collection = ColumnCollection(steps, columns, metadata, auto_detect_types=True)
    else:
        # None値のない行だけでコレクションを作成
        new_steps = [collection.step.values[i] for i in valid_indices]
        new_columns = {}
        for name, column in collection.columns.items():
            new_columns[name] = [column.values[i] for i in valid_indices]

        # 新しいコレクションを作成
        collection = ColumnCollection(
            step=new_steps,
            columns=new_columns,
            metadata=collection.metadata.copy(),
            auto_detect_types=True,
        )

        print("データ前処理後:")
        print(f"ステップ: {collection.step.values}")
        print(f"Force1: {collection['Force1'].values}")
        print(f"Displacement1: {collection['Displacement1'].values}")
        print()

# 初期データの表示
print("初期データ (不等間隔/欠測値あり):")
print(f"ステップ: {collection.step.values}")
print(f"Force1: {collection['Force1'].values}")
print(f"Displacement1: {collection['Displacement1'].values}")
print()

# 操作プロキシを取得
ops = collection.ops

print("1. 等間隔補間 (ステップ値ベース)")
# ステップ値に基づいて等間隔に補間（10点）
try:
    result = ops.interpolate(point_count=10).end()
    print(f"10点に等間隔補間したデータ:")
    print(f"  新しいステップ: {result.step.values}")
    print(f"  補間後Force1: {result['Force1'].values}")
    print(f"  補間後Displacement1: {result['Displacement1'].values}")
except Exception as e:
    print(f"等間隔補間に失敗しました: {e}")
print()

print("2. 指定ステップ値での補間")
# 特定のステップ値で補間
try:
    specific_steps = [3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10]
    result = ops.interpolate(x_values=specific_steps).end()
    print(f"指定ステップ値で補間したデータ:")
    print(f"  指定ステップ: {specific_steps}")
    print(f"  補間後Force1: {result['Force1'].values}")
except Exception as e:
    print(f"指定ステップ値での補間に失敗しました: {e}")
print()

print("3. 列を選択してからの補間 (チェーンメソッド)")
# 特定の列だけを選択してから補間を適用する例
try:
    result = (
        ops.select(columns=["Force1", "Displacement1"])  # 特定の列のみ選択
        .interpolate(
            point_count=10, method="linear"
        )  # 選択した列に対して補間、点数を指定
        .end()
    )
    print(f"選択した列のみに補間を適用:")
    print(f"  選択された列: {list(result.columns.keys())}")
    print(f"  補間後Force1: {result['Force1'].values}")
    print(f"  補間後Displacement1: {result['Displacement1'].values}")
except Exception as e:
    print(f"選択した列の補間に失敗しました: {e}")
print()

print("4. ステップ範囲を選択してからの補間")
# 特定のステップ範囲だけを選択して補間を適用する例
try:
    min_step, max_step = min(collection.step.values), max(collection.step.values)
    step_range = list(range(min_step, max_step + 1))

    result = (
        ops.select(steps=step_range)  # 特定のステップ範囲を選択
        .interpolate(point_count=len(step_range) * 2, method="linear")  # より細かい補間
        .end()
    )
    print(f"選択したステップ範囲に対して補間:")
    print(f"  選択したステップの範囲: {min_step}～{max_step}")
    print(f"  補間後のステップ数: {len(result)}")
    print(f"  補間後Force1の一部: {result['Force1'].values[:5]}...")
except Exception as e:
    print(f"選択したステップ範囲の補間に失敗しました: {e}")
print()

print("5. 変位を基準にした荷重の補間")
# 変位を等間隔にして、それに対応する荷重値を補間
try:
    result = ops.interpolate(base_column_name="Displacement1", point_count=8).end()
    print(f"変位を基準に補間したデータ:")
    print(f"  等間隔変位: {result['Displacement1'].values}")
    print(f"  対応するForce1: {result['Force1'].values}")
except Exception as e:
    print(f"変位を基準にした補間に失敗しました: {e}")
print()

print("6. 特定の列のみの補間")
# Force1とDisplacement1のみ補間
try:
    result = ops.interpolate(point_count=8, columns=["Force1", "Displacement1"]).end()
    print(f"特定列のみ補間したデータ:")
    print(f"  補間後Force1: {result['Force1'].values}")
    print(f"  補間後Displacement1: {result['Displacement1'].values}")

    # Force2は補間されていないことを確認
    original_force2 = collection["Force2"].values
    result_force2 = result["Force2"].values
    if len(original_force2) < len(result_force2):
        print(f"  Force2は補間されていない (元データと異なる長さでも内容は同じ)")
        print(f"    元のForce2: {original_force2}")
        print(f"    補間後のForce2 (先頭のみ): {result_force2[:len(original_force2)]}")
except Exception as e:
    print(f"特定列のみの補間に失敗しました: {e}")
print()

print("7. 補間方法の指定と比較")
try:
    # 線形補間（デフォルト）- 同じ補間を異なるパラメータで比較
    linear_result = ops.interpolate(point_count=10, method="linear").end()

    # より細かい点数での補間
    dense_result = ops.interpolate(point_count=20, method="linear").end()

    # より粗い点数での補間
    sparse_result = ops.interpolate(point_count=5, method="linear").end()

    print(f"異なる補間密度の比較 (Force1):")
    print(f"  標準補間(10点): {linear_result['Force1'].values}")
    print(f"  高密度補間(20点): {dense_result['Force1'].values[:5]}...")
    print(f"  低密度補間(5点): {sparse_result['Force1'].values}")
except Exception as e:
    print(f"補間方法の指定による補間に失敗しました: {e}")
print()

print("8. メタデータの補間")
try:
    # メタデータ（日付・時間）を時間順で補間
    result = ops.interpolate(point_count=10).end()

    # 補間されたメタデータの確認
    print(f"補間後のメタデータ:")
    print(f"  元の日付: {collection.date}")
    print(f"  補間後の日付: {result.date}")
except Exception as e:
    print(f"メタデータの補間に失敗しました: {e}")
print()

print("9. 補間と数学演算を組み合わせたチェーンメソッド")
try:
    # 補間後に数学演算を適用する例
    result = (
        ops.interpolate(point_count=12)  # 12点に等間隔補間
        .divide(
            "Force1",
            "Displacement1",
            result_column="Stiffness",
            handle_zero_division="none",
        )  # 剛性計算
        .multiply("Stiffness", 0.001, result_column="Stiffness_kN_mm")  # 単位変換
        .end()
    )
    print(f"補間と演算を組み合わせた結果:")
    print(f"  補間後のステップ: {result.step.values}")
    print(f"  計算された剛性 (kN/mm): {result['Stiffness_kN_mm'].values}")
except Exception as e:
    print(f"補間と演算の組み合わせに失敗しました: {e}")
print()

print("10. 高度な補間と分析のパイプライン")
try:
    # サンプルデータを使った確実に動作する分析パイプライン
    # まず最初のデータを作成（明示的に浮動小数点型で定義）
    steps = [3, 4, 5, 7, 10]
    columns = {
        "Force": [0.0, 2.9, 3.5, 5.0, 10.0],
        "Displacement": [
            0.01,
            0.08,
            0.12,
            0.25,
            0.65,
        ],  # ゼロを0.01に変更して除算エラーを回避
    }
    temp_collection = ColumnCollection(steps, columns, auto_detect_types=True)

    # 操作チェーンを実行
    result = (
        temp_collection.ops.interpolate(point_count=10)  # 10点に補間
        .divide(
            "Force",
            "Displacement",
            result_column="Stiffness",
            handle_zero_division="none",
        )  # 剛性計算
        .end()
    )

    # 結果を表示
    print(f"高度な分析パイプラインの結果:")
    print(f"  処理後の行数: {len(result)}行")

    # 剛性値の統計情報を計算（値をfloat型に明示的に変換）
    stiffness_values = []
    for s in result["Stiffness"].values:
        if s is not None:
            try:
                stiffness_values.append(float(s))
            except (TypeError, ValueError):
                pass  # 数値に変換できない値はスキップ

    if stiffness_values:
        avg_stiffness = sum(stiffness_values) / len(stiffness_values)
        print(f"  平均剛性: {avg_stiffness:.2f}")
        print(f"  最大剛性: {max(stiffness_values):.2f}")
        print(f"  最小剛性: {min(stiffness_values):.2f}")

        # 詳細なデータを表示（変位と荷重も明示的に変換）
        print(f"  詳細データ (最初の5行):")
        for i in range(min(5, len(result))):
            step = float(result.step.values[i])
            force = float(result["Force"].values[i])
            disp = float(result["Displacement"].values[i])
            stiff = result["Stiffness"].values[i]
            stiff_val = float(stiff) if stiff is not None else None
            stiff_str = f"{stiff_val:.2f}" if stiff_val is not None else "N/A"
            print(
                f"    ステップ{step:.1f}: 荷重={force:.2f}, 変位={disp:.4f}, 剛性={stiff_str}"
            )

        # 変位と荷重の関係を表示（明示的に変換）
        print(f"  変位-荷重の関係性:")
        first_disp = float(result["Displacement"].values[0])
        last_disp = float(result["Displacement"].values[-1])
        first_force = float(result["Force"].values[0])
        last_force = float(result["Force"].values[-1])

        disp_diff = last_disp - first_disp
        force_diff = last_force - first_force
        overall_stiffness = force_diff / disp_diff if disp_diff > 0 else 0

        print(f"    変位の増加量: {disp_diff:.4f}")
        print(f"    荷重の増加量: {force_diff:.2f}")
        print(f"    全体的な平均剛性: {overall_stiffness:.2f}")
    else:
        print("  有効な剛性データが見つかりませんでした。")
except Exception as e:
    print(f"高度な補間と分析パイプラインに失敗しました: {e}")
