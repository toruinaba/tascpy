"""
ColumnCollectionの数学演算操作を示すサンプルコード
"""

import os
import math
from tascpy.core.collection import ColumnCollection

# 現在のスクリプトからの相対パスでデータファイルを取得
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_CSV_PATH = os.path.join(DATA_DIR, "sample.csv")


def load_sample_data():
    """サンプルデータの読み込み"""
    try:
        # CSVファイルからデータを読み込む
        collection = ColumnCollection.from_file(
            filepath=SAMPLE_CSV_PATH, format_name="csv", auto_detect_types=True
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
        "Displacement2": [None, None, 0.00, 0.56, 0.61],
    }
    metadata = {
        "date": ["2020/11/30", "2020/11/30", "2020/12/01", "2020/12/01", "2020/12/01"],
        "time": ["17:21:36", "17:29:40", "13:22:11", "13:38:05", "13:38:10"],
        "title": "無題",
    }
    return ColumnCollection(steps, columns, metadata, auto_detect_types=True)


def preprocess_data_for_math(collection):
    """数学演算のためにデータを前処理（Noneの処理など）"""
    # 数学演算のデモのために、Noneを0に置き換えたコピーを作成
    result = collection.clone()

    # 力と変位のデータでNoneを0に置換
    for col_name in ["Force1", "Force2", "Displacement1", "Displacement2"]:
        if col_name in result.columns:
            result[col_name].values = [
                0.0 if v is None else v for v in result[col_name].values
            ]

    return result


def demonstrate_math_operations():
    """数学演算操作のデモンストレーション"""
    collection = load_sample_data()

    print("初期データ:")
    print(f"Force1: {collection['Force1'].values}")
    print(f"Force2: {collection['Force2'].values}")
    print(f"Displacement1: {collection['Displacement1'].values}")
    print(f"Displacement2: {collection['Displacement2'].values}")
    print()

    # 操作プロキシを取得
    ops = collection.ops

    print("1. 基本的な算術演算")
    # 足し算: 定数加算
    result = ops.add("Force1", 1.0).end()  # Force1 + 1.0
    print(f"Force1 + 1.0 = {result['Force1+1.0'].values}")

    # 引き算: 列同士
    result = ops.subtract("Force2", "Force1").end()  # Force2 - Force1
    print(f"Force2 - Force1 = {result['Force2-Force1'].values}")

    # 掛け算: 定数乗算
    result = ops.multiply("Displacement1", 10).end()  # Displacement1 * 10
    print(f"Displacement1 * 10 = {result['Displacement1*10'].values}")

    # 割り算: 列同士（ゼロ除算はNoneとして扱う）
    result = ops.divide(
        "Force1", "Displacement1", handle_zero_division="none"
    ).end()  # Force1 / Displacement1
    print(f"Force1 / Displacement1 = {result['Force1/Displacement1'].values}")
    print()

    print("2. 複合演算と新しい列名の指定")
    # 複数の列の合計（合力）を計算し、新しい列名を指定
    result = ops.add("Force1", "Force2", result_column="TotalForce").end()
    print(f"TotalForce (Force1 + Force2) = {result['TotalForce'].values}")

    # 変位の差分を計算（結果の列名は自動生成されない場合の例）
    result = ops.subtract(
        "Displacement2", "Displacement1", result_column="DisplacementDiff"
    ).end()
    print(f"DisplacementDiff = {result['DisplacementDiff'].values}")
    print()

    print("3. selectを使用して特定の列のみに演算を適用")
    # selectを使用して特定の列だけを選択してから数学演算を適用する例
    selected = ops.select(columns=["Force1", "Displacement1"]).end()
    selected_ops = selected.ops
    result = selected_ops.divide(
        "Force1",
        "Displacement1",
        result_column="Stiffness",
        handle_zero_division="none",
    ).end()
    print(
        f"選択した列のみで剛性計算: Force1/Displacement1 = {result['Stiffness'].values}"
    )
    print()

    print("4. select_stepを使用して特定のステップのみに演算を適用")
    # select_stepを使用して特定のステップだけに対して演算を適用する例
    step_selected = ops.select_step(
        steps=[3, 4, 5]
    ).end()  # ステップ3,4,5のデータのみを選択
    step_ops = step_selected.ops
    result = step_ops.multiply("Force1", 2, result_column="DoubleForce").end()
    print(f"選択したステップの荷重を2倍: Force1*2 = {result['DoubleForce'].values}")
    print()

    print("5. 数式の評価")
    # 数式文字列を評価して結果を計算（複合的な計算式）
    # 例: 剛性 k = F/(δ+0.001) の計算、0.001は0除算回避
    result = ops.evaluate(
        "(Force1+Force2)/(Displacement1+0.001)", result_column="Stiffness"
    ).end()
    print(f"剛性 k = (F1+F2)/(D1+0.001) = {result['Stiffness'].values}")
    print()

    print("6. 数学関数")
    # select操作で特定の列を選んでから数学関数を適用
    selected = ops.select(columns=["Displacement1", "Displacement2"]).end()
    selected_ops = selected.ops

    # 平方根
    result = selected_ops.sqrt("Displacement2", result_column="sqrt_disp").end()
    print(f"sqrt(Displacement2) = {result['sqrt_disp'].values}")

    # べき乗 - 別のselectを使用して単一の列で操作
    force_selected = ops.select(columns=["Force1"]).end()
    force_ops = force_selected.ops
    result = force_ops.pow("Force1", 2, result_column="Force1^2").end()
    print(f"Force1^2 = {result['Force1^2'].values}")

    # 指数
    result = selected_ops.exp("Displacement1", result_column="exp_disp").end()
    print(f"exp(Displacement1) = {result['exp_disp'].values}")
    print()

    print("7. 連鎖演算とselect_step")
    # 特定のステップだけを選択してから連鎖的に演算を適用
    valid_steps = [3, 4, 5]  # Noneを含まないステップ
    step_selected = ops.select_step(steps=valid_steps).end()
    step_ops = step_selected.ops

    # 選択したステップデータに対して連鎖的に演算を適用
    result = (
        step_ops.add("Force1", "Force2", result_column="TotalForce")
        .divide(
            "TotalForce", 2, result_column="AverageForce", handle_zero_division="none"
        )
        .sqrt("AverageForce", result_column="SqrtAvgForce")
        .divide(
            "Force1",
            "SqrtAvgForce",
            result_column="NormalizedForce1",
            handle_zero_division="none",
        )
        .end()
    )

    print("ステップを選択して連鎖演算を適用した結果:")
    print(f"  選択したステップ: {result.step.values}")
    print(f"  合計荷重: {result['TotalForce'].values}")
    print(f"  平均荷重: {result['AverageForce'].values}")
    print(f"  平均荷重の平方根: {result['SqrtAvgForce'].values}")
    print(f"  正規化荷重1: {result['NormalizedForce1'].values}")


if __name__ == "__main__":
    print("-- ColumnCollectionの数学演算操作 --\n")
    demonstrate_math_operations()
