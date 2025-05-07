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


if __name__ == "__main__":
    main()
