"""
ColumnCollectionのデータ補間を示すサンプルコード
"""

import os
import numpy as np
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
        
        # Noneデータを含む行が補間に影響するので、前処理として特定のみを抽出
        filtered = preprocess_data_for_interpolation(collection)
        return filtered
    except FileNotFoundError:
        print(f"ファイル '{SAMPLE_CSV_PATH}' が見つかりません。")
        return create_sample_data()  # ファイルが見つからない場合は模擬データを作成

def create_sample_data():
    """CSVファイルがない場合の不等間隔なサンプルデータを作成"""
    # 不等間隔なステップ値
    steps = [3, 4, 5, 7, 10]
    
    # 列データの定義（測定データの間隔が不均一な場合を想定）
    columns = {
        "Force1": [0.0, 2.9, 2.9, 5.0, 10.0],
        "Force2": [0.0, 8.8, 8.8, 12.5, 20.0],
        "Displacement1": [0.00, 0.08, 0.08, 0.25, 0.65],
        "Displacement2": [0.00, 0.56, 0.61, 1.10, 2.20]
    }
    
    # メタデータの定義
    metadata = {
        "date": ["2020/12/01", "2020/12/01", "2020/12/01", "2020/12/02", "2020/12/03"],
        "time": ["13:22:11", "13:38:05", "13:38:10", "10:30:00", "09:00:00"],
        "test_condition": "不等間隔なサンプルデータ"
    }
    
    # 自動型判定を使用してコレクションを作成
    return ColumnCollection(steps, columns, metadata, auto_detect_types=True)

def preprocess_data_for_interpolation(collection):
    """補間用にデータを前処理（Noneを含まないデータを抽出）"""
    # 補間のデモのために、Noneを含まない行だけを抽出
    ops = collection.ops
    filtered = ops.filter_by_value("Force1", lambda x: x is not None).end()
    
    # フィルタリング後のデータが空かチェック
    if len(filtered) == 0:
        print("警告: フィルタリング後のデータが0件です。より緩いフィルタリングを試みます。")
        # 別の列でフィルタリングを試みる
        if "Force2" in collection.columns:
            filtered = collection.ops.filter_by_value("Force2", lambda x: x is not None).end()
        
        # それでも空なら、元のデータを返す
        if len(filtered) == 0:
            print("警告: フィルタリング後も0件です。フィルタリングを適用せずに続行します。")
            return collection
    
    # 少なくとも2点以上のデータがないと補間できないことをチェック
    if len(filtered) < 2:
        print("警告: 補間には少なくとも2点以上のデータが必要です。フィルタリングを適用せずに続行します。")
        return collection
    
    return filtered

def demonstrate_interpolation():
    """データ補間のデモンストレーション"""
    collection = load_sample_data()
    
    print("初期データ (不等間隔/欠測値あり):")
    print(f"ステップ: {collection.step.values}")
    print(f"Force1: {collection['Force1'].values}")
    print(f"Displacement1: {collection['Displacement1'].values}")
    print()
    
    # None値が含まれているかチェック
    contains_none = any(v is None for v in collection['Displacement1'].values)
    if contains_none:
        print("警告: Displacement1列にNone値が含まれているため、None値を除外したデータを準備します")
        # None値を含まない行だけを抽出
        valid_indices = [i for i, v in enumerate(collection['Displacement1'].values) if v is not None]
        if len(valid_indices) < 2:
            print("警告: 有効なデータが不足しています。サンプルデータを使用します")
            collection = create_sample_data()
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
                auto_detect_types=True
            )
            
            print("データ前処理後:")
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
    
    print("3. selectを使用して補間したい列だけを選択")
    # 特定の列だけを選択（存在するカラムのみ）
    columns_to_select = ["Force1", "Displacement1"]
    if "time" in collection.metadata:
        # metadata内に"time"が存在する場合は追加
        print("  timeメタデータを使用します")
    
    selected = ops.select(columns=columns_to_select).end()
    selected_ops = selected.ops
    
    try:
        # 選択した列に対して補間
        result = selected_ops.interpolate_missing(
            method="linear", 
            columns=["Force1", "Displacement1"]
        ).end()
        
        print(f"選択した列のみに補間を適用:")
        print(f"  選択された列: {list(result.columns.keys())}")
        print(f"  補間後Force1: {result['Force1'].values}")
        print(f"  補間後Displacement1: {result['Displacement1'].values}")
    except Exception as e:
        print(f"選択した列の補間に失敗しました: {e}")
    print()
    
    print("4. select_stepを使用して特定のステップ範囲に補間")
    # 特定のステップ範囲だけを選択
    min_step, max_step = min(collection.step.values), max(collection.step.values)
    step_range = list(range(min_step, max_step + 1))
    step_selected = ops.select_step(steps=step_range).end()
    step_ops = step_selected.ops
    
    try:
        # 選択したステップ範囲に対して補間
        result = step_ops.interpolate(
            point_count=len(step_range)*2,  # より細かい補間
            method="cubic"
        ).end()
        
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
        original_force2 = collection['Force2'].values
        result_force2 = result['Force2'].values
        if len(original_force2) < len(result_force2):
            print(f"  Force2は補間されていない (元データと異なる長さでも内容は同じ)")
            print(f"    元のForce2: {original_force2}")
            print(f"    補間後のForce2 (先頭のみ): {result_force2[:len(original_force2)]}")
    except Exception as e:
        print(f"特定列のみの補間に失敗しました: {e}")
    print()
    
    print("7. 補間方法の指定")
    try:
        # 線形補間（デフォルト）
        linear_result = ops.interpolate(point_count=10, method="linear").end()
        
        # スプライン補間
        spline_result = ops.interpolate(point_count=10, method="spline").end()
        
        # 最近傍補間（前方または後方の値を使用）
        nearest_result = ops.interpolate(point_count=10, method="nearest").end()
        
        print(f"異なる補間方法の比較 (Force1):")
        print(f"  線形補間: {linear_result['Force1'].values}")
        print(f"  スプライン補間: {spline_result['Force1'].values}")
        print(f"  最近傍補間: {nearest_result['Force1'].values}")
    except Exception as e:
        print(f"補間方法の指定による補間に失敗しました: {e}")
    print()
    
    print("8. メタデータの補間")
    try:
        # メタデータ（日付・時間）を時間順で補間
        result = ops.interpolate(point_count=10).end()
        
        # 補間されたメタデータの確認（日付と時間は線形補間するのが難しいため、近傍値が使われることが多い）
        print(f"補間後のメタデータ:")
        print(f"  元の日付: {collection.date}")
        print(f"  補間後の日付: {result.date}")
    except Exception as e:
        print(f"メタデータの補間に失敗しました: {e}")

if __name__ == "__main__":
    print("-- ColumnCollectionのデータ補間 --\n")
    demonstrate_interpolation()