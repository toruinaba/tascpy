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
from tascpy.domains import as_load_displacement


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
        {"displacement": displacement, "load": load},
        step=list(range(len(displacement))),
        units={"displacement": "mm", "load": "kN"},
    )

    # LoadDisplacementCollectionに変換
    ld_collection = collection.ops.as_domain(as_load_displacement, "load", "displacement").end()

    return ld_collection


@pytest.fixture
def offset_yield_point(sample_load_displacement_data):
    """オフセット法で求めた降伏点"""
    return sample_load_displacement_data.ops.yield_point(method="offset", offset_value=0.002)


@pytest.fixture
def sample_with_cyclic_data():
    """サイクル荷重-変位データを作成"""
    steps = list(range(15))
    loads = [0, 10, 20, 10, 0, -10, -20, -10, 0, 15, 30, 15, 0, -15, -30]
    displacements = [0, 1, 2, 1, 0, -1, -2, -1, 0, 1.5, 3, 1.5, 0, -1.5, -3]
    cycles = [1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4]

    # コレクション作成
    collection = ColumnCollection(
        {"load": loads, "displacement": displacements, "cycle": cycles},
        step=steps,
        units={"displacement": "mm", "load": "kN"},
    )

    # LoadDisplacementCollectionに変換
    ld_collection = collection.ops.as_domain(as_load_displacement, "load", "displacement").end()

    return ld_collection


class TestPlotLoadDisplacement:
    """plot_load_displacement関数のテスト"""

    def test_basic_plot(self, sample_load_displacement_data):
        """基本的なプロット機能のテスト"""
        # 関数の戻り値は LoadDisplacementCollection のみ
        result_collection = sample_load_displacement_data.plot.plot_load_displacement()

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
        result_collection = sample_load_displacement_data.plot.plot_load_displacement(ax=custom_ax)

        fig = custom_ax.figure
        ax = custom_ax

        assert fig is custom_fig
        assert ax is custom_ax

        plt.close(fig)

    def test_with_kwargs(self, sample_load_displacement_data):
        """追加のキーワード引数が適用されるかのテスト"""
        result_collection = sample_load_displacement_data.plot.plot_load_displacement(
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

    def test_overlay_skeleton_curve(self, sample_with_cyclic_data):
        """スケルトン曲線のコレクションを元データと同じ Axes に重ねて描画できる"""
        skeleton = sample_with_cyclic_data.ops.to_skeleton_curve(cycle_column="cycle").end()
        ax = sample_with_cyclic_data.plot.plot_load_displacement(label="original")
        skeleton.plot.plot_load_displacement(ax=ax, label="skeleton", color="red")

        assert [line.get_label() for line in ax.lines] == ["original", "skeleton"]
        np.testing.assert_array_equal(ax.lines[1].get_ydata(), skeleton.load_data)
        assert ax.get_xlabel() == "displacement [mm]"

        plt.close(ax.figure)


class TestPlotYieldPoint:
    """plot_yield_point関数のテスト"""

    def test_yield_point_visualization(self, sample_load_displacement_data, offset_yield_point):
        """降伏点の可視化テスト"""
        sample_load_displacement_data.plot.plot_yield_point(offset_yield_point)

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

    def test_without_original_data(self, sample_load_displacement_data, offset_yield_point):
        """元データをプロットせずに降伏点のみ表示するテスト"""
        sample_load_displacement_data.plot.plot_yield_point(offset_yield_point, plot_original_data=False)

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
        general_point = sample_load_displacement_data.ops.yield_point(method="general", factor=0.33)

        sample_load_displacement_data.plot.plot_yield_point(general_point)

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

    def test_analysis_details(self, sample_load_displacement_data, offset_yield_point):
        """降伏点解析詳細表示のテスト"""
        sample_load_displacement_data.plot.plot_yield_analysis_details(offset_yield_point)

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


class TestCompareYieldPoints:
    """compare_yield_points関数のテスト"""

    def test_methods_comparison(self, sample_load_displacement_data):
        """複数の降伏点計算手法の比較テスト"""
        ops = sample_load_displacement_data.ops
        points = [
            ops.yield_point(method="offset", offset_value=0.002),
            ops.yield_point(method="offset", offset_value=0.005),
            ops.yield_point(method="general", factor=0.33),
        ]

        sample_load_displacement_data.plot.compare_yield_points(points)

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
