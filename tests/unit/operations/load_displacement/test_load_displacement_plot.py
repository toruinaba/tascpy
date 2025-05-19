"""荷重-変位ドメインのプロット関数のテスト"""

import pytest
import numpy as np

# テスト実行時にGUIウィンドウが表示されないよう、Aggバックエンドを使用
import matplotlib

matplotlib.use("Agg")  # テスト用の非表示バックエンド設定
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.collections import PathCollection

from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
from tascpy.domains.load_displacement import LoadDisplacementCollection
from tascpy.operations.load_displacement.plot import (
    plot_load_displacement,
    plot_yield_point,
    plot_yield_analysis_details,
    compare_yield_methods,
    plot_skeleton_curve,
    plot_cumulative_curve,
)
from tascpy.operations.load_displacement.analysis import find_yield_point
from tascpy.operations.load_displacement.curves import (
    create_skeleton_curve,
    create_cumulative_curve,
)


@pytest.fixture
def sample_load_displacement_data():
    """テスト用の荷重-変位データを作成"""
    # より細かい間隔でサンプルポイントを作成して、10%～30%の荷重範囲にデータを確保
    displacement = np.linspace(0, 10, 200)  # サンプル数を増やす

    # 荷重データ（より現実的な非線形挙動を作成）
    load = np.zeros_like(displacement)

    # 最初の部分は線形（初期勾配）
    initial_slope = 10.0
    elastic_range = 70  # データポイントの数
    load[:elastic_range] = initial_slope * displacement[:elastic_range]

    # 非線形部分（降伏後）
    post_yield_slope = 2.0
    transition_len = 30  # 遷移部分の長さ

    # 遷移部分（なめらかに勾配が変化）
    for i in range(transition_len):
        idx = elastic_range + i
        ratio = i / transition_len
        current_slope = initial_slope * (1 - ratio) + post_yield_slope * ratio
        load[idx] = load[elastic_range - 1] + current_slope * (
            displacement[idx] - displacement[elastic_range - 1]
        )

    # 完全な塑性域
    plastic_start = elastic_range + transition_len
    load[plastic_start:] = load[plastic_start - 1] + post_yield_slope * (
        displacement[plastic_start:] - displacement[plastic_start - 1]
    )

    # コレクション作成
    collection = ColumnCollection(
        step=list(range(len(displacement))),
        columns={"displacement": displacement, "load": load},
    )

    # 単位情報を追加
    collection.columns["displacement"].unit = "mm"
    collection.columns["load"].unit = "kN"

    # LoadDisplacementCollectionに変換
    ld_collection = collection.ops.as_domain(
        "load_displacement", load_column="load", displacement_column="displacement"
    ).end()

    return ld_collection


@pytest.fixture
def sample_with_yield_point(sample_load_displacement_data):
    """降伏点情報を含むサンプルデータ"""
    # オフセット法で降伏点を計算
    result = find_yield_point(
        sample_load_displacement_data, method="offset", offset_value=0.002
    )
    return result


@pytest.fixture
def sample_with_cyclic_data():
    """サイクル荷重-変位データを作成"""
    steps = list(range(15))
    loads = [0, 10, 20, 10, 0, -10, -20, -10, 0, 15, 30, 15, 0, -15, -30]
    displacements = [0, 1, 2, 1, 0, -1, -2, -1, 0, 1.5, 3, 1.5, 0, -1.5, -3]
    cycles = [1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4]

    # コレクション作成
    collection = ColumnCollection(
        steps, {"load": loads, "displacement": displacements, "cycle": cycles}
    )

    # 単位情報を追加
    collection.columns["displacement"].unit = "mm"
    collection.columns["load"].unit = "kN"

    # LoadDisplacementCollectionに変換
    ld_collection = collection.ops.as_domain(
        "load_displacement", load_column="load", displacement_column="displacement"
    ).end()

    return ld_collection


@pytest.fixture
def sample_with_skeleton_curve_columns(sample_with_cyclic_data):
    """スケルトン曲線データを列に含むサンプル（旧形式）"""
    result = create_skeleton_curve(sample_with_cyclic_data, store_as_columns=True)
    return result


@pytest.fixture
def sample_with_skeleton_curve_metadata(sample_with_cyclic_data):
    """スケルトン曲線データをメタデータに含むサンプル（新形式）"""
    result = create_skeleton_curve(sample_with_cyclic_data, store_as_columns=False)
    return result


@pytest.fixture
def sample_with_cumulative_curve_columns(sample_with_cyclic_data):
    """累積曲線データを列に含むサンプル（旧形式）"""
    result = create_cumulative_curve(sample_with_cyclic_data, store_as_columns=True)
    return result


@pytest.fixture
def sample_with_cumulative_curve_metadata(sample_with_cyclic_data):
    """累積曲線データをメタデータに含むサンプル（新形式）"""
    result = create_cumulative_curve(sample_with_cyclic_data, store_as_columns=False)
    return result


class TestPlotLoadDisplacement:
    """plot_load_displacement関数のテスト"""

    def test_basic_plot(self, sample_load_displacement_data):
        """基本的なプロット機能のテスト"""
        # 関数の戻り値は LoadDisplacementCollection のみ
        result_collection = plot_load_displacement(sample_load_displacement_data)

        # 現在のaxとfigureを取得
        fig = plt.gcf()
        ax = plt.gca()

        assert isinstance(fig, Figure)
        assert isinstance(ax, Axes)
        assert ax.get_xlabel() == "displacement [mm]"
        assert ax.get_ylabel() == "load [kN]"

        # プロットされたラインが1つあるか確認
        assert len(ax.lines) == 1

        plt.close(fig)

    def test_custom_axis(self, sample_load_displacement_data):
        """カスタム軸へのプロット機能のテスト"""
        custom_fig, custom_ax = plt.subplots()
        result_collection = plot_load_displacement(
            sample_load_displacement_data, ax=custom_ax
        )

        fig = custom_ax.figure
        ax = custom_ax

        assert fig is custom_fig
        assert ax is custom_ax

        plt.close(fig)

    def test_with_kwargs(self, sample_load_displacement_data):
        """追加のキーワード引数が適用されるかのテスト"""
        result_collection = plot_load_displacement(
            sample_load_displacement_data,
            color="red",
            linestyle="--",
            marker="o",
            label="Test Data",
        )

        # 現在のaxを取得
        fig = plt.gcf()
        ax = plt.gca()

        line = ax.lines[0]
        assert line.get_color() == "red"
        assert line.get_linestyle() == "--"
        assert line.get_marker() == "o"
        assert line.get_label() == "Test Data"

        plt.close(fig)


class TestPlotSkeletonCurve:
    """plot_skeleton_curve関数のテスト"""

    def test_skeleton_curve_from_columns(self, sample_with_skeleton_curve_columns):
        """列からスケルトン曲線をプロットするテスト（旧形式）"""
        result_collection = plot_skeleton_curve(sample_with_skeleton_curve_columns)

        # 現在のaxとfigureを取得
        fig = plt.gcf()
        ax = plt.gca()

        assert isinstance(fig, Figure)
        assert isinstance(ax, Axes)

        # 元データとスケルトン曲線の2つのラインがあるか確認
        assert len(ax.lines) == 2

        # 軸ラベルが正しく設定されているか確認
        assert "displacement" in ax.get_xlabel().lower()
        assert "load" in ax.get_ylabel().lower()

        # タイトルと凡例が設定されているか確認
        assert "Skeleton Curve" in ax.get_title()
        assert ax.get_legend() is not None

        plt.close(fig)

    def test_skeleton_curve_from_metadata(self, sample_with_skeleton_curve_metadata):
        """メタデータからスケルトン曲線をプロットするテスト（新形式）"""
        result_collection = plot_skeleton_curve(sample_with_skeleton_curve_metadata)

        # 現在のaxとfigureを取得
        fig = plt.gcf()
        ax = plt.gca()

        assert isinstance(fig, Figure)
        assert isinstance(ax, Axes)

        # 元データとスケルトン曲線の2つのラインがあるか確認
        assert len(ax.lines) == 2

        # スケルトン曲線のラインが正しく設定されているか
        skeleton_line = [
            line for line in ax.lines if line.get_label() == "Skeleton Curve"
        ][0]
        assert skeleton_line.get_color() == "red"
        assert skeleton_line.get_linewidth() == 2

        plt.close(fig)

    def test_skeleton_curve_without_original(self, sample_with_skeleton_curve_metadata):
        """元データなしでスケルトン曲線のみをプロットするテスト"""
        result_collection = plot_skeleton_curve(
            sample_with_skeleton_curve_metadata, plot_original=False
        )

        # 現在のaxとfigureを取得
        fig = plt.gcf()
        ax = plt.gca()

        # スケルトン曲線のみが存在するはず
        assert len(ax.lines) == 1

        plt.close(fig)

    def test_skeleton_curve_custom_style(self, sample_with_skeleton_curve_metadata):
        """カスタムスタイルでスケルトン曲線をプロットするテスト"""
        skeleton_kwargs = {
            "color": "blue",
            "linestyle": "--",
            "linewidth": 3,
            "label": "Custom Skeleton",
        }

        result_collection = plot_skeleton_curve(
            sample_with_skeleton_curve_metadata, skeleton_kwargs=skeleton_kwargs
        )

        # 現在のaxとfigureを取得
        fig = plt.gcf()
        ax = plt.gca()

        # カスタムスタイルが適用されているか確認
        skeleton_line = [
            line for line in ax.lines if line.get_label() == "Custom Skeleton"
        ][0]
        assert skeleton_line.get_color() == "blue"
        assert skeleton_line.get_linestyle() == "--"
        assert skeleton_line.get_linewidth() == 3

        plt.close(fig)


class TestPlotCumulativeCurve:
    """plot_cumulative_curve関数のテスト"""

    def test_cumulative_curve_from_columns(self, sample_with_cumulative_curve_columns):
        """列から累積曲線をプロットするテスト（旧形式）"""
        result_collection = plot_cumulative_curve(sample_with_cumulative_curve_columns)

        # 現在のaxとfigureを取得
        fig = plt.gcf()
        ax = plt.gca()

        assert isinstance(fig, Figure)
        assert isinstance(ax, Axes)

        # 元データと累積曲線の2つのラインがあるか確認
        assert len(ax.lines) == 2

        # 軸ラベルが正しく設定されているか確認
        assert "displacement" in ax.get_xlabel().lower()
        assert "load" in ax.get_ylabel().lower()

        # タイトルと凡例が設定されているか確認
        assert "Cumulative Curve" in ax.get_title()
        assert ax.get_legend() is not None

        plt.close(fig)

    def test_cumulative_curve_from_metadata(
        self, sample_with_cumulative_curve_metadata
    ):
        """メタデータから累積曲線をプロットするテスト（新形式）"""
        result_collection = plot_cumulative_curve(sample_with_cumulative_curve_metadata)

        # 現在のaxとfigureを取得
        fig = plt.gcf()
        ax = plt.gca()

        assert isinstance(fig, Figure)
        assert isinstance(ax, Axes)

        # 元データと累積曲線の2つのラインがあるか確認
        assert len(ax.lines) == 2

        # 累積曲線のラインが正しく設定されているか
        cumulative_line = [
            line for line in ax.lines if line.get_label() == "Cumulative Curve"
        ][0]
        assert cumulative_line.get_color() == "blue"
        assert cumulative_line.get_linewidth() == 2

        plt.close(fig)

    def test_cumulative_curve_without_original(
        self, sample_with_cumulative_curve_metadata
    ):
        """元データなしで累積曲線のみをプロットするテスト"""
        result_collection = plot_cumulative_curve(
            sample_with_cumulative_curve_metadata, plot_original=False
        )

        # 現在のaxとfigureを取得
        fig = plt.gcf()
        ax = plt.gca()

        # 累積曲線のみが存在するはず
        assert len(ax.lines) == 1

        plt.close(fig)

    def test_cumulative_curve_custom_style(self, sample_with_cumulative_curve_metadata):
        """カスタムスタイルで累積曲線をプロットするテスト"""
        cumulative_kwargs = {
            "color": "green",
            "linestyle": "-.",
            "linewidth": 3,
            "label": "Custom Cumulative",
        }

        result_collection = plot_cumulative_curve(
            sample_with_cumulative_curve_metadata, cumulative_kwargs=cumulative_kwargs
        )

        # 現在のaxとfigureを取得
        fig = plt.gcf()
        ax = plt.gca()

        # カスタムスタイルが適用されているか確認
        cumulative_line = [
            line for line in ax.lines if line.get_label() == "Custom Cumulative"
        ][0]
        assert cumulative_line.get_color() == "green"
        assert cumulative_line.get_linestyle() == "-."
        assert cumulative_line.get_linewidth() == 3

        plt.close(fig)


class TestPlotYieldPoint:
    """plot_yield_point関数のテスト"""

    def test_yield_point_visualization(self, sample_with_yield_point):
        """降伏点の可視化テスト"""
        result_collection = plot_yield_point(sample_with_yield_point)

        # 現在のaxとfigureを取得
        fig = plt.gcf()
        ax = plt.gca()

        # 基本的なグラフ要素の確認
        assert isinstance(fig, Figure)
        assert isinstance(ax, Axes)

        # 荷重変位曲線、初期勾配線、オフセット線、降伏点がプロットされているか確認
        assert len(ax.lines) >= 2  # 少なくとも元データと初期勾配線がある

        # 降伏点（散布図）が正しくプロットされているか
        scatter_points = [c for c in ax.collections if isinstance(c, PathCollection)]
        assert len(scatter_points) > 0

        plt.close(fig)

    def test_without_original_data(self, sample_with_yield_point):
        """元データをプロットせずに降伏点のみ表示するテスト"""
        result_collection = plot_yield_point(
            sample_with_yield_point, plot_original_data=False
        )

        # 現在のaxとfigureを取得
        fig = plt.gcf()
        ax = plt.gca()

        # 元データのラインがないことを確認（初期勾配線とオフセット線のみ）
        assert (
            len(
                [
                    line
                    for line in ax.lines
                    if line.get_label() == "Load-Displacement Data"
                ]
            )
            == 0
        )

        plt.close(fig)

    def test_general_yield_method(self, sample_load_displacement_data):
        """一般降伏法による降伏点表示のテスト"""
        # 一般降伏法で降伏点を計算
        general_result = find_yield_point(
            sample_load_displacement_data, method="general", factor=0.33
        )

        result_collection = plot_yield_point(general_result)

        # 現在のaxとfigureを取得
        fig = plt.gcf()
        ax = plt.gca()

        # 接線が表示されているか確認
        tangent_lines = [
            line
            for line in ax.lines
            if line.get_linestyle() == "--" and line.get_color() == "m"
        ]
        assert len(tangent_lines) == 1

        plt.close(fig)


class TestPlotYieldAnalysisDetails:
    """plot_yield_analysis_details関数のテスト"""

    def test_analysis_details(self, sample_with_yield_point):
        """降伏点解析詳細表示のテスト"""
        result_collection = plot_yield_analysis_details(sample_with_yield_point)

        # 現在のaxとfigureを取得
        fig = plt.gcf()
        ax = plt.gca()

        # 初期勾配計算に使用した範囲のハイライトがあるか確認
        # 多くの点が存在することを確認（シアン色の点のチェックは省略）
        scatter_collections = [
            c for c in ax.collections if isinstance(c, PathCollection)
        ]
        assert (
            len(scatter_collections) >= 2
        )  # 少なくとも2つの散布図（降伏点と初期勾配計算範囲）があるはず

        # テキスト情報が表示されているか確認
        texts = ax.texts
        assert len(texts) > 0
        text_content = texts[0].get_text()
        assert "Yield Point:" in text_content
        assert "Displacement:" in text_content
        assert "Load:" in text_content

        plt.close(fig)

    def test_error_without_yield_data(self, sample_load_displacement_data):
        """降伏点情報がない場合のエラーテスト"""
        with pytest.raises(
            ValueError, match="コレクションに降伏点の解析結果が含まれていません"
        ):
            plot_yield_analysis_details(sample_load_displacement_data)


class TestCompareYieldMethods:
    """compare_yield_methods関数のテスト"""

    def test_methods_comparison(self, sample_load_displacement_data):
        """複数の降伏点計算手法の比較テスト"""
        methods = [
            {
                "method": "offset",
                "offset_value": 0.002,
                "result_prefix": "yield_offset_small",
            },
            {
                "method": "offset",
                "offset_value": 0.005,
                "result_prefix": "yield_offset_large",
            },
            {"method": "general", "factor": 0.33, "result_prefix": "yield_general"},
        ]

        result_collection = compare_yield_methods(
            sample_load_displacement_data, methods=methods
        )

        # 現在のaxとfigureを取得
        fig = plt.gcf()
        ax = plt.gca()

        # 3つの降伏点（散布図）がプロットされているか確認
        scatter_points = [c for c in ax.collections if isinstance(c, PathCollection)]
        assert len(scatter_points) >= 3

        # 凡例に各メソッドが表示されているか確認
        legend = ax.get_legend()
        assert legend is not None
        legend_texts = [text.get_text() for text in legend.get_texts()]
        assert any("Offset" in text for text in legend_texts)
        assert any("General" in text for text in legend_texts)

        plt.close(fig)

    def test_default_methods(self, sample_load_displacement_data):
        """デフォルトメソッドを使用したテスト"""
        result_collection = compare_yield_methods(sample_load_displacement_data)

        # 現在のaxとfigureを取得
        fig = plt.gcf()
        ax = plt.gca()

        # デフォルトで2つの降伏点がプロットされるはず
        scatter_points = [c for c in ax.collections if isinstance(c, PathCollection)]
        assert len(scatter_points) >= 2

        plt.close(fig)
