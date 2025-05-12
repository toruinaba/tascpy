"""
異常値の検出・除去・可視化のサンプルコード

このサンプルでは、次の機能を紹介します：
1. 異常値を含むサンプルデータの生成
2. 移動平均の計算と可視化
3. 異常値の検出と可視化（新しい visualize_outliers 関数の使用）
4. 異常値の除去と効果の確認
5. 異なるパラメータによる効果の比較
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


def create_sample_data_with_outliers(
    size=200, outlier_ratio=0.05, base_value=0, amplitude=1
):
    """
    異常値を含むサンプルデータを生成します

    Args:
        size: データのサイズ
        outlier_ratio: 異常値の割合
        base_value: 基準値
        amplitude: 振幅

    Returns:
        異常値を含むデータ配列とその異常値のインデックス
    """
    # 通常値の生成（サイン波 + ノイズ）
    t = np.linspace(0, 6 * np.pi, size)
    normal_data = np.sin(t) * amplitude + base_value  # 基準値と振幅を調整可能
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
                amplitude + np.random.rand() * amplitude * 2
            )  # 上側の異常値
        else:
            data[idx] = normal_data[idx] - (
                amplitude + np.random.rand() * amplitude * 2
            )  # 下側の異常値

    # 一部にNone値（欠損値）を入れる
    none_indices = np.random.choice(size, int(size * 0.02), replace=False)
    for idx in none_indices:
        if idx not in outlier_indices:  # 異常値とNone値が重複しないようにする
            data[idx] = None

    return data.tolist(), outlier_indices


def analyze_data_distribution(data_list, title, with_outliers=True):
    """
    データの分布を分析して表示します

    Args:
        data_list: 分析対象のデータリスト
        title: グラフのタイトル
        with_outliers: 異常値を含むデータかどうかを示すフラグ
    """
    # None値とnp.nan値を除外して有効なデータのみ抽出
    valid_values = []
    for x in data_list:
        try:
            # None値のチェック
            if x is None:
                continue

            # NaNのチェック（数値化できない場合もスキップ）
            float_val = float(x)
            if np.isnan(float_val):
                continue

            valid_values.append(float_val)
        except (ValueError, TypeError):
            # 数値に変換できない値はスキップ
            continue

    if not valid_values:
        print(
            f"\n{title} {' （異常値あり）' if with_outliers else ' （異常値除去後）'} に有効なデータがありません"
        )
        return {"mean": 0, "std": 0, "min": 0, "max": 0, "range": 0}

    # 明示的に float型の配列に変換
    data = np.array(valid_values, dtype=float)

    # 基本統計量を計算
    mean = np.mean(data)
    std = np.std(data)
    min_val = np.min(data)
    max_val = np.max(data)
    data_range = max_val - min_val

    # 結果を表示
    status = "（異常値あり）" if with_outliers else "（異常値除去後）"
    print(f"\n{title} {status} の基本統計量:")
    print(f"- データ数: {len(data)}")
    print(f"- 平均値: {mean:.4f}")
    print(f"- 標準偏差: {std:.4f}")
    print(f"- 最小値: {min_val:.4f}")
    print(f"- 最大値: {max_val:.4f}")
    print(f"- 範囲（最大-最小）: {data_range:.4f}")

    return {
        "mean": mean,
        "std": std,
        "min": min_val,
        "max": max_val,
        "range": data_range,
    }


def main():
    """メイン処理"""
    print("異常値の検出・除去・可視化のサンプルコード")

    # === 1. サンプルデータの生成 ===
    print("\n1. サンプルデータの生成")
    np.random.seed(42)  # 再現性のために乱数シードを固定

    # 2つの異なるデータセットを生成
    size = 200
    # データセット1: 基準値0、振幅1の標準的なサイン波
    data1, true_outlier_indices1 = create_sample_data_with_outliers(
        size, outlier_ratio=0.05, base_value=0, amplitude=1
    )
    # データセット2: 基準値10、振幅2のサイン波
    data2, true_outlier_indices2 = create_sample_data_with_outliers(
        size, outlier_ratio=0.05, base_value=10, amplitude=2
    )

    # ステップ（インデックス）を作成
    steps = list(range(1, size + 1))

    # コレクションを作成
    collection1 = ColumnCollection(
        step=steps,
        columns={
            "data": Column("1", "標準データ", "", data1),
            "category": Column("2", "カテゴリ", "", ["A"] * size),
        },
        metadata={"description": "Sample data with outliers (standard)"},
    )

    collection2 = ColumnCollection(
        step=steps,
        columns={
            "data": Column("1", "スケール変更データ", "", data2),
            "category": Column("2", "カテゴリ", "", ["B"] * size),
        },
        metadata={"description": "Sample data with outliers (scaled)"},
    )

    # === 2. 移動平均の計算 ===
    print("\n2. 移動平均の計算")
    ops1 = CollectionOperations(collection1)
    ops2 = CollectionOperations(collection2)

    # 複数のウィンドウサイズで移動平均を計算（最初のデータセット）
    result1 = (
        ops1.moving_average(column="data", window_size=5, result_column="ma5")
        .moving_average(column="data", window_size=21, result_column="ma21")
        .end()
    )

    print(f"- データセット1の行数: {len(result1)}")
    print(f"- 移動平均(window=5)の最初の5件: {result1['ma5'].values[:5]}")
    print(f"- 移動平均(window=21)の最初の5件: {result1['ma21'].values[:5]}")

    # === 3. 異常値の検出と可視化（新機能：visualize_outliers） ===
    print("\n3. 異常値の検出と可視化")

    # visualize_outliers を使用した異常値の可視化（厳しいしきい値）
    plt.figure(figsize=(12, 10))
    plt.subplot(2, 1, 1)

    result_vis1 = ops1.visualize_outliers(
        column="data",
        window_size=15,
        threshold=0.3,  # 厳しいしきい値
        plot_type="line",
        highlight_color="red",
        outlier_marker="o",
        ax=plt.gca(),  # 現在のサブプロットに描画
        normal_alpha=0.7,
    ).end()

    # タイトルを明示的に設定（タイトル内に閾値を数値で表示）
    plt.title(f"標準データの異常値検出（厳しいしきい値: 0.3）")
    plt.xlabel("ステップ")
    plt.ylabel("データ値")

    # visualize_outliers を使用した異常値の可視化（緩いしきい値）
    plt.subplot(2, 1, 2)

    result_vis2 = ops1.visualize_outliers(
        column="data",
        window_size=15,
        threshold=0.7,  # 緩いしきい値
        plot_type="line",
        highlight_color="orange",
        outlier_marker="^",
        ax=plt.gca(),  # 現在のサブプロットに描画
        normal_alpha=0.7,
    ).end()

    # タイトルを明示的に設定
    plt.title(f"標準データの異常値検出（緩いしきい値: 0.7）")
    plt.xlabel("ステップ")
    plt.ylabel("データ値")

    plt.tight_layout()
    plt.savefig(os.path.join(IMGS_DIR, "outlier_visualization_comparison.png"))

    # 検出された異常値の数を計算
    strict_outlier_count = sum(result_vis1["_outlier_flags_data"].values)
    loose_outlier_count = sum(result_vis2["_outlier_flags_data"].values)
    true_outlier_count = len(true_outlier_indices1)

    print(f"- 実際の異常値の数: {true_outlier_count}")
    print(f"- 検出された異常値の数（厳しいしきい値）: {strict_outlier_count}")
    print(f"- 検出された異常値の数（緩いしきい値）: {loose_outlier_count}")

    # === 4. 異常値の除去と効果の確認 ===
    print("\n4. 異常値の除去と効果の確認")

    # 異常値を除去（データセット2を使用）
    result_with_removal = ops2.remove_outliers(
        column="data",
        window_size=15,
        threshold=0.3,
    ).end()

    # 除去後のデータ数を確認
    print(f"- 元データの行数: {len(collection2)}")
    print(f"- 異常値除去後の行数: {len(result_with_removal)}")
    print(f"- 除去されたデータの数: {len(collection2) - len(result_with_removal)}")

    # 異常値除去前後のデータ分布を比較
    stats_with_outliers = analyze_data_distribution(
        collection2["data"].values, "元データ", True
    )

    stats_without_outliers = analyze_data_distribution(
        result_with_removal["data"].values, "クリーニング後データ", False
    )

    # 除去前後の比較を可視化
    plt.figure(figsize=(12, 12))

    # プロット1: 元データと異常値除去後のデータの比較
    plt.subplot(2, 1, 1)

    # 元データ
    plt.plot(
        steps,
        collection2["data"].values,
        "o-",
        markersize=3,
        color="blue",
        alpha=0.6,
        label="Raw Data with Outliers",
    )

    # 異常値を除去したデータ
    cleaned_steps = result_with_removal.step
    plt.plot(
        cleaned_steps,
        result_with_removal["data"].values,
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

    # プロット2: ヒストグラム比較
    plt.subplot(2, 1, 2)

    # 異常値を含むデータのヒストグラム
    plt.hist(
        [x for x in collection2["data"].values if x is not None],
        bins=20,
        alpha=0.5,
        label="With Outliers",
        color="blue",
    )

    # 異常値を除去したデータのヒストグラム
    plt.hist(
        [x for x in result_with_removal["data"].values if x is not None],
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

    # === 5. エッジ処理と様々なパラメータの比較 ===
    print("\n5. エッジ処理と様々なパラメータの比較")

    # データセット2のサブセットを作成（特定範囲の抽出）
    subset = ops2.search_by_step_range(50, 100).end()
    subset_ops = CollectionOperations(subset)

    # サブセットでの異常値可視化の比較（異なるエッジ処理）
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))

    # 対称エッジ処理を使用
    result_symmetric = subset_ops.visualize_outliers(
        column="data",
        window_size=7,
        threshold=0.3,
        edge_handling="symmetric",
        highlight_color="red",
        ax=ax1,
        normal_color="blue",
        plot_type="scatter",
    ).end()

    # 対称エッジ処理のグラフにラベルとタイトルを明示的に設定
    sym_outlier_count = sum(result_symmetric["_outlier_flags_data"].values)
    ax1.set_title(
        f"異常値検出 - 対称エッジ処理（検出数: {sym_outlier_count}個）", fontsize=12
    )
    ax1.set_xlabel("ステップ", fontsize=10)
    ax1.set_ylabel("データ値", fontsize=10)

    # 非対称エッジ処理を使用
    result_asymmetric = subset_ops.visualize_outliers(
        column="data",
        window_size=7,
        threshold=0.3,
        edge_handling="asymmetric",
        highlight_color="magenta",
        ax=ax2,
        normal_color="cyan",
        plot_type="scatter",
    ).end()

    # 非対称エッジ処理のグラフにラベルとタイトルを明示的に設定
    asym_outlier_count = sum(result_asymmetric["_outlier_flags_data"].values)
    ax2.set_title(
        f"異常値検出 - 非対称エッジ処理（検出数: {asym_outlier_count}個）", fontsize=12
    )
    ax2.set_xlabel("ステップ", fontsize=10)
    ax2.set_ylabel("データ値", fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(IMGS_DIR, "edge_handling_outlier_comparison.png"))

    # === 6. クリーニング後のデータ分析 ===
    print("\n6. クリーニング後のデータ分析")

    # 移動平均を適用して滑らかなトレンドを確認
    cleaned_result = (
        CollectionOperations(result_with_removal)
        .moving_average(column="data", window_size=5, result_column="smoothed_data")
        .end()
    )

    # トレンド可視化
    plt.figure(figsize=(12, 6))
    plt.plot(
        cleaned_result.step,
        cleaned_result["data"].values,
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
    print(f"- outlier_visualization_comparison.png")
    print(f"- outlier_removal_effect.png")
    print(f"- edge_handling_outlier_comparison.png")
    print(f"- cleaned_data_trend.png")


if __name__ == "__main__":
    main()
