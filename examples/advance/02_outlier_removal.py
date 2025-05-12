"""
異常値除去のサンプルコード

このサンプルでは、次の機能を紹介します：
1. 異常値を含むサンプルデータの生成
2. 異常値の検出と可視化
3. 異常値の除去と効果の確認
4. クリーニング後のデータ分析と可視化
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
from tascpy.operations.proxy import CollectionOperations

# 出力画像用のディレクトリパスを設定
IMGS_DIR = os.path.join(os.path.dirname(__file__), "imgs")
os.makedirs(IMGS_DIR, exist_ok=True)


def create_sample_data_with_outliers(size=200, outlier_ratio=0.05):
    """
    異常値を含むサンプルデータを生成します

    Args:
        size: データのサイズ
        outlier_ratio: 異常値の割合

    Returns:
        異常値を含むデータ配列とその異常値のインデックス
    """
    # 通常値の生成（サイン波 + ノイズ）
    t = np.linspace(0, 6 * np.pi, size)
    normal_data = np.sin(t) * 2 + 10  # 基準値を10として振幅2のサイン波
    normal_data += 0.1 * np.random.randn(size)  # 小さなノイズを追加

    # 異常値の位置をランダムに決定
    outlier_count = int(size * outlier_ratio)
    outlier_indices = np.random.choice(size, outlier_count, replace=False)

    # 異常値を生成（通常値から大きく離れた値）
    data = normal_data.copy()
    for idx in outlier_indices:
        # 通常値よりも大きく（または小さく）なるように異常値を生成
        if np.random.random() > 0.5:
            data[idx] = normal_data[idx] + (
                2.0 + np.random.rand() * 3.0
            )  # 上側の異常値
        else:
            data[idx] = normal_data[idx] - (
                2.0 + np.random.rand() * 3.0
            )  # 下側の異常値

    return data.tolist(), outlier_indices.tolist()


def analyze_data_distribution(data_list, title, with_outliers=True):
    """
    データの分布を分析して表示します

    Args:
        data_list: 分析対象のデータリスト
        title: グラフのタイトル
        with_outliers: 異常値を含むデータかどうかを示すフラグ
    """
    # None値を除外してnumpy配列に変換
    data = np.array([x for x in data_list if x is not None])

    # 基本統計量を計算
    mean = np.mean(data)
    std = np.std(data)
    min_val = np.min(data)
    max_val = np.max(data)

    # 結果を表示
    status = "（異常値あり）" if with_outliers else "（異常値除去後）"
    print(f"\n{title} {status} の基本統計量:")
    print(f"- データ数: {len(data)}")
    print(f"- 平均値: {mean:.4f}")
    print(f"- 標準偏差: {std:.4f}")
    print(f"- 最小値: {min_val:.4f}")
    print(f"- 最大値: {max_val:.4f}")
    print(f"- 範囲（最大-最小）: {max_val - min_val:.4f}")

    return {
        "mean": mean,
        "std": std,
        "min": min_val,
        "max": max_val,
        "range": max_val - min_val,
    }


def main():
    """メイン処理"""
    print("異常値除去のサンプルコード")

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

    # === 1. 異常値の検出 ===
    print("\n1. 異常値の検出")

    # 異常値を検出する
    result_with_detection = ops.detect_outliers(
        column="raw_data",
        window_size=15,
        threshold=0.3,
        result_column="outlier_flags",
    ).end()

    # 異常値と認識されたデータポイントの数
    detected_count = sum(result_with_detection["outlier_flags"].values)
    print(f"- 検出された異常値の数: {detected_count}")
    print(f"- 実際の異常値の数: {len(true_outlier_indices)}")

    # 異常値のインデックス
    detected_indices = [
        i
        for i, flag in enumerate(result_with_detection["outlier_flags"].values)
        if flag == 1
    ]

    # 真の異常値と検出された異常値の比較
    true_positive = set(true_outlier_indices).intersection(set(detected_indices))
    false_negative = set(true_outlier_indices) - set(detected_indices)
    false_positive = set(detected_indices) - set(true_outlier_indices)

    print(f"- 正しく検出された異常値: {len(true_positive)}個")
    print(f"- 検出されなかった異常値: {len(false_negative)}個")
    print(f"- 誤って異常値と判定されたデータ: {len(false_positive)}個")

    # === 2. 異常値の除去 ===
    print("\n2. 異常値の除去")

    # 異常値を除去する
    result_with_removal = ops.remove_outliers(
        column="raw_data",
        window_size=15,
        threshold=0.3,
    ).end()

    # 除去後のデータ数を確認
    print(f"- 元データの行数: {len(collection)}")
    print(f"- 異常値除去後の行数: {len(result_with_removal)}")
    print(f"- 除去されたデータの数: {len(collection) - len(result_with_removal)}")

    # === 3. データ分布の比較分析 ===
    # 異常値を含むデータの基本統計量
    stats_with_outliers = analyze_data_distribution(
        collection["raw_data"].values, "元データ", True
    )

    # 異常値を除去したデータの基本統計量
    stats_without_outliers = analyze_data_distribution(
        result_with_removal["raw_data"].values, "クリーニング後データ", False
    )

    # === 4. データの可視化 ===
    print("\n4. 可視化結果の保存")

    plt.figure(figsize=(12, 15))

    # プロット1: 異常値の検出結果
    plt.subplot(3, 1, 1)
    plt.plot(
        steps,
        result_with_detection["raw_data"].values,
        "o-",
        markersize=3,
        color="blue",
        alpha=0.6,
        label="Raw Data",
    )

    # 検出された異常値のプロット
    detected_x = [steps[i] for i in detected_indices]
    detected_y = [result_with_detection["raw_data"].values[i] for i in detected_indices]
    plt.scatter(
        detected_x, detected_y, color="red", s=80, marker="o", label="Detected Outliers"
    )

    # 実際の異常値（検出できなかったものを含む）
    true_x = [steps[i] for i in true_outlier_indices]
    true_y = [result_with_detection["raw_data"].values[i] for i in true_outlier_indices]
    plt.scatter(
        true_x,
        true_y,
        facecolors="none",
        edgecolors="green",
        s=120,
        linewidths=2,
        label="True Outliers",
    )

    plt.title("異常値の検出")
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True, alpha=0.3)

    # プロット2: 元データと異常値除去後のデータの比較
    plt.subplot(3, 1, 2)

    # 元データ
    plt.plot(
        steps,
        collection["raw_data"].values,
        "o-",
        markersize=3,
        color="blue",
        alpha=0.6,
        label="Raw Data with Outliers",
    )

    # 異常値を除去したデータ
    # インデックスが元のデータと異なるため、新しいx軸を作成
    cleaned_steps = result_with_removal.step
    plt.plot(
        cleaned_steps,
        result_with_removal["raw_data"].values,
        "o-",
        markersize=4,
        color="green",
        alpha=0.7,
        label="Data after Outlier Removal",
    )

    plt.title("異常値除去の効果")
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True, alpha=0.3)

    # プロット3: ヒストグラム比較
    plt.subplot(3, 1, 3)

    # 異常値を含むデータのヒストグラム
    plt.hist(
        [x for x in collection["raw_data"].values if x is not None],
        bins=20,
        alpha=0.5,
        label="With Outliers",
        color="blue",
    )

    # 異常値を除去したデータのヒストグラム
    plt.hist(
        [x for x in result_with_removal["raw_data"].values if x is not None],
        bins=20,
        alpha=0.5,
        label="Without Outliers",
        color="green",
    )

    # 平均値のマーカー
    plt.axvline(
        stats_with_outliers["mean"],
        color="blue",
        linestyle="dashed",
        linewidth=2,
        label="Mean (with outliers)",
    )
    plt.axvline(
        stats_without_outliers["mean"],
        color="green",
        linestyle="dashed",
        linewidth=2,
        label="Mean (without outliers)",
    )

    plt.title("データ分布の比較")
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(IMGS_DIR, "outlier_removal_effect.png"))

    # === 5. データクリーニング後の分析 ===
    print("\n5. クリーニング後のデータ分析")

    # 移動平均を適用して滑らかなトレンドを確認
    cleaned_result = (
        CollectionOperations(result_with_removal)
        .moving_average(column="raw_data", window_size=5, result_column="smoothed_data")
        .end()
    )

    # トレンド可視化
    plt.figure(figsize=(12, 6))
    plt.plot(
        cleaned_result.step,
        cleaned_result["raw_data"].values,
        "o-",
        markersize=3,
        alpha=0.6,
        color="blue",
        label="Cleaned Data",
    )
    plt.plot(
        cleaned_result.step,
        cleaned_result["smoothed_data"].values,
        linewidth=2,
        color="red",
        label="Trend (Moving Average)",
    )

    plt.title("クリーニング後データのトレンド分析")
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(IMGS_DIR, "cleaned_data_trend.png"))

    print(f"\n画像ファイルを保存しました。")
    print(f"保存先: {IMGS_DIR}")
    print(f"- outlier_removal_effect.png")
    print(f"- cleaned_data_trend.png")


if __name__ == "__main__":
    main()
