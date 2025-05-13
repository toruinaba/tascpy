"""
降伏点計算の詳細情報表示機能のサンプルコード

このサンプルでは、荷重-変位データから降伏点を計算する際に、
降伏点が見つからない場合の詳細な計算プロセス情報を取得・表示する方法を示します。
通常の成功するケースと、失敗するケースの両方を実演します。
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, Tuple, Optional, List

# tascpyをインポート
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import NumberColumn, Column
from tascpy.domains.load_displacement import LoadDisplacementCollection

# 荷重-変位ドメインの操作関数をインポート
from tascpy.operations.load_displacement.analysis import find_yield_point
from tascpy.operations.load_displacement.plot import plot_load_displacement


def create_modified_data(
    collection: LoadDisplacementCollection, modification_type: str = "linear"
) -> LoadDisplacementCollection:
    """降伏点検出の挙動を確認するためのテストデータを作成

    Args:
        collection: 元となる荷重-変位コレクション
        modification_type: 修正タイプ ("linear", "elastic", "no_intersection")

    Returns:
        LoadDisplacementCollection: 修正されたデータ
    """
    result = collection.clone()

    # 荷重と変位データの取得
    disp_column = result.displacement_column
    load_column = result.load_column

    disp_data = result[disp_column].values.copy()
    load_data = result[load_column].values.copy()

    # データの修正
    if modification_type == "linear":
        # 完全な線形関係にする（降伏点なし）
        stiffness = 5.0  # 一定の勾配
        load_data = [d * stiffness for d in disp_data]

    elif modification_type == "elastic":
        # 限りなく弾性に近い挙動にする（降伏点検出が難しい）
        stiffness = 5.0
        for i in range(len(disp_data)):
            # わずかに非線形性を持たせる
            load_data[i] = (
                disp_data[i] * stiffness * (1 - 0.01 * disp_data[i] / max(disp_data))
            )

    elif modification_type == "no_intersection":
        # オフセット線と交点がないケース
        stiffness = 5.0
        offset = 2.0  # 大きなオフセット
        for i in range(len(disp_data)):
            # 下側に大きくずれた線形関係
            load_data[i] = disp_data[i] * stiffness - offset

    # 修正したデータをコレクションに反映
    result.columns[load_column] = Column(
        ch=result.columns[load_column].ch,
        name=load_column,
        unit=result.columns[load_column].unit,
        values=load_data,
        metadata=result.columns[load_column].metadata,
    )

    # データ説明をメタデータに追加
    if result.metadata is None:
        result.metadata = {}

    # 荷重列と変位列の情報を明示的にメタデータに設定
    # これにより、find_yield_point関数が正しい列を見つけられる
    result.metadata["domain"] = "load_displacement"
    result._load_column = load_column
    result._displacement_column = disp_column

    result.metadata["description"] = f"Modified data ({modification_type})"

    return result


def analyze_and_print_yield_details(
    collection: LoadDisplacementCollection,
    method: str = "offset",
    offset_value: float = 0.002,
    factor: float = 0.33,
    debug_mode: bool = False,
    fail_silently: bool = False,
) -> Tuple[Optional[LoadDisplacementCollection], bool]:
    """降伏点を計算し結果と計算過程の詳細を表示

    Args:
        collection: 荷重-変位コレクション
        method: 計算方法 ('offset', 'general')
        offset_value: オフセット値（オフセット法の場合）
        factor: 勾配比率（一般降伏法の場合）
        debug_mode: デバッグ情報をコンソールに出力するかどうか
        fail_silently: 例外を発生させずに失敗情報を返すかどうか

    Returns:
        Tuple[LoadDisplacementCollection, bool]: 結果コレクションと成功フラグ
    """
    print(f"\n===== 降伏点計算の詳細分析 ({method}法) =====")

    try:
        # 降伏点の計算
        result = find_yield_point(
            collection,
            method=method,
            offset_value=offset_value,
            factor=factor,
            range_start=0.1,
            range_end=0.3,
            debug_mode=debug_mode,
            fail_silently=fail_silently,
        )

        # 成功した場合の処理
        print("✅ 降伏点が正常に計算されました")

        # メタデータからの情報抽出
        if (
            "analysis" in result.metadata
            and "yield_point" in result.metadata["analysis"]
        ):
            yield_info = result.metadata["analysis"]["yield_point"]
            debug_info = result.metadata["analysis"]["yield_point_calculation"][
                "debug_info"
            ]

            print("\n【基本情報】")
            print(f"使用メソッド: {yield_info['method']}")
            print(
                f"降伏変位: {yield_info['displacement']:.5f} {collection[collection.displacement_column].unit}"
            )
            print(
                f"降伏荷重: {yield_info['load']:.3f} {collection[collection.load_column].unit}"
            )
            print(f"初期勾配: {yield_info['initial_slope']:.3f}")

            print("\n【計算過程の情報】")
            print(f"データ点数: {debug_info['data_stats']['data_points']}")
            print(
                f"荷重範囲: {debug_info['data_stats']['min_load']:.3f} - {debug_info['data_stats']['max_load']:.3f}"
            )
            print(
                f"変位範囲: {debug_info['data_stats']['min_disp']:.5f} - {debug_info['data_stats']['max_disp']:.5f}"
            )
            print(
                f"計算範囲: {debug_info['data_range']['range_start']*100}% - {debug_info['data_range']['range_end']*100}%"
            )
            print(f"計算範囲の点数: {debug_info['data_range']['num_points_in_range']}")
            print(f"初期勾配の品質 (R²): {debug_info['r_squared']:.3f}")

            if method == "offset":
                print("\n【オフセット法の詳細】")
                offset_info = debug_info["offset_method"]
                print(f"オフセット値: {offset_info['offset_value']}")
                print(f"オフセット量: {offset_info['offset_amount']:.5f}")
                print(
                    f"差分統計: 最小={offset_info['diff_stats']['min']:.3f}, "
                    + f"最大={offset_info['diff_stats']['max']:.3f}, "
                    + f"平均={offset_info['diff_stats']['mean']:.3f}"
                )
                print(
                    f"符号変化: {'あり' if offset_info['diff_stats']['has_sign_change'] else 'なし'}"
                )

                # 交点情報
                if "yield_point" in debug_info and debug_info["yield_point"]["found"]:
                    yield_point = debug_info["yield_point"]
                    print("\n【交点の詳細】")
                    print(f"交点インデックス: {yield_point['intersection_indices']}")
                    print(f"補間比率: {yield_point['intersection_ratio']:.3f}")

            elif method == "general":
                print("\n【一般降伏法の詳細】")
                general_info = debug_info["general_method"]
                print(f"係数: {general_info['factor']}")
                print(f"閾値: {general_info['threshold']:.3f}")
                print(
                    f"勾配統計: 最小={general_info['slopes_stats']['min']:.3f}, "
                    + f"最大={general_info['slopes_stats']['max']:.3f}, "
                    + f"平均={general_info['slopes_stats']['mean']:.3f}"
                )

                # 降伏点情報
                if "yield_point" in debug_info and debug_info["yield_point"]["found"]:
                    yield_point = debug_info["yield_point"]
                    print("\n【降伏点の詳細】")
                    print(f"降伏点インデックス: {yield_point['index']}")
                    print(f"降伏点での勾配: {yield_point['slope_at_point']:.3f}")

            # 警告メッセージの表示
            if "warnings" in debug_info:
                print("\n【警告】")
                for warning in debug_info["warnings"]:
                    print(f"- {warning}")

        return result, True

    except ValueError as e:
        # エラーが発生した場合
        print(f"❌ エラー: {e}")

        if fail_silently:
            # 失敗時でも結果が返されている場合
            result = collection.ops.find_yield_point(
                method=method,
                offset_value=offset_value,
                factor=factor,
                range_start=0.1,
                range_end=0.3,
                debug_mode=debug_mode,
                fail_silently=True,
            ).end()

            # 失敗情報がメタデータにある場合
            if (
                "analysis" in result.metadata
                and "yield_point_calculation" in result.metadata["analysis"]
            ):
                calc_info = result.metadata["analysis"]["yield_point_calculation"]
                debug_info = calc_info["debug_info"]

                print("\n【計算失敗の詳細情報】")
                print(f"失敗理由: {calc_info['reason']}")
                print(f"使用メソッド: {debug_info['method']}")

                print("\n【計算過程の情報】")
                print(f"データ点数: {debug_info['data_stats']['data_points']}")
                print(
                    f"荷重範囲: {debug_info['data_stats']['min_load']:.3f} - {debug_info['data_stats']['max_load']:.3f}"
                )
                print(
                    f"変位範囲: {debug_info['data_stats']['min_disp']:.5f} - {debug_info['data_stats']['max_disp']:.5f}"
                )

                if "initial_slope" in debug_info:
                    print(f"初期勾配: {debug_info['initial_slope']:.3f}")
                    print(f"初期勾配の品質 (R²): {debug_info['r_squared']:.3f}")

                    if method == "offset":
                        print("\n【オフセット法の詳細】")
                        offset_info = debug_info["offset_method"]
                        print(f"オフセット値: {offset_info['offset_value']}")
                        print(f"オフセット量: {offset_info['offset_amount']:.5f}")
                        print(
                            f"差分統計: 最小={offset_info['diff_stats']['min']:.3f}, "
                            + f"最大={offset_info['diff_stats']['max']:.3f}, "
                            + f"平均={offset_info['diff_stats']['mean']:.3f}"
                        )
                        print(
                            f"符号変化: {'あり' if offset_info['diff_stats']['has_sign_change'] else 'なし'}"
                        )

                        # 交点がない場合の理由分析
                        if not offset_info["diff_stats"]["has_sign_change"]:
                            if offset_info["diff_stats"]["min"] > 0:
                                print(
                                    "※ すべての点がオフセット線より上にあるため交点がありません"
                                )
                            elif offset_info["diff_stats"]["max"] < 0:
                                print(
                                    "※ すべての点がオフセット線より下にあるため交点がありません"
                                )

                    elif method == "general" and "general_method" in debug_info:
                        print("\n【一般降伏法の詳細】")
                        general_info = debug_info["general_method"]
                        print(f"係数: {general_info['factor']}")
                        print(f"閾値: {general_info['threshold']:.3f}")
                        print(
                            f"勾配統計: 最小={general_info['slopes_stats']['min']:.3f}, "
                            + f"最大={general_info['slopes_stats']['max']:.3f}, "
                            + f"平均={general_info['slopes_stats']['mean']:.3f}"
                        )

                        if (
                            general_info["slopes_stats"]["min"]
                            > general_info["threshold"]
                        ):
                            print(
                                "※ すべての点の勾配が閾値を下回っていないため降伏点が見つかりません"
                            )

                # サンプルデータの表示
                if (
                    method == "offset"
                    and "offset_method" in debug_info
                    and "evaluation_points" in debug_info["offset_method"]
                ):
                    # オフセット法の場合のサンプルポイント
                    print("\n【評価ポイントのサンプル】")
                    print("インデックス, 変位, 荷重, オフセット線値, 差分")
                    points = debug_info["offset_method"]["evaluation_points"]
                    for point in points[:5]:  # 最初の5つだけ表示
                        print(
                            f"{point['index']}, {point['displacement']:.5f}, {point['load']:.2f}, "
                            + f"{point['offset_line_value']:.2f}, {point['difference']:.2f}"
                        )
                    if len(points) > 5:
                        print("...")

                elif (
                    method == "general"
                    and "general_method" in debug_info
                    and "slope_samples" in debug_info["general_method"]
                ):
                    # 一般降伏法の場合のサンプルポイント
                    print("\n【勾配サンプル】")
                    print("インデックス, 変位, 荷重, 勾配")
                    samples = debug_info["general_method"]["slope_samples"]
                    for sample in samples[:5]:  # 最初の5つだけ表示
                        print(
                            f"{sample['index']}, {sample['displacement']:.5f}, {sample['load']:.2f}, {sample['slope']:.2f}"
                        )
                    if len(samples) > 5:
                        print("...")

            return result, False
        else:
            # 例外を再発生
            raise

    except Exception as e:
        # その他の例外
        print(f"❌ 予期せぬエラー: {e}")
        return None, False


def visualize_yield_calculation(
    collection: LoadDisplacementCollection,
    result: LoadDisplacementCollection,
    success: bool,
    method: str = "offset",
    title: Optional[str] = None,
    output_path: Optional[str] = None,
) -> None:
    """降伏点計算の結果を可視化

    Args:
        collection: 元のコレクション
        result: 計算結果のコレクション
        success: 計算が成功したかどうか
        method: 計算方法
        title: グラフタイトル
        output_path: 出力パス
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # 元データの取得
    disp_column = collection.displacement_column
    load_column = collection.load_column
    disp_data = collection[disp_column].values
    load_data = collection[load_column].values

    # 元データの描画
    ax.plot(disp_data, load_data, "b.-", label="荷重-変位曲線")

    # メタデータからの情報取得
    if "analysis" in result.metadata:
        if success and "yield_point" in result.metadata["analysis"]:
            # 成功した場合の描画
            yield_info = result.metadata["analysis"]["yield_point"]
            debug_info = result.metadata["analysis"]["yield_point_calculation"][
                "debug_info"
            ]

            # 初期勾配線
            initial_slope = yield_info["initial_slope"]
            x_vals = np.linspace(0, max(disp_data), 100)
            ax.plot(
                x_vals,
                initial_slope * x_vals,
                "k--",
                label=f"初期勾配 ({initial_slope:.1f})",
            )

            # 降伏点
            yield_disp = yield_info["displacement"]
            yield_load = yield_info["load"]
            ax.plot(yield_disp, yield_load, "ro", markersize=8, label="降伏点")

            if method == "offset":
                # オフセット法の場合
                offset_value = yield_info["parameters"]["offset_value"]
                offset_line = (
                    initial_slope * x_vals
                    - initial_slope * offset_value * max(disp_data)
                )
                ax.plot(
                    x_vals,
                    offset_line,
                    "r--",
                    label=f"オフセット線 ({offset_value*100:.1f}%)",
                )

            elif method == "general":
                # 一般降伏法の場合
                factor = yield_info["parameters"]["factor"]
                ax.plot(
                    x_vals,
                    initial_slope * factor * x_vals,
                    "g--",
                    label=f"勾配閾値 ({factor*100:.1f}%)",
                )

        elif not success and "yield_point_calculation" in result.metadata["analysis"]:
            # 失敗した場合の描画
            calc_info = result.metadata["analysis"]["yield_point_calculation"]
            debug_info = calc_info["debug_info"]

            if "initial_slope" in debug_info:
                # 初期勾配線
                initial_slope = debug_info["initial_slope"]
                x_vals = np.linspace(0, max(disp_data), 100)
                ax.plot(
                    x_vals,
                    initial_slope * x_vals,
                    "k--",
                    label=f"初期勾配 ({initial_slope:.1f})",
                )

                if method == "offset" and "offset_method" in debug_info:
                    # オフセット法の場合
                    offset_value = debug_info["parameters"]["offset_value"]
                    offset_line = (
                        initial_slope * x_vals
                        - initial_slope * offset_value * max(disp_data)
                    )
                    ax.plot(
                        x_vals,
                        offset_line,
                        "r--",
                        label=f"オフセット線 ({offset_value*100:.1f}%)",
                    )

                    # サンプルポイントの表示
                    if "evaluation_points" in debug_info["offset_method"]:
                        points = debug_info["offset_method"]["evaluation_points"]
                        sample_indices = [p["index"] for p in points]
                        sample_disps = [p["displacement"] for p in points]
                        sample_loads = [p["load"] for p in points]
                        ax.scatter(
                            sample_disps,
                            sample_loads,
                            color="cyan",
                            s=30,
                            alpha=0.6,
                            label="評価ポイント",
                        )

                elif method == "general" and "general_method" in debug_info:
                    # 一般降伏法の場合
                    factor = debug_info["parameters"]["factor"]
                    threshold_line = initial_slope * factor * x_vals
                    ax.plot(
                        x_vals,
                        threshold_line,
                        "g--",
                        label=f"勾配閾値 ({factor*100:.1f}%)",
                    )

                    # サンプルポイントの表示
                    if "slope_samples" in debug_info["general_method"]:
                        samples = debug_info["general_method"]["slope_samples"]
                        sample_disps = [s["displacement"] for s in samples]
                        sample_loads = [s["load"] for s in samples]
                        ax.scatter(
                            sample_disps,
                            sample_loads,
                            color="cyan",
                            s=30,
                            alpha=0.6,
                            label="評価ポイント",
                        )

    # グラフの設定
    if title:
        ax.set_title(title)
    else:
        if success:
            ax.set_title(f"{method}法による降伏点計算 (成功)")
        else:
            ax.set_title(f"{method}法による降伏点計算 (失敗)")

    ax.set_xlabel(f"変位 ({collection[disp_column].unit})")
    ax.set_ylabel(f"荷重 ({collection[load_column].unit})")
    ax.grid(True, linestyle="--", alpha=0.7)
    ax.legend(loc="lower right")

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path)
        print(f"グラフを保存しました: {output_path}")

    plt.close()


def main() -> None:
    """メイン関数"""
    print("===== 降伏点計算の詳細情報表示機能のデモ =====")

    # CSVファイルからデータを読み込み
    print("\n【データの読み込み】")
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    sample_csv_path = os.path.join(data_dir, "load_displacement_sample.csv")

    # CSVファイルからColumnCollectionを作成
    collection = ColumnCollection.from_file(
        filepath=sample_csv_path, format_name="csv", auto_detect_types=True
    )

    # 荷重-変位ドメインに変換
    ld_collection = collection.ops.as_domain(
        "load_displacement", load_column="Force1", displacement_column="Displacement1"
    ).end()

    print(
        f"データ読み込み完了: {len(ld_collection)} 行 × {len(ld_collection.columns)} 列"
    )
    print(
        f"荷重列: {ld_collection.load_column}, 変位列: {ld_collection.displacement_column}"
    )

    output_dir = os.path.join(os.path.dirname(__file__), "imgs")
    os.makedirs(output_dir, exist_ok=True)

    # ============================================================================
    # ケース1: 通常のデータによる降伏点計算（成功例）
    # ============================================================================
    print("\n【ケース1: 通常データによる降伏点計算】")

    # デバッグモードをオンにして詳細情報を表示
    print("\nオフセット法による計算:")
    offset_result, offset_success = analyze_and_print_yield_details(
        ld_collection,
        method="offset",
        offset_value=0.002,  # 0.2%オフセット
        debug_mode=True,
    )

    # 結果の可視化
    if offset_result:
        visualize_yield_calculation(
            ld_collection,
            offset_result,
            offset_success,
            method="offset",
            title="通常データでのオフセット降伏点計算 (0.2%)",
            output_path=os.path.join(output_dir, "yield_normal_offset.png"),
        )

    print("\n一般降伏法による計算:")
    general_result, general_success = analyze_and_print_yield_details(
        ld_collection, method="general", factor=0.33, debug_mode=True  # 33%勾配低下
    )

    # 結果の可視化
    if general_result:
        visualize_yield_calculation(
            ld_collection,
            general_result,
            general_success,
            method="general",
            title="通常データでの一般降伏点計算 (33%)",
            output_path=os.path.join(output_dir, "yield_normal_general.png"),
        )

    # ============================================================================
    # ケース2: 完全弾性データによる降伏点計算（失敗例）
    # ============================================================================
    print("\n\n【ケース2: 完全弾性データによる降伏点計算】")

    # 線形データを作成（降伏点が見つからないケース）
    linear_data = create_modified_data(ld_collection, modification_type="linear")

    # 基本的なデータ表示
    print(f"生成したデータのタイプ: {linear_data.metadata['description']}")

    # 計算と詳細情報表示（失敗時にエラーを抑制）
    print("\nオフセット法による計算（失敗するケース）:")
    try:
        linear_offset_result, linear_offset_success = analyze_and_print_yield_details(
            linear_data,
            method="offset",
            offset_value=0.002,
            debug_mode=True,
            fail_silently=True,  # エラー発生時も処理を継続
        )

        # 結果の可視化
        if linear_offset_result:
            visualize_yield_calculation(
                linear_data,
                linear_offset_result,
                linear_offset_success,
                method="offset",
                title="線形データでのオフセット降伏点計算 (失敗例)",
                output_path=os.path.join(output_dir, "yield_linear_offset_failed.png"),
            )
    except Exception as e:
        print(f"予期せぬエラー: {e}")

    # ============================================================================
    # ケース3: 交点なしデータによる降伏点計算（失敗例）
    # ============================================================================
    print("\n\n【ケース3: 交点なしデータによる降伏点計算】")

    # 交点がないデータを作成
    no_intersection_data = create_modified_data(
        ld_collection, modification_type="no_intersection"
    )

    print(f"生成したデータのタイプ: {no_intersection_data.metadata['description']}")

    # 計算と詳細情報表示（失敗時にエラーを抑制）
    print("\nオフセット法による計算（交点なしのケース）:")
    try:
        no_int_result, no_int_success = analyze_and_print_yield_details(
            no_intersection_data,
            method="offset",
            offset_value=0.002,
            debug_mode=True,
            fail_silently=True,
        )

        # 結果の可視化
        if no_int_result:
            visualize_yield_calculation(
                no_intersection_data,
                no_int_result,
                no_int_success,
                method="offset",
                title="交点なしデータでのオフセット降伏点計算 (失敗例)",
                output_path=os.path.join(
                    output_dir, "yield_no_intersection_failed.png"
                ),
            )
    except Exception as e:
        print(f"予期せぬエラー: {e}")

    # ============================================================================
    # ケース4: 弾性に近いデータでの閾値調整による計算
    # ============================================================================
    print("\n\n【ケース4: 弾性に近いデータでの閾値調整による計算】")

    # わずかに非線形性のあるデータを作成
    elastic_data = create_modified_data(ld_collection, modification_type="elastic")

    print(f"生成したデータのタイプ: {elastic_data.metadata['description']}")

    # 小さなオフセット値での計算（失敗する可能性が高い）
    print("\n小さなオフセット値 (0.1%) での計算:")
    try:
        small_offset_result, small_offset_success = analyze_and_print_yield_details(
            elastic_data,
            method="offset",
            offset_value=0.001,  # 0.1%オフセット（小さい）
            debug_mode=True,
            fail_silently=True,
        )

        # 結果の可視化
        if small_offset_result:
            visualize_yield_calculation(
                elastic_data,
                small_offset_result,
                small_offset_success,
                method="offset",
                title="弾性に近いデータでの小さなオフセット値計算",
                output_path=os.path.join(output_dir, "yield_elastic_small_offset.png"),
            )
    except Exception as e:
        print(f"予期せぬエラー: {e}")

    # 大きなオフセット値での計算（成功する可能性が高い）
    print("\n大きなオフセット値 (1.0%) での計算:")
    try:
        large_offset_result, large_offset_success = analyze_and_print_yield_details(
            elastic_data,
            method="offset",
            offset_value=0.01,  # 1.0%オフセット（大きい）
            debug_mode=True,
            fail_silently=True,
        )

        # 結果の可視化
        if large_offset_result:
            visualize_yield_calculation(
                elastic_data,
                large_offset_result,
                large_offset_success,
                method="offset",
                title="弾性に近いデータでの大きなオフセット値計算",
                output_path=os.path.join(output_dir, "yield_elastic_large_offset.png"),
            )
    except Exception as e:
        print(f"予期せぬエラー: {e}")

    print("\n===== デモ完了 =====")


if __name__ == "__main__":
    main()
