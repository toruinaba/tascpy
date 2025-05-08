"""
荷重-変位ドメインの活用例を示すサンプルコード

このサンプルでは、CSVファイルから荷重-変位データを読み込み、
ColumnCollectionからLoadDisplacementCollectionへの変換と、
荷重-変位ドメイン特有の解析操作を行う方法を示します。
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import NumberColumn
from tascpy.domains.load_displacement import LoadDisplacementCollection

# 荷重-変位ドメインの操作関数を直接インポート
from tascpy.operations.load_displacement.analysis import (
    calculate_slopes,
    calculate_stiffness,
    find_yield_point,
)

# 荷重-変位プロット関数をインポート
from tascpy.operations.load_displacement.plot import (
    plot_load_displacement,
    plot_yield_point,
    plot_yield_analysis_details,
    compare_yield_methods,
)


def main():
    """メイン関数"""
    # ===== CSVファイルからデータを読み込み =====
    print("===== CSVファイルからデータを読み込み =====")

    # 現在のスクリプトからの相対パスでデータファイルを取得
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    sample_csv_path = os.path.join(data_dir, "load_displacement_sample.csv")

    # CSVファイルからColumnCollectionを作成
    collection = ColumnCollection.from_file(
        filepath=sample_csv_path, format_name="csv", auto_detect_types=True
    )

    print(
        f"読み込んだデータの形状: {len(collection)} 行 × {len(collection.columns)} 列"
    )
    print(f"列名: {list(collection.columns.keys())}")

    # 最初と最後のいくつかのデータを表示
    force_column = "Force1"
    disp_column = "Displacement1"

    print("\n荷重データ (最初の5行):")
    print(collection[force_column].values[:5])

    print("\n変位データ (最初の5行):")
    print(collection[disp_column].values[:5])

    # ===== LoadDisplacementCollectionへの変換 =====
    print("\n===== LoadDisplacementCollectionへの変換 =====")

    # 荷重と変位の列を指定して荷重-変位ドメインへ変換
    # 方法1: 直接初期化
    ld_collection1 = LoadDisplacementCollection(
        step=collection.step,
        columns=collection.columns,
        load_column=force_column,
        displacement_column=disp_column,
    )
    print(f"方法1: ドメイン = {ld_collection1.domain}")
    print(f"    荷重カラム = {ld_collection1.load_column}")
    print(f"    変位カラム = {ld_collection1.displacement_column}")

    # 方法2: 操作を使用した変換
    ld_collection2 = collection.ops.as_domain(
        "load_displacement", load_column=force_column, displacement_column=disp_column
    ).end()
    print(f"方法2: ドメイン = {ld_collection2.domain}")
    print(f"    荷重カラム = {ld_collection2.load_column}")
    print(f"    変位カラム = {ld_collection2.displacement_column}")

    # 以降は変換されたコレクションを使用
    ld_collection = ld_collection2

    # 利用可能なメソッドを確認
    print("\n利用可能なメソッド:")
    available_methods = [
        method for method in dir(ld_collection.ops) if not method.startswith("_")
    ]
    print(f"LoadDisplacementCollection.ops の利用可能なメソッド: {available_methods}")

    # ===== データの可視化（基本） =====
    print("\n===== 荷重-変位曲線の可視化 =====")

    # データの取得
    load_data = ld_collection[ld_collection.load_column].values
    disp_data = ld_collection[ld_collection.displacement_column].values

    # 基本的な荷重-変位曲線
    plt.figure(figsize=(10, 6))
    plt.plot(disp_data, load_data, "b.-", label="荷重-変位曲線")
    plt.title("荷重-変位曲線")
    plt.xlabel(f"変位 ({ld_collection[ld_collection.displacement_column].unit})")
    plt.ylabel(f"荷重 ({ld_collection[ld_collection.load_column].unit})")
    plt.grid(True)
    plt.legend()

    # 図の保存
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(output_dir, "load_displacement_basic.png")
    plt.savefig(output_path)
    plt.close()

    print(f"基本荷重-変位曲線の図を保存しました: {output_path}")

    # ===== 荷重-変位ドメイン特有の解析操作 =====
    print("\n===== 荷重-変位ドメイン特有の解析操作 =====")

    # 1. 傾き（接線剛性）の計算
    print("\n1. 傾き（接線剛性）の計算")
    # ops経由ではなく直接関数を呼び出し
    slopes = calculate_slopes(ld_collection)

    slope_column = [col for col in slopes.columns.keys() if "slope" in col.lower()][0]
    slope_values = [
        s if s is not None else float("nan") for s in slopes[slope_column].values
    ]

    print(f"接線剛性の列名: {slope_column}")
    valid_slopes = [s for s in slope_values if not np.isnan(s)]
    if valid_slopes:
        print(f"接線剛性の範囲: {min(valid_slopes):.3f} ～ {max(valid_slopes):.3f}")

    # 2. 初期剛性の計算（線形領域からの推定）
    print("\n2. 初期剛性の計算")

    # 線形領域の範囲を指定して剛性を計算（相対変位）
    try:
        # ops経由ではなく直接関数を呼び出し
        stiffness = calculate_stiffness(
            ld_collection,
            range_start=0.1,  # 初期10%（荷重範囲の相対位置）
            range_end=0.4,  # 40%まで（荷-load範囲の相対位置）
            method="linear_regression",
        )

        print(
            f"線形回帰による初期剛性: {stiffness:.3f} {ld_collection[ld_collection.load_column].unit}/{ld_collection[ld_collection.displacement_column].unit}"
        )

        # 絶対範囲を指定するのではなく、別の範囲を指定して初期剛性を計算
        # disp_startとdisp_endはサポートされていないため、range_startとrange_endに変更
        stiffness_abs = calculate_stiffness(
            ld_collection,
            range_start=0.0,  # 最小荷重から
            range_end=0.2,  # 最大荷重の20%まで
            method="linear_regression",
        )

        print(
            f"小さい範囲での初期剛性: {stiffness_abs:.3f} {ld_collection[ld_collection.load_column].unit}/{ld_collection[ld_collection.displacement_column].unit}"
        )

    except Exception as e:
        print(f"剛性計算でエラー: {str(e)}")

    # 3. 降伏点の解析
    print("\n3. 降伏点の解析")

    try:
        # 3.1 オフセット法による降伏点の特定
        # range_startとrange_endを調整して線形領域のみを使用
        yield_result_offset = find_yield_point(
            ld_collection,
            method="offset",
            range_start=0.05,  # 荷重の5%から (より初期部分を使用)
            range_end=0.25,  # 荷重の25%まで (非線形になる前の範囲)
            offset_value=0.2,  # 0.5から0.2に調整 (より一般的な値)
            result_prefix="yield_offset",
        )

        yield_disp_offset = yield_result_offset["yield_offset_displacement"].values[0]
        yield_load_offset = yield_result_offset["yield_offset_load"].values[0]

        print(f"オフセット法による降伏点:")
        print(
            f"  変位 = {yield_disp_offset:.3f} {ld_collection[ld_collection.displacement_column].unit}"
        )
        print(
            f"  荷重 = {yield_load_offset:.3f} {ld_collection[ld_collection.load_column].unit}"
        )

        # 初期勾配の取得
        initial_slope_offset = yield_result_offset.metadata["analysis"]["yield_point"][
            "initial_slope"
        ]
        print(f"  初期勾配 = {initial_slope_offset:.3f}")

        # 3.2 一般降伏法による降伏点の特定
        # 同じ範囲設定を適用し、低めのfactor値を使用
        yield_result_general = find_yield_point(
            ld_collection,
            method="general",
            range_start=0.05,  # オフセット法と同じ設定
            range_end=0.25,  # オフセット法と同じ設定
            factor=0.25,  # 初期勾配の25%を降伏点と定義（低めに設定）
            result_prefix="yield_general",
        )

        yield_disp_general = yield_result_general["yield_general_displacement"].values[
            0
        ]
        yield_load_general = yield_result_general["yield_general_load"].values[0]

        print(f"一般降伏法による降伏点:")
        print(
            f"  変位 = {yield_disp_general:.3f} {ld_collection[ld_collection.displacement_column].unit}"
        )
        print(
            f"  荷重 = {yield_load_general:.3f} {ld_collection[ld_collection.load_column].unit}"
        )

        # 初期勾配の取得
        initial_slope_general = yield_result_general.metadata["analysis"][
            "yield_point"
        ]["initial_slope"]
        print(f"  初期勾配 = {initial_slope_general:.3f}")

    except Exception as e:
        print(f"降伏点解析でエラー: {str(e)}")

    # ===== 解析結果の可視化 =====
    print("\n===== 解析結果の可視化 =====")

    try:
        plt.figure(figsize=(12, 9))

        # 1. 荷重-変位曲線と降伏点
        plt.subplot(2, 1, 1)
        plt.plot(disp_data, load_data, "b.-", label="荷重-変位曲線")

        # 降伏点の表示（計算済みの場合）
        if "yield_disp_offset" in locals():
            plt.plot(
                yield_disp_offset,
                yield_load_offset,
                "ro",
                markersize=8,
                label=f"オフセット降伏点 ({yield_load_offset:.2f} {ld_collection[ld_collection.load_column].unit})",
            )

        if "yield_disp_general" in locals():
            plt.plot(
                yield_disp_general,
                yield_load_general,
                "go",
                markersize=8,
                label=f"一般降伏点 ({yield_load_general:.2f} {ld_collection[ld_collection.load_column].unit})",
            )

        # 初期剛性ラインの表示
        if "initial_slope_offset" in locals():
            x_vals = np.linspace(0, max(disp_data) * 0.6, 100)
            plt.plot(
                x_vals,
                initial_slope_offset * x_vals,
                "k--",
                label=f"初期勾配 ({initial_slope_offset:.1f})",
            )

            # オフセットライン
            offset_value = yield_result_offset.metadata["analysis"]["yield_point"][
                "parameters"
            ]["offset_value"]
            plt.plot(
                x_vals,
                initial_slope_offset * x_vals
                - initial_slope_offset * offset_value * max(disp_data),
                "r--",
                label=f"オフセットライン ({offset_value*100:.1f}%)",
            )

            # 一般降伏法のライン
            if "initial_slope_general" in locals():
                factor = yield_result_general.metadata["analysis"]["yield_point"][
                    "parameters"
                ]["factor"]
                plt.plot(
                    x_vals,
                    initial_slope_general * factor * x_vals,
                    "g--",
                    label=f"勾配低下ライン ({factor*100:.1f}%)",
                )

        plt.title("荷重-変位曲線と降伏点解析")
        plt.xlabel(f"変位 ({ld_collection[ld_collection.displacement_column].unit})")
        plt.ylabel(f"荷重 ({ld_collection[ld_collection.load_column].unit})")
        plt.grid(True)
        plt.legend(loc="lower right")

        # 2. 接線剛性の変化
        plt.subplot(2, 1, 2)
        # 接線剛性（変位との関係）
        valid_indices = [i for i, s in enumerate(slope_values) if not np.isnan(s)]
        valid_disps = [disp_data[i] for i in valid_indices]
        valid_slopes = [slope_values[i] for i in valid_indices]

        plt.plot(valid_disps, valid_slopes, "g.-", label="接線剛性")

        if "initial_slope_offset" in locals():
            plt.axhline(
                y=initial_slope_offset,
                color="k",
                linestyle="--",
                label=f"初期勾配 ({initial_slope_offset:.1f})",
            )
            plt.axhline(
                y=initial_slope_offset * 0.333,
                color="g",
                linestyle="--",
                label="33.3%初期勾配",
            )

        plt.title("変位と接線剛性の関係")
        plt.xlabel(f"変位 ({ld_collection[ld_collection.displacement_column].unit})")
        plt.ylabel(
            f"接線剛性 ({ld_collection[ld_collection.load_column].unit}/{ld_collection[ld_collection.displacement_column].unit})"
        )
        plt.grid(True)
        plt.legend(loc="upper right")

        plt.tight_layout()

        # 図の保存
        output_path = os.path.join(output_dir, "load_displacement_analysis.png")
        plt.savefig(output_path)
        plt.close()

        print(f"解析結果の図を保存しました: {output_path}")

    except Exception as e:
        print(f"可視化でエラー: {str(e)}")

    # ===== plot.py のユーティリティ関数の使用例 =====
    print("\n===== plot.py のユーティリティ関数の使用例 =====")

    try:
        # 既存の荷重変位データを使用（既に解析済みのものを使用）

        # 1. 基本的な荷重-変位プロット
        print("\n1. 基本的な荷重-変位プロット")
        fig1, ax1 = plot_load_displacement(ld_collection)
        plt.title("基本的な荷重-変位曲線")
        plt.tight_layout()
        output_path = os.path.join(output_dir, "plot_basic.png")
        plt.savefig(output_path)
        plt.close(fig1)
        print(f"基本的な荷重-変位プロットを保存: {output_path}")

        # 2. 降伏点のプロット（オフセット法）
        print("\n2. オフセット法による降伏点プロット")
        # オフセット法で降伏点を計算
        offset_result = find_yield_point(
            ld_collection,
            method="offset",
            offset_value=0.002,  # 0.2%ストレインオフセット
            range_start=0.05,
            range_end=0.3,
            result_prefix="offset_yield",
        )

        fig2, ax2 = plot_yield_point(offset_result)
        plt.title("オフセット法による降伏点 (0.2%ストレイン)")
        plt.tight_layout()
        output_path = os.path.join(output_dir, "plot_offset_yield.png")
        plt.savefig(output_path)
        plt.close(fig2)
        print(f"オフセット法による降伏点プロットを保存: {output_path}")

        # 3. 降伏点の詳細解析プロット
        print("\n3. 降伏点の詳細解析プロット")
        fig3, ax3 = plot_yield_analysis_details(offset_result)
        plt.tight_layout()
        output_path = os.path.join(output_dir, "plot_yield_details.png")
        plt.savefig(output_path)
        plt.close(fig3)
        print(f"降伏点の詳細解析プロットを保存: {output_path}")

        # 4. 複数の降伏点定義方法の比較
        print("\n4. 複数の降伏点定義方法の比較")
        methods = [
            {
                "method": "offset",
                "offset_value": 0.001,  # 0.1%ストレインオフセット
                "result_prefix": "yield_offset_small",
            },
            {
                "method": "offset",
                "offset_value": 0.002,  # 0.2%ストレインオフセット（標準）
                "result_prefix": "yield_offset_standard",
            },
            {
                "method": "offset",
                "offset_value": 0.005,  # 0.5%ストレインオフセット
                "result_prefix": "yield_offset_large",
            },
            {
                "method": "general",
                "factor": 0.33,  # 33%勾配低下
                "result_prefix": "yield_general_33",
            },
            {
                "method": "general",
                "factor": 0.50,  # 50%勾配低下
                "result_prefix": "yield_general_50",
            },
        ]

        fig4, ax4 = compare_yield_methods(ld_collection, methods=methods)
        plt.title("様々な降伏点定義方法の比較")
        plt.tight_layout()
        output_path = os.path.join(output_dir, "plot_yield_comparison.png")
        plt.savefig(output_path)
        plt.close(fig4)
        print(f"複数の降伏点定義方法の比較プロットを保存: {output_path}")

        # 5. カスタマイズされたプロット例
        print("\n5. カスタマイズされたプロット例")
        fig5, (ax5a, ax5b) = plt.subplots(1, 2, figsize=(14, 6))

        # 左側: 基本的な荷重-変位曲線をカスタマイズ
        plot_load_displacement(
            ld_collection,
            ax=ax5a,
            color="blue",
            linestyle="-",
            linewidth=1.5,
            marker="o",
            markersize=4,
            alpha=0.7,
            label="試験データ",
        )
        ax5a.set_title("カスタマイズされた荷重-変位曲線")
        ax5a.grid(True, linestyle="--", alpha=0.6)

        # 右側: 降伏点の比較
        # 2種類の方法でプロットして比較
        offset_small = find_yield_point(
            ld_collection,
            method="offset",
            offset_value=0.001,
            result_prefix="small_offset",
        )

        general = find_yield_point(
            ld_collection, method="general", factor=0.33, result_prefix="general_yield"
        )

        # オフセット法のプロット
        plot_yield_point(
            offset_small,
            ax=ax5b,
            plot_original_data=True,
            plot_initial_slope=True,
            plot_offset_line=True,
        )

        # 一般降伏法のプロットを同じグラフに追加
        yield_data = general.metadata["analysis"]["yield_point"]
        yield_disp = yield_data["displacement"]
        yield_load = yield_data["load"]

        ax5b.scatter(
            [yield_disp],
            [yield_load],
            color="green",
            s=100,
            marker="^",
            label="一般降伏法 (33%)",
            zorder=5,
        )

        # タイトルと凡例の設定
        ax5b.set_title("2つの降伏点定義の比較")
        ax5b.legend(loc="lower right")

        plt.tight_layout()
        output_path = os.path.join(output_dir, "plot_customized.png")
        plt.savefig(output_path)
        plt.close(fig5)
        print(f"カスタマイズされたプロット例を保存: {output_path}")

        # 6. 実用的なレポート用プロット
        print("\n6. 実用的なレポート用プロット")
        fig6, axs = plt.subplots(2, 2, figsize=(12, 10))

        # 1. 基本的な荷重-変位曲線
        plot_load_displacement(ld_collection, ax=axs[0, 0])
        axs[0, 0].set_title("荷重-変位曲線")

        # 2. 0.2%オフセット降伏の詳細
        offset_std = find_yield_point(
            ld_collection,
            method="offset",
            offset_value=0.002,
            result_prefix="std_offset",
        )
        plot_yield_analysis_details(offset_std, ax=axs[0, 1])
        axs[0, 1].set_title("0.2%オフセット降伏解析")

        # 3. 一般降伏法の詳細
        general_yield = find_yield_point(
            ld_collection, method="general", factor=0.33, result_prefix="general_33"
        )
        plot_yield_analysis_details(general_yield, ax=axs[1, 0])
        axs[1, 0].set_title("一般降伏法 (33%勾配)")

        # 4. 複数手法の比較
        methods = [
            {
                "method": "offset",
                "offset_value": 0.002,
                "result_prefix": "yield_offset_std",
            },
            {"method": "general", "factor": 0.33, "result_prefix": "yield_general_std"},
        ]
        compare_yield_methods(ld_collection, methods=methods, ax=axs[1, 1])
        axs[1, 1].set_title("降伏点定義の比較")

        # 全体タイトル設定
        fig6.suptitle("荷重-変位解析レポート", fontsize=16)
        fig6.tight_layout(rect=[0, 0, 1, 0.95])  # suptitleのスペースを確保

        output_path = os.path.join(output_dir, "load_displacement_report.png")
        plt.savefig(output_path)
        plt.close(fig6)
        print(f"実用的なレポート用プロットを保存: {output_path}")

        # すべてのプロットが正常に完了したことを報告
        print("\nすべてのplot.pyユーティリティ関数のデモを完了しました")

    except Exception as e:
        print(f"プロットでエラー: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
