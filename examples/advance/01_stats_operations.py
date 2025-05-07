"""
移動平均と異常値検出のサンプルコード

このサンプルでは、次の機能を紹介します：
1. 移動平均の計算と可視化
2. 異常値検出の実行と可視化
3. 異なるパラメータによる効果の比較
"""

import numpy as np
import matplotlib.pyplot as plt
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
from tascpy.operations.proxy import CollectionOperations


def create_sample_data_with_outliers(size=200, outlier_ratio=0.05):
    """
    異常値を含むサンプルデータを生成します

    Args:
        size: データのサイズ
        outlier_ratio: 異常値の割合

    Returns:
        異常値を含むデータ配列
    """
    # 通常値の生成（サイン波 + ノイズ）
    t = np.linspace(0, 6 * np.pi, size)
    normal_data = np.sin(t) + 0.1 * np.random.randn(size)

    # 異常値の位置をランダムに決定
    outlier_count = int(size * outlier_ratio)
    outlier_indices = np.random.choice(size, outlier_count, replace=False)

    # 異常値を生成（通常値から大きく離れた値）
    data = normal_data.copy()
    for idx in outlier_indices:
        data[idx] = normal_data[idx] + (
            np.random.choice([-1, 1]) * (1.0 + np.random.rand())
        )

    # 一部にNone値（欠損値）を入れる
    none_indices = np.random.choice(size, int(size * 0.02), replace=False)
    for idx in none_indices:
        if idx not in outlier_indices:  # 異常値とNone値が重複しないようにする
            data[idx] = None

    return data, outlier_indices


def main():
    """メイン処理"""
    print("移動平均と異常値検出のサンプルコード")

    # サンプルデータの生成
    np.random.seed(42)  # 再現性のために乱数シードを固定
    size = 200
    data, true_outlier_indices = create_sample_data_with_outliers(size, 0.05)

    # ステップ（インデックス）を作成
    steps = list(range(1, size + 1))

    # コレクションを作成
    collection = ColumnCollection(
        step=steps,
        columns={
            "raw_data": Column("1", "Raw Data", "", data),
        },
        metadata={"description": "Sample data with outliers"},
    )

    # CollectionOperationsを使って操作する
    ops = CollectionOperations(collection)

    # === すべての操作を一つのチェーンで実行 ===
    print("\n1. 異なるウィンドウサイズでの移動平均の計算と異常値検出")

    # 移動平均と異常値検出を一連のチェーンで実行
    result = (
        ops.moving_average(column="raw_data", window_size=5, result_column="ma5")
        .moving_average(column="raw_data", window_size=21, result_column="ma21")
        .detect_outliers(
            column="raw_data",
            window_size=15,
            threshold=0.3,  # 厳しい閾値
            result_column="outliers_strict",
        )
        .detect_outliers(
            column="raw_data",
            window_size=15,
            threshold=0.7,  # 緩い閾値
            result_column="outliers_loose",
        )
        .end()
    )

    # 結果の表示
    print(f"- 元データの行数: {len(result)}")
    print(f"- 移動平均(window=5)の最初の5件: {result['ma5'].values[:5]}")
    print(f"- 移動平均(window=21)の最初の5件: {result['ma21'].values[:5]}")

    # 異常値の数を計算
    strict_count = sum(result["outliers_strict"].values)
    loose_count = sum(result["outliers_loose"].values)
    true_count = len(true_outlier_indices)

    print("\n2. 異常値検出結果")
    print(f"- 実際の異常値の数: {true_count}")
    print(f"- 検出された異常値の数（厳しい閾値）: {strict_count}")
    print(f"- 検出された異常値の数（緩い閾値）: {loose_count}")

    # === 結果の可視化 ===
    # 1. 移動平均の可視化
    plt.figure(figsize=(12, 10))

    # プロット1: 移動平均
    plt.subplot(2, 1, 1)
    plt.plot(steps, result["raw_data"].values, "o-", markersize=3, label="Raw Data")
    plt.plot(steps, result["ma5"].values, label="Moving Avg (window=5)")
    plt.plot(steps, result["ma21"].values, label="Moving Avg (window=21)")
    plt.legend()
    plt.title("Moving Average Calculation")
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.grid(True, alpha=0.3)

    # プロット2: 異常値検出
    plt.subplot(2, 1, 2)

    # 原データをプロット
    plt.plot(
        steps,
        result["raw_data"].values,
        "o-",
        markersize=3,
        color="blue",
        alpha=0.5,
        label="Raw Data",
    )

    # 厳しい閾値で検出した異常値
    strict_outlier_indices = [
        i for i, val in enumerate(result["outliers_strict"].values) if val == 1
    ]
    strict_values = [result["raw_data"].values[i] for i in strict_outlier_indices]
    plt.scatter(
        [steps[i] for i in strict_outlier_indices],
        strict_values,
        color="red",
        s=80,
        marker="o",
        label="Detected (strict)",
    )

    # 緩い閾値でのみ検出した異常値
    loose_only_indices = [
        i
        for i, (strict, loose) in enumerate(
            zip(result["outliers_strict"].values, result["outliers_loose"].values)
        )
        if loose == 1 and strict == 0
    ]
    loose_only_values = [result["raw_data"].values[i] for i in loose_only_indices]
    if loose_only_indices:  # リストが空でない場合のみプロット
        plt.scatter(
            [steps[i] for i in loose_only_indices],
            loose_only_values,
            color="orange",
            s=80,
            marker="^",
            label="Detected (loose only)",
        )

    # 真の異常値（検出できなかったもの含む）
    plt.scatter(
        [steps[i] for i in true_outlier_indices],
        [result["raw_data"].values[i] for i in true_outlier_indices],
        facecolors="none",
        edgecolors="green",
        s=120,
        linewidths=2,
        label="True Outliers",
    )

    plt.title("Outlier Detection")
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("stats_operations_result.png")  # 画像として保存
    plt.show()

    # === 追加: 特定範囲のデータで検証 ===
    print("\n3. データサブセットでの検証")

    # データの一部分を抽出（search_by_step_rangeを使用）
    subset = ops.search_by_step_range(50, 100).end()
    subset_ops = CollectionOperations(subset)

    # 異なるエッジ処理方法の比較
    subset_result = (
        subset_ops.moving_average(
            column="raw_data",
            window_size=7,
            edge_handling="symmetric",
            result_column="ma7_symmetric",
        )
        .moving_average(
            column="raw_data",
            window_size=7,
            edge_handling="asymmetric",
            result_column="ma7_asymmetric",
        )
        .end()
    )

    print(f"- サブセットデータの行数: {len(subset_result)}")
    print(f"- 対称エッジ処理の最初の値: {subset_result['ma7_symmetric'].values[0]}")
    print(f"- 非対称エッジ処理の最初の値: {subset_result['ma7_asymmetric'].values[0]}")

    # サブセットデータの可視化
    plt.figure(figsize=(12, 6))
    plt.plot(
        subset_result.step,
        subset_result["raw_data"].values,
        "o-",
        markersize=4,
        color="blue",
        alpha=0.5,
        label="Raw Data",
    )
    plt.plot(
        subset_result.step,
        subset_result["ma7_symmetric"].values,
        "r-",
        linewidth=2,
        label="Moving Avg (symmetric)",
    )
    plt.plot(
        subset_result.step,
        subset_result["ma7_asymmetric"].values,
        "g--",
        linewidth=2,
        label="Moving Avg (asymmetric)",
    )

    plt.title("Edge Handling Comparison")
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("edge_handling_comparison.png")  # 画像として保存
    plt.show()


if __name__ == "__main__":
    main()
