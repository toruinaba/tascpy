import pytest
from unittest.mock import patch, MagicMock
import matplotlib.pyplot as plt

from tascpy.operations.core.plot import plot, visualize_outliers
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column


@pytest.fixture
def sample_collection():
    """テスト用のColumnCollectionフィクスチャ"""
    return ColumnCollection(
        step=[1, 2, 3, 4, 5],
        columns={
            "x": Column("1", "X Values", "m", [1, 2, 3, 4, 5]),
            "y1": Column("2", "Y1 Values", "kg", [10, 20, 30, 40, 50]),
            "y2": Column("3", "Y2 Values", "N", [100, 200, 300, 400, 500]),
        },
        metadata={"description": "Test Collection for Plot"},
    )


class TestPlot:
    """plot関数のテスト"""

    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.subplots")
    def test_scatter_plot(self, mock_subplots, mock_show, sample_collection):
        """散布図の描画が正しく機能することを確認"""
        # モックの設定
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # plot関数を呼び出す
        result = plot(sample_collection, "x", "y1")

        # 検証: matplotlibの適切なメソッドが呼ばれたか
        mock_ax.scatter.assert_called_once()
        mock_ax.set_xlabel.assert_called_with("X Values [m]")
        mock_ax.set_ylabel.assert_called_with("Y1 Values [kg]")
        # axがNoneの場合（新しい図を作成した場合）のみplt.showが呼ばれる
        mock_show.assert_called_once()

        # 元のコレクションが返されることを確認
        assert result is sample_collection

    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.subplots")
    def test_line_plot(self, mock_subplots, mock_show, sample_collection):
        """線グラフの描画が正しく機能することを確認"""
        # モックの設定
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # plot関数を呼び出す
        result = plot(sample_collection, "x", "y1", plot_type="line")

        # 検証: matplotlibの適切なメソッドが呼ばれたか
        mock_ax.plot.assert_called_once()
        mock_ax.set_xlabel.assert_called_with("X Values [m]")
        mock_ax.set_ylabel.assert_called_with("Y1 Values [kg]")
        # axがNoneの場合（新しい図を作成した場合）のみplt.showが呼ばれる
        mock_show.assert_called_once()

        # 元のコレクションが返されることを確認
        assert result is sample_collection

    @patch("matplotlib.pyplot.show")
    def test_existing_axes(self, mock_show, sample_collection):
        """既存のAxesオブジェクトを使用する機能が正しく動作することを確認"""
        # 既存のAxesオブジェクトをモックで作成
        mock_ax = MagicMock()

        # plot関数を呼び出す
        result = plot(sample_collection, "x", "y1", ax=mock_ax)

        # 検証: 新しいサブプロットを作らず、既存のaxesオブジェクトが使用されるか
        mock_ax.scatter.assert_called_once()
        mock_ax.set_xlabel.assert_called_with("X Values [m]")
        mock_ax.set_ylabel.assert_called_with("Y1 Values [kg]")
        # 既存のAxesオブジェクトを使用する場合はplt.showは呼ばれない
        mock_show.assert_not_called()

        # 元のコレクションが返されることを確認
        assert result is sample_collection

    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.subplots")
    def test_plot_kwargs(self, mock_subplots, mock_show, sample_collection):
        """キーワード引数が正しく渡されることを確認"""
        # モックの設定
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # 追加のキーワード引数を持つplot関数の呼び出し
        plot(sample_collection, "x", "y1", color="red", marker="o", s=100)

        # 検証: キーワード引数が正しく渡されたか
        args, kwargs = mock_ax.scatter.call_args
        assert kwargs.get("color") == "red"
        assert kwargs.get("marker") == "o"
        assert kwargs.get("s") == 100

    def test_nonexistent_column(self, sample_collection):
        """存在しない列名を指定した場合にKeyErrorが発生することを確認"""
        # 存在しないx列
        with pytest.raises(KeyError, match="列 'nonexistent_x' は存在しません"):
            plot(sample_collection, "nonexistent_x", "y1")

        # 存在しないy列
        with pytest.raises(KeyError, match="列 'nonexistent_y' は存在しません"):
            plot(sample_collection, "x", "nonexistent_y")

    @patch("matplotlib.pyplot.subplots")
    def test_invalid_plot_type(self, mock_subplots, sample_collection):
        """無効なプロットタイプを指定した場合にValueErrorが発生することを確認"""
        # モックの設定
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # 無効なプロットタイプでの呼び出し
        with pytest.raises(
            ValueError,
            match="plot_type は 'scatter' または 'line' のいずれかである必要があります",
        ):
            plot(sample_collection, "x", "y1", plot_type="invalid_type")

    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.subplots")
    def test_title_setting(self, mock_subplots, mock_show, sample_collection):
        """グラフタイトルが正しく設定されることを確認"""
        # モックの設定
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # plot関数を呼び出す
        plot(sample_collection, "x", "y1", plot_type="scatter")

        # 検証: タイトルが正しく設定されたか
        mock_ax.set_title.assert_called_with("Scatter plot of Y1 Values vs X Values")

        # 線グラフでも確認
        mock_ax.reset_mock()
        plot(sample_collection, "x", "y2", plot_type="line")
        mock_ax.set_title.assert_called_with("Line plot of Y2 Values vs X Values")

    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.subplots")
    def test_x_none_uses_step(self, mock_subplots, mock_show, sample_collection):
        """x_columnがNoneの場合にstepが使用されることを確認"""
        # モックの設定
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # plot関数を呼び出す（x_column=None）
        result = plot(sample_collection, None, "y1")

        # 検証: stepがx軸として使われ、適切なラベルが設定されるか
        mock_ax.scatter.assert_called_once()
        # 第1引数（x値）がstep.valuesである
        args, kwargs = mock_ax.scatter.call_args
        assert args[0] is sample_collection.step.values

        # 軸ラベルとタイトルの検証
        mock_ax.set_xlabel.assert_called_with("Step")
        mock_ax.set_ylabel.assert_called_with("Y1 Values [kg]")
        mock_ax.set_title.assert_called_with("Scatter plot of Y1 Values vs Step")

        # 元のコレクションが返されることを確認
        assert result is sample_collection

    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.subplots")
    def test_y_none_uses_step(self, mock_subplots, mock_show, sample_collection):
        """y_columnがNoneの場合にstepが使用されることを確認"""
        # モックの設定
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # plot関数を呼び出す（y_column=None）
        result = plot(sample_collection, "x", None)

        # 検証: stepがy軸として使われ、適切なラベルが設定されるか
        mock_ax.scatter.assert_called_once()
        # 第2引数（y値）がstep.valuesである
        args, kwargs = mock_ax.scatter.call_args
        assert args[1] is sample_collection.step.values

        # 軸ラベルとタイトルの検証
        mock_ax.set_xlabel.assert_called_with("X Values [m]")
        mock_ax.set_ylabel.assert_called_with("Step")
        mock_ax.set_title.assert_called_with("Scatter plot of Step vs X Values")

        # 元のコレクションが返されることを確認
        assert result is sample_collection

    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.subplots")
    def test_both_none_uses_step(self, mock_subplots, mock_show, sample_collection):
        """x_columnとy_columnの両方がNoneの場合にstepが使用されることを確認"""
        # モックの設定
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # plot関数を呼び出す（x_column=None, y_column=None）
        result = plot(sample_collection, None, None)

        # 検証: 両軸にstepが使われ、適切なラベルが設定されるか
        mock_ax.scatter.assert_called_once()
        # 両方の引数がstep.valuesである
        args, kwargs = mock_ax.scatter.call_args
        assert args[0] is sample_collection.step.values
        assert args[1] is sample_collection.step.values

        # 軸ラベルとタイトルの検証
        mock_ax.set_xlabel.assert_called_with("Step")
        mock_ax.set_ylabel.assert_called_with("Step")
        mock_ax.set_title.assert_called_with("Scatter plot of Step vs Step")

        # 元のコレクションが返されることを確認
        assert result is sample_collection


class TestVisualizeOutliers:
    """visualize_outliers関数のテスト"""

    @patch("tascpy.operations.core.stats.detect_outliers")
    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.subplots")
    def test_basic_visualization(
        self, mock_subplots, mock_show, mock_detect_outliers, sample_collection
    ):
        """基本的な異常値の可視化機能が正しく動作することを確認"""
        # detect_outliersのモック戻り値を設定
        mock_outlier_collection = sample_collection.clone()
        mock_outlier_collection.columns["_outlier_flags_y1"] = Column(
            "outlier", "Outlier Flags", "", [0, 1, 0, 1, 0]
        )
        mock_detect_outliers.return_value = mock_outlier_collection

        # モックの設定
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # visualize_outliers関数を呼び出す
        result = visualize_outliers(sample_collection, "y1")

        # 検証: detect_outliers が呼ばれたか
        mock_detect_outliers.assert_called_once()

        # 検証: matplotlibの適切なメソッドが呼ばれたか
        mock_ax.scatter.assert_called()  # 複数回呼ばれる可能性があるため、exact=Falseを使わない
        mock_ax.set_title.assert_called()
        mock_ax.set_xlabel.assert_called()
        mock_ax.set_ylabel.assert_called()

        # axがNoneの場合（新しい図を作成した場合）のみplt.showが呼ばれる
        mock_show.assert_called_once()

        # 結果がdetect_outliers関数から返されたコレクションであることを確認
        assert result is mock_outlier_collection

    @patch("tascpy.operations.core.stats.detect_outliers")
    @patch("matplotlib.pyplot.show")
    def test_existing_axes(self, mock_show, mock_detect_outliers, sample_collection):
        """既存のAxesオブジェクトを使用する機能が正しく動作することを確認"""
        # detect_outliersのモック戻り値を設定
        mock_outlier_collection = sample_collection.clone()
        mock_outlier_collection.columns["_outlier_flags_y1"] = Column(
            "outlier", "Outlier Flags", "", [0, 1, 0, 1, 0]
        )
        mock_detect_outliers.return_value = mock_outlier_collection

        # 既存のAxesオブジェクトをモックで作成
        mock_ax = MagicMock()

        # visualize_outliers関数を呼び出す
        result = visualize_outliers(sample_collection, "y1", ax=mock_ax)

        # 検証: 既存のaxesオブジェクトが使用されるか
        mock_ax.scatter.assert_called()
        mock_ax.set_xlabel.assert_called()
        mock_ax.set_ylabel.assert_called()

        # 既存のAxesオブジェクトを使用する場合はplt.showは呼ばれない
        mock_show.assert_not_called()

        # 結果がdetect_outliers関数から返されたコレクションであることを確認
        assert result is mock_outlier_collection

    @patch("tascpy.operations.core.stats.detect_outliers")
    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.subplots")
    def test_no_outliers(
        self, mock_subplots, mock_show, mock_detect_outliers, sample_collection
    ):
        """異常値がない場合の動作を確認"""
        # detect_outliersのモック戻り値を設定（異常値なし）
        mock_outlier_collection = sample_collection.clone()
        mock_outlier_collection.columns["_outlier_flags_y1"] = Column(
            "outlier", "Outlier Flags", "", [0, 0, 0, 0, 0]
        )
        mock_detect_outliers.return_value = mock_outlier_collection

        # モックの設定
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # visualize_outliers関数を呼び出す（異常値なし）
        with patch("builtins.print") as mock_print:
            result = visualize_outliers(sample_collection, "y1")

            # 検証: 異常値がない旨のメッセージが出力されたか
            mock_print.assert_any_call("visualize_outliers: 異常値がありません")

        # 異常値がなくても、通常のデータポイントはプロットされるはず
        mock_ax.scatter.assert_called()

        # axがNoneの場合（新しい図を作成した場合）のみplt.showが呼ばれる
        mock_show.assert_called_once()

    @patch("tascpy.operations.core.stats.detect_outliers")
    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.subplots")
    def test_custom_parameters(
        self, mock_subplots, mock_show, mock_detect_outliers, sample_collection
    ):
        """カスタムパラメータ指定時の動作を確認"""
        # detect_outliersのモック戻り値を設定
        mock_outlier_collection = sample_collection.clone()
        mock_outlier_collection.columns["_outlier_flags_y1"] = Column(
            "outlier", "Outlier Flags", "", [0, 1, 0, 1, 0]
        )
        mock_detect_outliers.return_value = mock_outlier_collection

        # モックの設定
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # カスタムパラメータを指定してvisualize_outliers関数を呼び出す
        result = visualize_outliers(
            sample_collection,
            "y1",
            window_size=5,
            threshold=0.3,
            highlight_color="red",
            plot_type="line",
            show_normal=True,
            normal_color="blue",
            normal_alpha=0.5,
            outlier_marker="x",
            outlier_size=100,
        )

        # 検証: detect_outliers がカスタムパラメータで呼ばれたか
        mock_detect_outliers.assert_called_with(
            sample_collection,
            column="y1",
            window_size=5,
            threshold=0.3,
            result_column="_outlier_flags_y1",
            edge_handling="asymmetric",
            min_abs_value=1e-10,
            scale_factor=1.0,
        )

        # axがNoneの場合（新しい図を作成した場合）のみplt.showが呼ばれる
        mock_show.assert_called_once()
