"""荷重-変位プロット機能の機能テスト"""

import os
import pytest
import numpy as np

# Matplotlibのバックエンドを設定（グラフィカルバックエンドを使用しない）
import matplotlib

matplotlib.use("Agg")  # 非対話的なバックエンドを使用
import matplotlib.pyplot as plt
from pathlib import Path
import tempfile
import shutil

from tascpy.core.collection import ColumnCollection
from tascpy.domains.load_displacement import LoadDisplacementCollection
from tascpy.operations.load_displacement.analysis import find_yield_point
from tascpy.operations.load_displacement.plot import (
    plot_load_displacement,
    plot_yield_point,
    plot_yield_analysis_details,
    compare_yield_methods,
)


@pytest.fixture
def sample_data_path():
    """サンプルデータファイルのパスを返す"""
    base_path = Path(__file__).parent.parent.parent
    return base_path / "examples" / "data" / "load_displacement_sample.csv"


@pytest.fixture
def csv_file_info(sample_data_path):
    """CSVファイルから適切な荷重・変位カラム名を取得"""
    # ファイルが存在することを確認
    if not sample_data_path.exists():
        pytest.skip(f"サンプルデータファイル {sample_data_path} が見つかりません")

    # CSVファイルを読み込み - ファイル構造に合わせて設定
    collection = ColumnCollection.from_file(
        str(sample_data_path), format_name="csv", auto_detect_types=True
    )

    # 自動的にカラム型を判定
    collection = collection.auto_detect_column_types()

    # テスト用に適切なカラム名を識別
    force_columns = [
        name
        for name, col in collection.columns.items()
        if getattr(col, "unit", "") == "kN"
    ]
    disp_columns = [
        name
        for name, col in collection.columns.items()
        if getattr(col, "unit", "") == "mm"
    ]

    if force_columns and disp_columns:
        force_col = force_columns[0]
        disp_col = disp_columns[0]
        return (force_col, disp_col)
    else:
        pytest.skip("適切な荷重・変位カラムが見つかりませんでした")
        return None


@pytest.fixture
def load_displacement_data(sample_data_path, csv_file_info):
    """サンプルデータから荷重変位コレクションを作成"""
    # カラム名が取得できていることを確認
    if not csv_file_info:
        pytest.skip("適切な荷重・変位カラムが見つかりませんでした")

    force_col, disp_col = csv_file_info

    # CSVファイルを読み込み - 修正した設定
    collection = ColumnCollection.from_file(
        str(sample_data_path),
        format_name="csv",
        delimiter=",",
        title_row=0,  # 「無題」のタイトル行
        ch_row=1,  # データ番号,日付,時刻,CH0,CH1
        name_row=2,  # ,,,Force1,Displacement1
        unit_row=3,  # ,,,kN,mm
        data_start_row=4,
        step_col=0,
        date_col=1,
        time_col=2,
        data_start_col=3,
    )

    # 自動的にカラム型を判定
    collection = collection.auto_detect_column_types()

    # ドメインコレクションに変換
    ld_collection = collection.ops.as_domain(
        "load_displacement", load_column=force_col, displacement_column=disp_col
    ).end()

    return ld_collection


def test_inspect_csv_data(csv_file_info):
    """CSVファイルの構造を確認するテスト"""
    if csv_file_info:
        force_col, disp_col = csv_file_info
        print(f"\nCSVファイルの構造:")
        print(f"- 荷重カラム: {force_col}")
        print(f"- 変位カラム: {disp_col}")
        assert force_col == "Force1"  # 期待通りのカラム名であることを確認
        assert disp_col == "Displacement1"  # 期待通りのカラム名であることを確認
    else:
        pytest.fail("CSVファイルから荷重・変位カラムを取得できませんでした")


class TestLoadDisplacementPlotFunctional:
    """荷重-変位プロット機能の機能テスト"""

    def setup_method(self):
        """各テスト前に一時ディレクトリを作成"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """各テスト後に一時ディレクトリを削除"""
        shutil.rmtree(self.temp_dir)

    def test_plot_workflow(self, load_displacement_data):
        """フルプロットワークフローのテスト

        各プロット機能を順番に使用し、一連のワークフローをテスト
        """
        # 降伏点解析
        offset_result = find_yield_point(
            load_displacement_data, method="offset", offset_value=0.002
        )

        general_result = find_yield_point(
            load_displacement_data, method="general", factor=0.33
        )

        # 基本的な荷重-変位プロット
        fig1, ax1 = plot_load_displacement(load_displacement_data)
        basic_plot_path = Path(self.temp_dir) / "basic_plot.png"
        fig1.savefig(basic_plot_path)
        plt.close(fig1)

        # オフセット法による降伏点プロット
        fig2, ax2 = plot_yield_point(offset_result)
        offset_plot_path = Path(self.temp_dir) / "offset_yield_plot.png"
        fig2.savefig(offset_plot_path)
        plt.close(fig2)

        # 一般降伏法による降伏点プロット
        fig3, ax3 = plot_yield_point(general_result)
        general_plot_path = Path(self.temp_dir) / "general_yield_plot.png"
        fig3.savefig(general_plot_path)
        plt.close(fig3)

        # 詳細解析情報プロット
        fig4, ax4 = plot_yield_analysis_details(offset_result)
        details_plot_path = Path(self.temp_dir) / "yield_analysis_details.png"
        fig4.savefig(details_plot_path)
        plt.close(fig4)

        # 複数手法比較プロット
        methods = [
            {
                "method": "offset",
                "offset_value": 0.002,
                "result_prefix": "yield_offset",
            },
            {
                "method": "offset",
                "offset_value": 0.005,
                "result_prefix": "yield_offset_large",
            },
            {"method": "general", "factor": 0.33, "result_prefix": "yield_general"},
        ]

        fig5, ax5 = compare_yield_methods(load_displacement_data, methods=methods)
        comparison_plot_path = Path(self.temp_dir) / "yield_methods_comparison.png"
        fig5.savefig(comparison_plot_path)
        plt.close(fig5)

        # ファイルが作成されたことを確認
        assert basic_plot_path.exists()
        assert offset_plot_path.exists()
        assert general_plot_path.exists()
        assert details_plot_path.exists()
        assert comparison_plot_path.exists()

        # ファイルサイズが0より大きいことを確認（描画が行われた証拠）
        assert basic_plot_path.stat().st_size > 0
        assert offset_plot_path.stat().st_size > 0
        assert general_plot_path.stat().st_size > 0
        assert details_plot_path.stat().st_size > 0
        assert comparison_plot_path.stat().st_size > 0

    def test_custom_plot_parameters(self, load_displacement_data):
        """カスタムパラメータを使ったプロットのテスト"""

        # カスタム軸の作成
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # 基本的な荷重-変位プロットをカスタマイズ
        plot_load_displacement(
            load_displacement_data,
            ax=ax1,
            color="blue",
            marker="o",
            linestyle="-",
            linewidth=1.5,
            alpha=0.7,
            label="Experimental Data",
        )
        ax1.set_title("Custom Load-Displacement Plot")
        ax1.grid(True, linestyle="--", alpha=0.5)

        # 異なる範囲設定での降伏点計算
        custom_result = find_yield_point(
            load_displacement_data,
            method="offset",
            offset_value=0.001,
            range_start=0.2,
            range_end=0.4,
        )

        # カスタマイズされた降伏点プロット
        plot_yield_analysis_details(
            custom_result, ax=ax2, color="green", marker="s", linestyle="-."
        )
        ax2.set_title("Custom Yield Analysis")

        # 図を保存
        custom_plot_path = Path(self.temp_dir) / "custom_plot.png"
        fig.tight_layout()
        fig.savefig(custom_plot_path)
        plt.close(fig)

        # ファイルが作成されたことを確認
        assert custom_plot_path.exists()
        assert custom_plot_path.stat().st_size > 0

    def test_integration_example(self, load_displacement_data):
        """実用的なデータ解析フローの統合テスト"""

        # 3つの異なる降伏点定義でデータを解析
        offset_small = find_yield_point(
            load_displacement_data,
            method="offset",
            offset_value=0.001,
            result_prefix="yield_small",
        )

        offset_standard = find_yield_point(
            load_displacement_data,
            method="offset",
            offset_value=0.002,
            result_prefix="yield_standard",
        )

        general = find_yield_point(
            load_displacement_data,
            method="general",
            factor=0.33,
            result_prefix="yield_general",
        )

        # 降伏解析結果の詳細を取得
        small_yield_data = offset_small.metadata["analysis"]["yield_point"]
        standard_yield_data = offset_standard.metadata["analysis"]["yield_point"]
        general_yield_data = general.metadata["analysis"]["yield_point"]

        # 結果の比較
        small_yield_load = small_yield_data["load"]
        standard_yield_load = standard_yield_data["load"]
        general_yield_load = general_yield_data["load"]

        # オフセット値が増えると降伏荷重も増えるはず
        assert small_yield_load <= standard_yield_load

        # 2x2の図を作成してサブプロット
        fig, axs = plt.subplots(2, 2, figsize=(12, 10))

        # 基本プロットと各降伏点解析の表示
        plot_load_displacement(load_displacement_data, ax=axs[0, 0])
        axs[0, 0].set_title("Raw Load-Displacement Data")

        plot_yield_analysis_details(offset_small, ax=axs[0, 1])
        axs[0, 1].set_title("Offset Method (0.1% Strain)")

        plot_yield_analysis_details(offset_standard, ax=axs[1, 0])
        axs[1, 0].set_title("Offset Method (0.2% Strain)")

        plot_yield_analysis_details(general, ax=axs[1, 1])
        axs[1, 1].set_title("General Yield Method (33% Slope)")

        # 全体タイトルの設定
        fig.suptitle("Comparison of Different Yield Point Definitions", fontsize=16)
        fig.tight_layout(rect=[0, 0, 1, 0.96])  # suptitleのスペースを確保

        # 図を保存
        integration_plot_path = Path(self.temp_dir) / "integration_example.png"
        fig.savefig(integration_plot_path)
        plt.close(fig)

        # 結果のサマリデータフレームを保存
        results_path = Path(self.temp_dir) / "yield_results.csv"
        with open(results_path, "w") as f:
            f.write(
                "Method,Offset/Factor,Yield Load (kN),Yield Displacement (mm),Initial Slope (kN/mm)\n"
            )
            f.write(
                f"Offset,0.001,{small_yield_data['load']:.2f},{small_yield_data['displacement']:.4f},{small_yield_data['initial_slope']:.2f}\n"
            )
            f.write(
                f"Offset,0.002,{standard_yield_data['load']:.2f},{standard_yield_data['displacement']:.4f},{standard_yield_data['initial_slope']:.2f}\n"
            )
            f.write(
                f"General,0.33,{general_yield_data['load']:.2f},{general_yield_data['displacement']:.4f},{general_yield_data['initial_slope']:.2f}\n"
            )

        # ファイルが作成されたことを確認
        assert integration_plot_path.exists()
        assert results_path.exists()

        # ファイルサイズを確認
        assert integration_plot_path.stat().st_size > 0
        assert results_path.stat().st_size > 0


def test_visual_inspection(load_displacement_data):
    """手動視覚確認用のテスト（CIではスキップ）

    このテストはCIでは自動的にスキップされ、手動でのみ実行されることを想定
    """
    # CI環境変数が設定されている場合はスキップ
    if "CI" in os.environ:
        pytest.skip("CI環境では視覚確認テストをスキップ")

    # 降伏点解析の実行
    offset_result = find_yield_point(
        load_displacement_data, method="offset", offset_value=0.002
    )

    # 複数の手法の比較
    methods = [
        {
            "method": "offset",
            "offset_value": 0.001,
            "result_prefix": "yield_offset_small",
        },
        {
            "method": "offset",
            "offset_value": 0.002,
            "result_prefix": "yield_offset_std",
        },
        {
            "method": "offset",
            "offset_value": 0.005,
            "result_prefix": "yield_offset_large",
        },
        {"method": "general", "factor": 0.33, "result_prefix": "yield_general"},
    ]

    # プロット表示
    fig, ax = compare_yield_methods(load_displacement_data, methods=methods)
    plt.show()  # 手動実行時のみ表示される

    # 詳細解析プロット
    fig2, ax2 = plot_yield_analysis_details(offset_result)
    plt.show()  # 手動実行時のみ表示される
