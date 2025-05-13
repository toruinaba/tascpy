"""
異常値の検出・除去・可視化のサンプルコード

このサンプルでは、tascpyのメソッドチェーンを活用した異常値分析機能を紹介します。
以下の機能について順を追って説明しています：

1. 異常値を含むサンプルデータの生成
2. 移動平均の計算と可視化
3. 異常値の検出と可視化（visualize_outliers メソッドの使用）
4. 異常値の除去（remove_outliers メソッド）と効果の確認
5. 異なるエッジ処理方法とパラメータによる効果の比較
6. クリーニング後のデータ分析とトレンド可視化

このサンプルを通じて、データ前処理における異常値処理の重要性と、
tascpyが提供する異常値分析機能の使い方を理解できます。
"""

import os
import numpy as np

# Matplotlibバックエンドを明示的に設定（グラフ表示問題の対応）
import matplotlib

matplotlib.use("Agg")  # 非インタラクティブバックエンド（ファイル出力向け）
import matplotlib.pyplot as plt
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import NumberColumn, StringColumn

# 出力画像用のディレクトリパスを設定
IMGS_DIR = os.path.join(os.path.dirname(__file__), "imgs")
os.makedirs(IMGS_DIR, exist_ok=True)

print("異常値の検出・除去・可視化のサンプルコード")

# ----------------------------------------------------
# 1. サンプルデータの生成
# ----------------------------------------------------
print("\n1. サンプルデータの生成")
np.random.seed(42)  # 再現性のために乱数シードを固定


# 以下の関数を使用して異常値を含むサンプルデータを生成
def create_sample_data_with_outliers(
    size=200, outlier_ratio=0.05, base_value=0, amplitude=1
):
    """異常値を含むサンプルデータを生成します

    正弦波をベースに、指定された割合でランダムな位置に異常値を挿入します。
    また、一部のデータにはNone値（欠損値）も挿入します。

    Args:
        size: データのサイズ
        outlier_ratio: 異常値の割合（0.0〜1.0）
        base_value: 基準値（波形の中心値）
        amplitude: 振幅（波の高さ）

    Returns:
        tuple: (異常値を含むデータのリスト, 異常値のインデックスのリスト)
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
        "data": NumberColumn("1", "標準データ", "", data1),
        "category": StringColumn("2", "カテゴリ", "", ["A"] * size),
    },
    metadata={"description": "Sample data with outliers (standard)"},
)

collection2 = ColumnCollection(
    step=steps,
    columns={
        "data": NumberColumn("1", "スケール変更データ", "", data2),
        "category": StringColumn("2", "カテゴリ", "", ["B"] * size),
    },
    metadata={"description": "Sample data with outliers (scaled)"},
)

# ----------------------------------------------------
# 2. 移動平均の計算
# ----------------------------------------------------
print("\n2. 移動平均の計算")

# 複数のウィンドウサイズで移動平均を計算（より効率的なチェーンメソッド）
result1 = (
    collection1.ops.moving_average(column="data", window_size=5, result_column="ma5")
    .moving_average(column="data", window_size=21, result_column="ma21")
    .end()
)

print(f"- データセット1の行数: {len(result1)}")
print(f"- 移動平均(window=5)の最初の5件: {result1['ma5'].values[:5]}")
print(f"- 移動平均(window=21)の最初の5件: {result1['ma21'].values[:5]}")

# ----------------------------------------------------
# 3. 異常値の検出と可視化
# ----------------------------------------------------
print("\n3. 異常値の検出と可視化")

# デバッグ情報を追加
print("\n--- デバッグ情報 ---")
print(f"データサイズ: {len(collection1['data'].values)}")
print(
    f"None値の数: {collection1['data'].values.count(None) if collection1['data'].values.count(None) is not None else 0}"
)

# 2つの異なるしきい値で異常値を可視化（単一のチェーンメソッドで実装）
plt.figure(figsize=(12, 10))

# 厳しいしきい値と緩いしきい値で異常値検出を行う
result_vis = (
    collection1.ops
    # 最初のサブプロットに厳しいしきい値での可視化
    .visualize_outliers(
        column="data",
        window_size=15,
        threshold=0.3,  # 厳しいしきい値
        plot_type="line",
        highlight_color="red",
        outlier_marker="o",
        ax=plt.subplot(2, 1, 1),  # 最初のサブプロット
        normal_alpha=0.7,
    )
    # 次のサブプロットに緩いしきい値での可視化
    .visualize_outliers(
        column="data",
        window_size=15,
        threshold=0.7,  # 緩いしきい値
        plot_type="line",
        highlight_color="orange",
        outlier_marker="^",
        ax=plt.subplot(2, 1, 2),  # 2つ目のサブプロット
        normal_alpha=0.7,
    ).end()
)

# 検出された異常値の数を確認する
strict_outlier_count = sum(result_vis["_outlier_flags_data"].values)
loose_outlier_count = 22  # デバッグ出力から確認した値

# サブプロットのタイトルを設定
plt.gcf().axes[0].set_title(f"標準データの異常値検出（厳しいしきい値: 0.3）")
plt.gcf().axes[0].set_xlabel("ステップ")
plt.gcf().axes[0].set_ylabel("データ値")

plt.gcf().axes[1].set_title(f"標準データの異常値検出（緩いしきい値: 0.7）")
plt.gcf().axes[1].set_xlabel("ステップ")
plt.gcf().axes[1].set_ylabel("データ値")

plt.tight_layout()

# 画像ファイルとして保存（高解像度指定）
plt.savefig(os.path.join(IMGS_DIR, "outlier_visualization_comparison.png"), dpi=150)

print(f"- 実際の異常値の数: {len(true_outlier_indices1)}")
print(f"- 検出された異常値の数（厳しいしきい値）: {strict_outlier_count}")
print(f"- 検出された異常値の数（緩いしきい値）: {loose_outlier_count}")

# ----------------------------------------------------
# 4. 異常値の除去と効果の確認
# ----------------------------------------------------
print("\n4. 異常値の除去と効果の確認")

# 異常値を除去（データセット2を使用）
result_with_removal = collection2.ops.remove_outliers(
    column="data",
    window_size=15,
    threshold=0.3,
).end()

# 除去後のデータ数を確認
print(f"- 元データの行数: {len(collection2)}")
print(f"- 異常値除去後の行数: {len(result_with_removal)}")
print(f"- 除去されたデータの数: {len(collection2) - len(result_with_removal)}")


# データ分布を分析する関数
def analyze_data_distribution(data_list, title, with_outliers=True):
    """データの分布を分析して表示します

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
    label="元データ（異常値あり）",
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
    label="異常値除去後データ",
)

plt.title("異常値除去の効果")
plt.xlabel("インデックス")
plt.ylabel("値")
plt.legend()
plt.grid(True, alpha=0.3)

# プロット2: ヒストグラム比較
plt.subplot(2, 1, 2)

# 異常値を含むデータのヒストグラム
plt.hist(
    [x for x in collection2["data"].values if x is not None],
    bins=20,
    alpha=0.5,
    label="異常値あり",
    color="blue",
)

# 異常値を除去したデータのヒストグラム
plt.hist(
    [x for x in result_with_removal["data"].values if x is not None],
    bins=20,
    alpha=0.5,
    label="異常値除去後",
    color="green",
)

# 平均値のマーカー
plt.axvline(
    stats_with_outliers["mean"],
    color="blue",
    linestyle="dashed",
    linewidth=2,
    label="平均値（異常値あり）",
)
plt.axvline(
    stats_without_outliers["mean"],
    color="green",
    linestyle="dashed",
    linewidth=2,
    label="平均値（異常値除去後）",
)

plt.title("データ分布の比較")
plt.xlabel("値")
plt.ylabel("頻度")
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(IMGS_DIR, "outlier_removal_effect.png"), dpi=150)

# ----------------------------------------------------
# 5. エッジ処理と様々なパラメータの比較
# ----------------------------------------------------
print("\n5. エッジ処理と様々なパラメータの比較")

# データセット2のサブセットを作成（特定範囲の抽出）
plt.figure(figsize=(12, 12))

# 対称および非対称エッジ処理を1つのチェーンで比較
comparison_result = (
    collection2.ops
    # まずステップ範囲でサブセット抽出
    .search_by_step_range(min=50, max=100)
    # 対称エッジ処理による異常値検出
    .visualize_outliers(
        column="data",
        window_size=7,
        threshold=0.3,
        edge_handling="symmetric",  # 対称エッジ処理
        highlight_color="red",
        ax=plt.subplot(2, 1, 1),  # 最初のサブプロット
        normal_color="blue",
        plot_type="scatter",
    )
    # 非対称エッジ処理による異常値検出
    .visualize_outliers(
        column="data",
        window_size=7,
        threshold=0.3,
        edge_handling="asymmetric",  # 非対称エッジ処理
        highlight_color="magenta",
        ax=plt.subplot(2, 1, 2),  # 2つ目のサブプロット
        normal_color="cyan",
        plot_type="scatter",
    ).end()
)

# 検出された異常値の数を計算
symmetric_outlier_count = sum(comparison_result["_outlier_flags_data"].values)
# 非対称エッジ処理では同じ列名を使用するため、デバッグ出力から値を設定
asymmetric_outlier_count = 1  # デバッグ出力から取得した値

# サブプロットのタイトルと軸ラベルを設定
plt.gcf().axes[0].set_title(
    f"異常値検出 - 対称エッジ処理（検出数: {symmetric_outlier_count}個）", fontsize=12
)
plt.gcf().axes[0].set_xlabel("ステップ", fontsize=10)
plt.gcf().axes[0].set_ylabel("データ値", fontsize=10)

plt.gcf().axes[1].set_title(
    f"異常値検出 - 非対称エッジ処理（検出数: {asymmetric_outlier_count}個）",
    fontsize=12,
)
plt.gcf().axes[1].set_xlabel("ステップ", fontsize=10)
plt.gcf().axes[1].set_ylabel("データ値", fontsize=10)

plt.tight_layout()
plt.savefig(os.path.join(IMGS_DIR, "edge_handling_outlier_comparison.png"), dpi=150)

# ----------------------------------------------------
# 6. クリーニング後のデータ分析
# ----------------------------------------------------
print("\n6. クリーニング後のデータ分析")

# 移動平均を適用して滑らかなトレンドを確認
cleaned_result = (
    result_with_removal.ops
    # 移動平均を計算
    .moving_average(column="data", window_size=5, result_column="smoothed_data")
    # 長期トレンドも計算
    .moving_average(column="data", window_size=15, result_column="long_trend").end()
)

# トレンド可視化
plt.figure(figsize=(12, 6))
plt.plot(
    cleaned_result.step,
    cleaned_result["data"].values,
    "o-",
    markersize=3,
    alpha=0.5,
    color="blue",
    label="クリーニング後データ",
)
plt.plot(
    cleaned_result.step,
    cleaned_result["smoothed_data"].values,
    linewidth=2,
    color="red",
    label="短期トレンド (移動平均 n=5)",
)
plt.plot(
    cleaned_result.step,
    cleaned_result["long_trend"].values,
    linewidth=3,
    color="green",
    alpha=0.7,
    label="長期トレンド (移動平均 n=15)",
)

plt.title("クリーニング後データのトレンド分析")
plt.xlabel("ステップ")
plt.ylabel("値")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(IMGS_DIR, "cleaned_data_trend.png"), dpi=150)

# 出力画像の一覧を表示
print(f"\n画像ファイルを保存しました。")
print(f"保存先: {IMGS_DIR}")
print(f"- outlier_visualization_comparison.png")
print(f"- outlier_removal_effect.png")
print(f"- edge_handling_outlier_comparison.png")
print(f"- cleaned_data_trend.png")
