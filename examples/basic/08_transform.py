"""
ColumnCollectionのデータ変換を示すサンプルコード
"""

import os
import math
from tascpy.core.collection import ColumnCollection

# 現在のスクリプトからの相対パスでデータファイルを取得
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_CSV_PATH = os.path.join(DATA_DIR, "sample.csv")

def load_sample_data():
    """サンプルデータの読み込みと拡張"""
    try:
        # CSVファイルからデータを読み込む
        collection = ColumnCollection.from_file(
            filepath=SAMPLE_CSV_PATH,
            format_name="csv",
            auto_detect_types=True
        )
        
        # データの拡張（モデル変換用にさらにデータを追加）
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
        "Displacement2": [None, None, 0.00, 0.56, 0.61, 0.75, 1.10, 1.45, 1.82, 2.20]
    }
    metadata = {
        "date": ["2020/11/30", "2020/11/30", "2020/12/01", "2020/12/01", "2020/12/01", 
                "2020/12/02", "2020/12/02", "2020/12/02", "2020/12/03", "2020/12/03"],
        "time": ["17:21:36", "17:29:40", "13:22:11", "13:38:05", "13:38:10",
                "09:15:00", "10:30:00", "14:45:00", "08:20:00", "09:00:00"],
        "title": "無題"
    }
    return ColumnCollection(steps, columns, metadata, auto_detect_types=True)

def extend_sample_data(collection):
    """サンプルデータに行を追加して拡張する"""
    extended = collection.clone()
    
    # 追加の行データを準備
    new_steps = list(range(max(extended.step.values) + 1, max(extended.step.values) + 6))
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

def preprocess_data_for_transform(collection):
    """変換操作のためにデータを前処理（Noneの処理など）"""
    # 変換操作のデモのために、Noneをもつデータをフィルタリングしたコピーを作成
    result = collection.clone()
    
    # Noneを持つ行をフィルタリング（フィルタ方法の例として）
    ops = result.ops
    filtered = ops.filter_by_value("Force1", lambda x: x is not None).end()
    
    # フィルタリング後のデータが空かチェック
    if len(filtered) == 0:
        print("警告: フィルタリング後のデータが0件です。より緩いフィルタリングを試みます。")
        # より緩いフィルタリングを試す（Force2列が存在する場合）
        if "Force2" in result.columns:
            filtered = result.ops.filter_by_value("Force2", lambda x: x is not None).end()
        
        # それでも空なら、元のデータを返す
        if len(filtered) == 0:
            print("警告: フィルタリング後も0件です。フィルタリングを適用せずに続行します。")
            return result
    
    return filtered

def replace_none_with_zero(collection, columns):
    """指定された列のNone値を0に置き換える"""
    result = collection.clone()
    for column in columns:
        if column in result.columns:
            result.columns[column].values = [
                0 if value is None else value for value in result.columns[column].values
            ]
    return result

def demonstrate_transforms():
    """データ変換操作のデモンストレーション"""
    # データの読み込みと前処理
    collection = load_sample_data()
    # None値を持つ行をフィルタリングしたデータを使用
    filtered = preprocess_data_for_transform(collection)
    
    print("初期データ:")
    print(f"行数: {len(filtered)}")
    print(f"Force1: {filtered['Force1'].values}")
    print(f"Displacement1: {filtered['Displacement1'].values}")
    print()
    
    # None値を0に置き換え（数値演算を行うため）
    filtered = replace_none_with_zero(filtered, ["Force1", "Displacement1", "Force2", "Displacement2"])
    
    # 操作プロキシを取得
    ops = filtered.ops
    
    print("1. selectを使用して変換に必要な列のみを選択")
    # 変換に必要な列のみを選択
    selected = ops.select(columns=["Force1", "Displacement1"]).end()
    selected_ops = selected.ops
    
    print(f"選択された列: {list(selected.columns.keys())}")
    print(f"  選択後の行数: {len(selected)}")
    print()
    
    print("2. 単位変換")
    # kN -> N （1000倍）
    result = selected_ops.multiply("Force1", 1000, result_column="Force1_N").end()
    # 重要: 新しい結果に基づいてopsを更新
    result_ops = result.ops
    
    # mm -> m （0.001倍）
    result = result_ops.multiply("Displacement1", 0.001, result_column="Displacement1_m").end()
    result_ops = result.ops
    
    print(f"力の単位変換: kN -> N")
    print(f"  元データ (kN): {result['Force1'].values}")
    print(f"  変換後 (N): {result['Force1_N'].values}")
    
    print(f"変位の単位変換: mm -> m")
    print(f"  元データ (mm): {result['Displacement1'].values}")
    print(f"  変換後 (m): {result['Displacement1_m'].values}")
    print()
    
    print("3. select_stepを使用して特定のステップの変換")
    # 重要なステップを選択（例: 中間のステップのみ）
    step_indices = list(range(3, 8))
    step_selected = ops.select_step(steps=step_indices).end()
    step_ops = step_selected.ops
    
    # 選択したステップに対して変換を適用
    result = step_ops.multiply("Force1", 1000, result_column="Force1_N").end()
    result_ops = result.ops
    result = result_ops.multiply("Displacement1", 0.001, result_column="Displacement1_m").end()
    
    print(f"選択したステップ値: {result.step.values}")
    print(f"  変換後 (N): {result['Force1_N'].values}")
    print(f"  変換後 (m): {result['Displacement1_m'].values}")
    print()
    
    # 全データに戻して以降の変換を続行
    ops = filtered.ops
    result = ops.multiply("Force1", 1000, result_column="Force1_N").end()
    ops = result.ops
    result = ops.multiply("Displacement1", 0.001, result_column="Displacement1_m").end()
    ops = result.ops
    
    print("4. 応力・ひずみ計算")
    # 応力計算 (σ = F/A): 断面積を50mm² (= 5.0e-5 m²) と仮定
    area_mm2 = 50.0
    area_m2 = area_mm2 * 1e-6
    
    result = ops.divide("Force1_N", area_m2, result_column="Stress_Pa").end()  # Pa = N/m²
    ops = result.ops
    result = ops.divide("Stress_Pa", 1e6, result_column="Stress_MPa").end()    # MPa = Pa/1e6
    ops = result.ops
    
    # ひずみ計算 (ε = ΔL/L): 初期長さを50mm (= 0.05 m) と仮定
    length_m = 0.05
    result = ops.divide("Displacement1_m", length_m, result_column="Strain").end()  # 無次元
    ops = result.ops
    result = ops.multiply("Strain", 100, result_column="Strain_percent").end()  # % = 無次元 * 100
    ops = result.ops
    
    print(f"応力計算: σ = F/A (断面積 = {area_mm2} mm²)")
    print(f"  応力 (MPa): {result['Stress_MPa'].values}")
    
    print(f"ひずみ計算: ε = ΔL/L (初期長さ = {length_m*1000} mm)")
    print(f"  ひずみ (%): {result['Strain_percent'].values}")
    print()
    
    print("5. 特定のステップの応力-ひずみデータを変換")
    # 特定のステップ（例: 後半のデータ）だけを選択
    important_steps = [6, 7, 8, 9, 10]  # 重要なステップ
    step_selected = ops.select_step(steps=important_steps).end()
    step_ops = step_selected.ops
    
    # 選択したデータに対して対数変換を適用
    result = step_ops.log("Strain", base=math.e, result_column="LogStrain").end()
    result_ops = result.ops
    result = result_ops.log("Stress_Pa", base=10, result_column="LogStress").end()
    
    print(f"選択したステップの対数変換:")
    print(f"  選択したステップ: {result.step.values}")
    print(f"  対数ひずみ: {result['LogStrain'].values}")
    print(f"  対数応力: {result['LogStress'].values}")
    print()
    
    # 全データセットに戻る
    ops = result.ops
    
    print("6. 正規化")
    # 変位データの正規化 (min-max法)
    result = ops.normalize("Displacement1", method="minmax", result_column="Disp_norm_minmax").end()
    ops = result.ops
    # 荷重データの正規化 (Z-score法)
    result = ops.normalize("Force1", method="zscore", result_column="Force_norm_zscore").end()
    ops = result.ops
    
    print(f"変位の正規化（Min-Max法: [0,1]範囲）")
    print(f"  元データ: {result['Displacement1'].values}")
    print(f"  正規化後: {result['Disp_norm_minmax'].values}")
    
    print(f"荷重の正規化（Z-score法: 平均0、標準偏差1）")
    print(f"  元データ: {result['Force1'].values}")
    print(f"  正規化後: {result['Force_norm_zscore'].values}")
    print()
    
    # cumsumメソッドが利用できないためスキップ
    print("7. 累積計算（機能は未実装のためスキップします）")
    # 変位の累積値を手動で計算（デモのため）
    disp_values = result['Displacement1'].values
    cumsum_values = []
    running_sum = 0
    for val in disp_values:
        running_sum += val
        cumsum_values.append(running_sum)
    
    print(f"変位の累積和:")
    print(f"  元データ: {disp_values}")
    print(f"  累積和: {cumsum_values}")
    print()
    
    # diffとintegrateも未実装の可能性があるが、確認するためにコードを保持
    try:
        print("8. 微分と積分（近似計算）")
        # 荷重変位曲線からの剛性（接線剛性: dF/dx）計算
        result = ops.diff("Force1", "Displacement1", result_column="Stiffness_dF_dx").end()
        ops = result.ops
        
        # 荷重変位曲線からのエネルギー（面積積分）計算
        result = ops.integrate("Force1", "Displacement1", method="trapezoid", result_column="Energy").end()
        ops = result.ops
        
        print(f"剛性計算（微分: dF/dx）:")
        print(f"  荷重: {result['Force1'].values}")
        print(f"  変位: {result['Displacement1'].values}")
        print(f"  剛性: {result['Stiffness_dF_dx'].values}")
        
        print(f"エネルギー計算（積分: ∫F·dx）:")
        print(f"  エネルギー: {result['Energy'].values}")
    except AttributeError:
        print("8. 微分と積分（機能は未実装のためスキップします）")

if __name__ == "__main__":
    print("-- ColumnCollectionのデータ変換 --\n")
    demonstrate_transforms()