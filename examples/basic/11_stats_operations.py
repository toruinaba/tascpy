"""
NumberColumnの基本統計量を取得する方法を示すサンプルコード

このサンプルではtascpyライブラリのNumberColumnクラスに実装された
統計関数（max, min, mean, median, std, sum, variance, quantile）を
使用してデータの分析を行う方法を示します。
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import NumberColumn

# 現在のスクリプトからの相対パスでデータファイルを取得
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_CSV_PATH = os.path.join(DATA_DIR, "load_displacement_sample.csv")

print("-- NumberColumnの統計関数の使用例 --\n")

# ----------------------------------------------------
# データの準備
# ----------------------------------------------------

# CSVファイルからデータを読み込む
try:
    collection = ColumnCollection.from_file(
        filepath=SAMPLE_CSV_PATH, format_name="csv", auto_detect_types=True
    )
except FileNotFoundError:
    # サンプルデータが存在しない場合はダミーデータを作成
    print("サンプルデータが見つかりません。ダミーデータを生成します。")

    # ダミーデータの生成
    steps = list(range(1, 101))

    # 正規分布のノイズを含むデータ作成
    np.random.seed(42)  # 再現性のため
    load_data = np.linspace(0, 100, 100) + np.random.normal(0, 5, 100)
    disp_data = np.linspace(0, 20, 100) + np.random.normal(0, 1, 100)

    # 一部にNone値を含めて実際のデータに近づける
    load_data[10:15] = None
    disp_data[80:85] = None

    # ColumnCollectionの作成
    collection = ColumnCollection(
        step=steps,
        columns={
            "Load": NumberColumn(None, "Load", "N", load_data.tolist()),
            "Displacement": NumberColumn(
                None, "Displacement", "mm", disp_data.tolist()
            ),
        },
        metadata={"description": "基本統計量サンプル"},
        auto_detect_types=True,
    )

# データの簡単な確認
print(f"列名: {list(collection.columns.keys())}")
print(f"行数: {len(collection)}")
print()

# ----------------------------------------------------
# 基本統計量の計算
# ----------------------------------------------------

print("1. 基本的な統計量の取得")
print("-----------------------")

# サンプルデータから最初の数値列を取得
column_names = list(collection.columns.keys())
numeric_columns = [
    name for name, col in collection.columns.items() if isinstance(col, NumberColumn)
]

if not numeric_columns:
    print("数値型の列が見つかりません。処理を中止します。")
    exit()

# 使用する列名
load_column_name = numeric_columns[0]
print(f"使用する列名: {load_column_name}")

# Load列を取得（NumberColumnオブジェクト）
load_column = collection[load_column_name]

# 各種統計量を計算
max_value = load_column.max()
min_value = load_column.min()
mean_value = load_column.mean()
median_value = load_column.median()
std_value = load_column.std()
sum_value = load_column.sum()
variance_value = load_column.variance()

# 結果を表示
print(f"最大値 (max): {max_value:.2f}")
print(f"最小値 (min): {min_value:.2f}")
print(f"平均値 (mean): {mean_value:.2f}")
print(f"中央値 (median): {median_value:.2f}")
print(f"標準偏差 (std): {std_value:.2f}")
print(f"合計 (sum): {sum_value:.2f}")
print(f"分散 (variance): {variance_value:.2f}")
print()

# ----------------------------------------------------
# パーセンタイル値の計算
# ----------------------------------------------------

print("2. パーセンタイル値の計算")
print("------------------------")

# 様々なパーセンタイルを計算
q_values = [0, 0.25, 0.5, 0.75, 1.0]
for q in q_values:
    q_value = load_column.quantile(q)
    print(f"{int(q*100)}パーセンタイル: {q_value:.2f}")
print()

# ----------------------------------------------------
# None値の扱いの確認
# ----------------------------------------------------

print("3. None値の扱いの確認")
print("--------------------")

# None値の確認
none_count = load_column.count_nones()
none_indices = load_column.none_indices()
has_none = load_column.has_none()

print(f"None値の数: {none_count}")
print(f"None値の位置: {none_indices}")
print(f"None値を含むか: {has_none}")
print()

# ----------------------------------------------------
# 複数列の統計比較
# ----------------------------------------------------

print("4. 複数列の統計比較")
print("------------------")

# 各列の統計量を取得
stats_comparison = {}
for col_name, column in collection.columns.items():
    if isinstance(column, NumberColumn):
        stats_comparison[col_name] = {
            "max": column.max(),
            "min": column.min(),
            "mean": column.mean(),
            "median": column.median(),
            "std": column.std(),
        }

# 結果を表形式で表示
for col_name, stats in stats_comparison.items():
    print(f"列名: {col_name}")
    for stat_name, value in stats.items():
        print(f"  {stat_name}: {value:.2f}")
    print()

# ----------------------------------------------------
# メソッドチェーンでの操作と統計
# ----------------------------------------------------

print("5. メソッドチェーンでの操作と統計")
print("------------------------------")

try:
    # 処理前の統計情報を表示
    print(f"クリーニング前の{load_column_name}列のデータ数: {len(collection)}")
    pre_mean = collection[load_column_name].mean()
    pre_std = collection[load_column_name].std()
    print(f"クリーニング前の{load_column_name}列の平均値: {pre_mean:.2f}")
    print(f"クリーニング前の{load_column_name}列の標準偏差: {pre_std:.2f}")

    # サンプルデータに依存しないより基本的なデモ
    # この例では、平均から離れたデータポイントを除外する
    mean_value = collection[load_column_name].mean()
    std_value = collection[load_column_name].std()

    # 平均値から1標準偏差以上離れたデータを除外するカスタム関数
    def is_within_std_range(row):
        val = row.get(load_column_name)  # 行データから値を取得
        if val is None:
            return False
        # 平均±1標準偏差の範囲内にあるかチェック
        return abs(val - mean_value) <= std_value

    # search_by_conditionを使用して値をフィルタリング
    result = collection.ops.search_by_condition(is_within_std_range).end()

    # 処理後の統計情報を表示
    if len(result) > 0:
        print(f"平均±標準偏差でフィルタリング後のデータ数: {len(result)}")
        if load_column_name in result.columns:
            post_mean = result[load_column_name].mean()
            post_std = result[load_column_name].std()

            if post_mean is not None and post_std is not None:
                print(
                    f"フィルタリング後の{load_column_name}列の平均値: {post_mean:.2f}"
                )
                print(
                    f"フィルタリング後の{load_column_name}列の標準偏差: {post_std:.2f}"
                )
                print(f"平均値の変化: {post_mean - pre_mean:.2f}")
                print(f"標準偏差の変化: {post_std - pre_std:.2f}")
            else:
                print("フィルタリング後の統計値を計算できません")
        else:
            print(f"フィルタリング後に列 {load_column_name} が見つかりません")
    else:
        print("フィルタリング後にデータが残りませんでした")
except Exception as e:
    import traceback

    print(f"データ処理中にエラーが発生しました: {e}")
    print(traceback.format_exc())
print()

# ----------------------------------------------------
# データの可視化と統計
# ----------------------------------------------------

print("6. データの可視化と統計")
print("---------------------")

try:
    # 可視化の準備
    plt.figure(figsize=(12, 7))

    # 元データをプロット
    valid_indices = [
        i for i, v in enumerate(collection[load_column_name].values) if v is not None
    ]
    valid_steps = [collection.step.values[i] for i in valid_indices]
    valid_loads = [collection[load_column_name].values[i] for i in valid_indices]

    plt.plot(valid_steps, valid_loads, "o-", alpha=0.5, label="元データ", color="blue")

    # フィルタリングしたデータをプロット (前のセクションで作成した result を使用)
    if "result" in locals() and len(result) > 0:
        filtered_indices = [
            i for i, v in enumerate(result[load_column_name].values) if v is not None
        ]
        filtered_steps = [result.step.values[i] for i in filtered_indices]
        filtered_loads = [result[load_column_name].values[i] for i in filtered_indices]

        plt.plot(
            filtered_steps,
            filtered_loads,
            "x",
            alpha=0.8,
            label="フィルタリング後のデータ",
            color="red",
            markersize=10,
        )

    # 統計情報の表示
    # 元データの統計ライン
    plt.axhline(
        y=collection[load_column_name].mean(),
        color="blue",
        linestyle="-",
        alpha=0.7,
        label=f"元データ平均値: {collection[load_column_name].mean():.2f}",
    )

    # 標準偏差の範囲を表示
    plt.axhline(
        y=collection[load_column_name].mean() + collection[load_column_name].std(),
        color="blue",
        linestyle="--",
        alpha=0.5,
    )
    plt.axhline(
        y=collection[load_column_name].mean() - collection[load_column_name].std(),
        color="blue",
        linestyle="--",
        alpha=0.5,
        label=f"元データ平均値±標準偏差: {collection[load_column_name].std():.2f}",
    )

    # フィルタリング後の統計ライン
    if "result" in locals() and len(result) > 0:
        if result[load_column_name].mean() is not None:
            plt.axhline(
                y=result[load_column_name].mean(),
                color="red",
                linestyle="-",
                alpha=0.7,
                label=f"フィルタリング後平均値: {result[load_column_name].mean():.2f}",
            )

            # 標準偏差の範囲を表示
            plt.axhline(
                y=result[load_column_name].mean() + result[load_column_name].std(),
                color="red",
                linestyle="--",
                alpha=0.5,
            )
            plt.axhline(
                y=result[load_column_name].mean() - result[load_column_name].std(),
                color="red",
                linestyle="--",
                alpha=0.5,
                label=f"フィルタリング後平均値±標準偏差: {result[load_column_name].std():.2f}",
            )

    # グラフの設定
    plt.title(f"{load_column_name}データの統計分析 - フィルタリング前後の比較")
    plt.xlabel("ステップ")
    plt.ylabel(f"{load_column_name}値")
    plt.grid(True, alpha=0.3)
    plt.legend()

    # グラフの表示
    plt.tight_layout()
    # plt.show()  # コメントアウトしてターミナル出力を確認
    plt.savefig(os.path.join(os.path.dirname(__file__), "imgs", "stats_example.png"))
    print("グラフを画像ファイルとして保存しました")

except Exception as e:
    print(f"グラフ作成中にエラーが発生しました: {e}")
