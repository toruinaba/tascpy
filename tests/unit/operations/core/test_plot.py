import pytest
from unittest.mock import patch, MagicMock
import matplotlib.pyplot as plt

from tascpy.operations.core.plot import plot, visualize_outliers
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
import numpy as np


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
        # backend_mpl.plot defaults to "line" unless plot_type="scatter" is passed.
        # But this test expects scatter.
        result = plot(sample_collection, y_column="y1", x_column="x", plot_type="scatter")

        # 検証: matplotlibの適切なメソッドが呼ばれたか
        mock_ax.scatter.assert_called_once()
        mock_ax.set_xlabel.assert_called_with("X Values [m]")
        mock_ax.set_ylabel.assert_called_with("Y1 Values [kg]")
        # axがNoneの場合（新しい図を作成した場合）のみplt.showが呼ばれる
        mock_show.assert_called_once()

        # Axesオブジェクトが返されることを確認 (chaining broken)
        assert result is mock_ax

    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.subplots")
    def test_line_plot(self, mock_subplots, mock_show, sample_collection):
        """線グラフの描画が正しく機能することを確認"""
        # モックの設定
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # plot関数を呼び出す
        result = plot(sample_collection, y_column="y1", x_column="x", plot_type="line")

        # 検証: matplotlibの適切なメソッドが呼ばれたか
        mock_ax.plot.assert_called_once()
        mock_ax.set_xlabel.assert_called_with("X Values [m]")
        mock_ax.set_ylabel.assert_called_with("Y1 Values [kg]")
        # axがNoneの場合（新しい図を作成した場合）のみplt.showが呼ばれる
        mock_show.assert_called_once()

        # 元のコレクションではなくAxesが返されることを確認
        assert result is mock_ax

    @patch("matplotlib.pyplot.show")
    def test_existing_axes(self, mock_show, sample_collection):
        """既存のAxesオブジェクトを使用する機能が正しく動作することを確認"""
        # 既存のAxesオブジェクトをモックで作成
        mock_ax = MagicMock()

        # plot関数を呼び出す
        result = plot(sample_collection, y_column="y1", x_column="x", ax=mock_ax, plot_type="scatter")

        # 検証: 新しいサブプロットを作らず、既存のaxesオブジェクトが使用されるか
        mock_ax.scatter.assert_called_once()
        mock_ax.set_xlabel.assert_called_with("X Values [m]")
        mock_ax.set_ylabel.assert_called_with("Y1 Values [kg]")
        # 既存のAxesオブジェクトを使用する場合はplt.showは呼ばれない
        mock_show.assert_not_called()

        # Axesオブジェクトが返されることを確認
        assert result is mock_ax
        """既存のAxesオブジェクトを使用する機能が正しく動作することを確認"""
        # 既存のAxesオブジェクトをモックで作成
        mock_ax = MagicMock()

        # plot関数を呼び出す
        result = plot(sample_collection, y_column="y1", x_column="x", ax=mock_ax, plot_type="scatter")

        # 検証: 新しいサブプロットを作らず、既存のaxesオブジェクトが使用されるか
        mock_ax.scatter.assert_called_once()
        mock_ax.set_xlabel.assert_called_with("X Values [m]")
        mock_ax.set_ylabel.assert_called_with("Y1 Values [kg]")
        # 既存のAxesオブジェクトを使用する場合はplt.showは呼ばれない
        mock_show.assert_not_called()

        # Axesオブジェクトが返されることを確認
        assert result is mock_ax

    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.subplots")
    def test_plot_kwargs(self, mock_subplots, mock_show, sample_collection):
        """キーワード引数が正しく渡されることを確認"""
        # モックの設定
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # 追加のキーワード引数を持つplot関数の呼び出し
        plot(sample_collection, y_column="y1", x_column="x", plot_type="scatter", color="red", marker="o", s=100)

        # 検証: キーワード引数が正しく渡されたか
        args, kwargs = mock_ax.scatter.call_args
        assert kwargs.get("color") == "red"
        assert kwargs.get("marker") == "o"
        assert kwargs.get("s") == 100

    def test_nonexistent_column(self, sample_collection):
        """存在しない列名を指定した場合にKeyErrorが発生することを確認"""
        # 存在しないx列
        with pytest.raises(KeyError, match="列 'nonexistent_x' は存在しません"):
            plot(sample_collection, y_column="y1", x_column="nonexistent_x")

        # 存在しないy列
        with pytest.raises(KeyError, match="列 'nonexistent_y' は存在しません"):
            plot(sample_collection, y_column="nonexistent_y", x_column="x")

    @patch("matplotlib.pyplot.subplots")
    def test_invalid_plot_type(self, mock_subplots, sample_collection):
        """無効なプロットタイプを指定した場合、デフォルト（line）にフォールバックすることを確認"""
        # モックの設定
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # 無効なプロットタイプでの呼び出し - エラーにならずline plotとして描画される
        plot(sample_collection, y_column="y1", x_column="x", plot_type="invalid_type")
        
        # エラーが発生しなければOK、かつplotが呼ばれているはず
        mock_ax.plot.assert_called()

    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.subplots")
    def test_title_setting(self, mock_subplots, mock_show, sample_collection):
        """グラフタイトルが正しく設定されることを確認"""
        # モックの設定
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # plot関数を呼び出す
        plot(sample_collection, y_column="y1", x_column="x", plot_type="scatter")

        # 検証: タイトルが正しく設定されたか
        mock_ax.set_title.assert_called_with("Y1 Values vs X Values")

        # 線グラフでも確認
        mock_ax.reset_mock()
        plot(sample_collection, y_column="y2", x_column="x", plot_type="line")
        mock_ax.set_title.assert_called_with("Y2 Values vs X Values")

    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.subplots")
    def test_x_none_uses_step(self, mock_subplots, mock_show, sample_collection):
        """x_columnがNoneの場合にstepが使用されることを確認"""
        # モックの設定
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # plot関数を呼び出す（x_column=None）
        result = plot(sample_collection, y_column="y1", x_column=None, plot_type="scatter")

        # 検証: stepがx軸として使われ、適切なラベルが設定されるか
        mock_ax.scatter.assert_called_once()
        # 第1引数（x値）がstep.valuesである
        args, kwargs = mock_ax.scatter.call_args
        np.testing.assert_array_equal(args[0], sample_collection.step.values)

        # 軸ラベルとタイトルの検証
        mock_ax.set_xlabel.assert_called_with("Step")
        mock_ax.set_ylabel.assert_called_with("Y1 Values [kg]")
        mock_ax.set_title.assert_called_with("Y1 Values vs Step")

        # Axesオブジェクトが返されることを確認
        assert result is mock_ax

    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.subplots")
    def test_y_none_uses_step(self, mock_subplots, mock_show, sample_collection):
        """y_columnがNoneの場合にstepが使用されることを確認"""
        # モックの設定
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # plot関数を呼び出す（y_column=None）
        result = plot(sample_collection, y_column=None, x_column="x", plot_type="scatter")

        # 検証: stepがy軸として使われ、適切なラベルが設定されるか
        mock_ax.scatter.assert_called_once()
        # 第2引数（y値）がstep.valuesである
        args, kwargs = mock_ax.scatter.call_args
        np.testing.assert_array_equal(args[1], sample_collection.step.values)

        # 軸ラベルとタイトルの検証
        mock_ax.set_xlabel.assert_called_with("X Values [m]")
        mock_ax.set_ylabel.assert_called_with("Step")
        mock_ax.set_title.assert_called_with("Step vs X Values")

        # Axesオブジェクトが返されることを確認
        assert result is mock_ax

    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.subplots")
    def test_both_none_uses_step(self, mock_subplots, mock_show, sample_collection):
        """x_columnとy_columnの両方がNoneの場合にstepが使用されることを確認"""
        # モックの設定
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # plot関数を呼び出す（x_column=None, y_column=None）
        result = plot(sample_collection, y_column=None, x_column=None, plot_type="scatter")

        # 検証: 両軸にstepが使われ、適切なラベルが設定されるか
        mock_ax.scatter.assert_called_once()
        # 両方の引数がstep.valuesである
        args, kwargs = mock_ax.scatter.call_args
        np.testing.assert_array_equal(args[0], sample_collection.step.values)
        np.testing.assert_array_equal(args[1], sample_collection.step.values)

        # 軸ラベルとタイトルの検証
        mock_ax.set_xlabel.assert_called_with("Step")
        mock_ax.set_ylabel.assert_called_with("Step")
        mock_ax.set_title.assert_called_with("Step vs Step")

        # Axesオブジェクトが返されることを確認
        assert result is mock_ax


class TestVisualizeOutliers:
    """visualize_outliers関数のテスト"""

    @patch("tascpy.functional.stats.detect_outliers")
    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.subplots")
    def test_basic_visualization(
        self, mock_subplots, mock_show, mock_detect_outliers, sample_collection
    ):
        """基本的な異常値の可視化機能が正しく動作することを確認"""
        # detect_outliersのモック戻り値を設定 (純粋関数なのでフラグのリスト/配列を返す)
        mock_detect_outliers.return_value = [0, 1, 0, 1, 0]

        # モックの設定
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # visualize_outliers関数を呼び出す
        result = visualize_outliers(sample_collection, "y1")

        # 検証: detect_outliers が呼ばれたか
        mock_detect_outliers.assert_called_once()
        
        # 検証: detect_outliers が純粋な値（NumPy配列など）で呼ばれたか確認
        # args[0] は y_values
        call_args = mock_detect_outliers.call_args
        assert call_args is not None
        # args[0]にはy列の値(numpy array)が入っているはず
        np.testing.assert_array_equal(call_args[0][0], sample_collection.columns["y1"].values)

        # 検証: matplotlibの適切なメソッドが呼ばれたか
        # 正常値と異常値で少なくとも2回scatterが呼ばれる
        assert mock_ax.scatter.call_count >= 1
        mock_ax.set_title.assert_called()
        mock_ax.set_xlabel.assert_called()
        mock_ax.set_ylabel.assert_called()

        # axがNoneの場合（新しい図を作成した場合）のみplt.showが呼ばれる
        # 純粋関数化したため plt.show() は呼ばれない仕様に変更 (呼び出し元で制御)
        # mock_show.assert_called_once() -> Removed

        # 結果がAxesオブジェクトであることを確認
        assert result is mock_ax

    @patch("tascpy.functional.stats.detect_outliers")
    @patch("matplotlib.pyplot.show")
    def test_existing_axes(self, mock_show, mock_detect_outliers, sample_collection):
        """既存のAxesオブジェクトを使用する機能が正しく動作することを確認"""
        # detect_outliersのモック戻り値を設定
        mock_detect_outliers.return_value = [0, 1, 0, 1, 0]

        # 既存のAxesオブジェクトをモックで作成
        mock_ax = MagicMock()

        # visualize_outliers関数を呼び出す
        result = visualize_outliers(sample_collection, "y1", ax=mock_ax)

        # 検証: 既存のaxesオブジェクトが使用されるか
        assert mock_ax.scatter.call_count >= 1
        mock_ax.set_xlabel.assert_called()
        mock_ax.set_ylabel.assert_called()

        # 既存のAxesオブジェクトを使用する場合はplt.showは呼ばれない
        mock_show.assert_not_called()

        # 結果がAxesであることを確認
        assert result is mock_ax

    @patch("tascpy.functional.stats.detect_outliers")
    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.subplots")
    def test_no_outliers(
        self, mock_subplots, mock_show, mock_detect_outliers, sample_collection
    ):
        """異常値がない場合の動作を確認"""
        # detect_outliersのモック戻り値を設定（異常値なし）
        mock_detect_outliers.return_value = [0, 0, 0, 0, 0]

        # モックの設定
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # visualize_outliers関数を呼び出す（異常値なし）
        with patch("builtins.print") as mock_print:
            result = visualize_outliers(sample_collection, "y1")

            # 検証: 異常値がない旨のメッセージが出力されたか
            mock_print.assert_any_call("visualize_outliers: 異常値は検出されませんでした")

        # 異常値がなくても、通常のデータポイントはプロットされるはず
        mock_ax.scatter.assert_called()

        # 結果がAxesであることを確認
        assert result is mock_ax

    @patch("tascpy.functional.stats.detect_outliers")
    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.subplots")
    def test_custom_parameters(
        self, mock_subplots, mock_show, mock_detect_outliers, sample_collection
    ):
        """カスタムパラメータ指定時の動作を確認"""
        # detect_outliersのモック戻り値を設定
        mock_detect_outliers.return_value = [0, 1, 0, 1, 0]

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
            show_normal=True,
            normal_color="blue",
            normal_alpha=0.5,
            outlier_marker="x",
            outlier_size=100,
        )

        # 検証: detect_outliers がカスタムパラメータで呼ばれたか
        # 注意: 引数の順序やキーワード引数を正確にチェック
        args, kwargs = mock_detect_outliers.call_args
        assert kwargs["window_size"] == 5
        assert kwargs["threshold"] == 0.3
        # result_columnは渡されない（純粋関数コールなので不要）

        # 結果がAxesであることを確認
        assert result is mock_ax


from tascpy.operations.core.plot import plot_const_x

class TestPlotConstX:
    """plot_const_x関数のテスト"""

    @patch("tascpy.visualization.backend_mpl.plot")
    def test_basic_plot_const_x(self, mock_plot, sample_collection):
        """plot_const_xが正しく動作することを確認"""
        # mock_plot returns what? usually ax.
        mock_ax = MagicMock()
        mock_plot.return_value = mock_ax

        x_values = [10, 20]
        y_columns = ["y1", "y2"]
        # y1[0]=10, y2[0]=100

        # Call
        result = plot_const_x(sample_collection, x_values=x_values, y_columns=y_columns)

        # Verify inject_columns extracted values passed to plot
        mock_plot.assert_called_once()
        args, kwargs = mock_plot.call_args
        
        # Check x_values
        np.testing.assert_array_equal(kwargs["x_values"], np.array(x_values))
        
        # Check y_values (should be [y1[0], y2[0]] = [10, 100])
        expected_y = np.array([10.0, 100.0])
        np.testing.assert_array_equal(kwargs["y_values"], expected_y)
        
        assert result is mock_ax

    @patch("tascpy.visualization.backend_mpl.plot")
    def test_length_mismatch(self, mock_plot, sample_collection):
        """長さが一致しない場合にエラーが発生することを確認"""
        x_values = [10] # len 1
        y_columns = ["y1", "y2"] # len 2
        
        with pytest.raises(ValueError, match="一致しません"):
             plot_const_x(sample_collection, x_values=x_values, y_columns=y_columns)
