import pytest
from unittest.mock import patch, MagicMock
import matplotlib.pyplot as plt

from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column
import numpy as np


@pytest.fixture
def sample_collection():
    """テスト用のColumnCollectionフィクスチャ"""
    return ColumnCollection(
        step=[1, 2, 3, 4, 5],
        columns={
            "x": Column("x", [1, 2, 3, 4, 5], unit="m", ch="1"),
            "y1": Column("y1", [10, 20, 30, 40, 50], unit="kg", ch="2"),
            "y2": Column("y2", [100, 200, 300, 400, 500], unit="N", ch="3"),
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
        result = sample_collection.plot.plot(y_column="y1", x_column="x", plot_type="scatter")

        # 検証: matplotlibの適切なメソッドが呼ばれたか
        mock_ax.scatter.assert_called_once()
        mock_ax.set_xlabel.assert_called_with("x [m]")
        mock_ax.set_ylabel.assert_called_with("y1 [kg]")
        # 図の表示は呼び出し側で行う（新しい図を作成しても plt.show は呼ばない）
        mock_show.assert_not_called()

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
        result = sample_collection.plot.plot(y_column="y1", x_column="x", plot_type="line")

        # 検証: matplotlibの適切なメソッドが呼ばれたか
        mock_ax.plot.assert_called_once()
        mock_ax.set_xlabel.assert_called_with("x [m]")
        mock_ax.set_ylabel.assert_called_with("y1 [kg]")
        # 図の表示は呼び出し側で行う（新しい図を作成しても plt.show は呼ばない）
        mock_show.assert_not_called()

        # 元のコレクションではなくAxesが返されることを確認
        assert result is mock_ax

    @patch("matplotlib.pyplot.show")
    def test_existing_axes(self, mock_show, sample_collection):
        """既存のAxesオブジェクトを使用する機能が正しく動作することを確認"""
        # 既存のAxesオブジェクトをモックで作成
        mock_ax = MagicMock()

        # plot関数を呼び出す
        result = sample_collection.plot.plot(y_column="y1", x_column="x", ax=mock_ax, plot_type="scatter")

        # 検証: 新しいサブプロットを作らず、既存のaxesオブジェクトが使用されるか
        mock_ax.scatter.assert_called_once()
        mock_ax.set_xlabel.assert_called_with("x [m]")
        mock_ax.set_ylabel.assert_called_with("y1 [kg]")
        # 既存のAxesオブジェクトを使用する場合はplt.showは呼ばれない
        mock_show.assert_not_called()

        # Axesオブジェクトが返されることを確認
        assert result is mock_ax
        mock_ax.set_ylabel.assert_called_with("y1 [kg]")
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
        sample_collection.plot.plot(y_column="y1", x_column="x", plot_type="scatter", color="red", marker="o", s=100)

        # 検証: キーワード引数が正しく渡されたか
        args, kwargs = mock_ax.scatter.call_args
        assert kwargs.get("color") == "red"
        assert kwargs.get("marker") == "o"
        assert kwargs.get("s") == 100

    def test_nonexistent_column(self, sample_collection):
        """存在しない列名を指定した場合にKeyErrorが発生することを確認"""
        # 存在しないx列
        with pytest.raises(KeyError, match="列 'nonexistent_x' が存在しません"):
            sample_collection.plot.plot(y_column="y1", x_column="nonexistent_x")

        # 存在しないy列
        with pytest.raises(KeyError, match="列 'nonexistent_y' が存在しません"):
            sample_collection.plot.plot(y_column="nonexistent_y", x_column="x")

    def test_invalid_plot_type(self, sample_collection):
        """無効な plot_type は ValueError"""
        with pytest.raises(ValueError, match="plot_type"):
            sample_collection.plot.plot(y_column="y1", x_column="x", plot_type="invalid_type")

    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.subplots")
    def test_title_setting(self, mock_subplots, mock_show, sample_collection):
        """グラフタイトルが正しく設定されることを確認"""
        # モックの設定
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # plot関数を呼び出す
        sample_collection.plot.plot(y_column="y1", x_column="x", plot_type="scatter")

        # 検証: タイトルが正しく設定されたか
        mock_ax.set_title.assert_called_with("y1 vs x")

        # 線グラフでも確認
        mock_ax.reset_mock()
        sample_collection.plot.plot(y_column="y2", x_column="x", plot_type="line")
        mock_ax.set_title.assert_called_with("y2 vs x")

    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.pyplot.subplots")
    def test_x_none_uses_step(self, mock_subplots, mock_show, sample_collection):
        """x_columnがNoneの場合にstepが使用されることを確認"""
        # モックの設定
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # plot関数を呼び出す（x_column=None）
        result = sample_collection.plot.plot(y_column="y1", x_column=None, plot_type="scatter")

        # 検証: stepがx軸として使われ、適切なラベルが設定されるか
        mock_ax.scatter.assert_called_once()
        # 第1引数（x値）がstep.valuesである
        args, kwargs = mock_ax.scatter.call_args
        np.testing.assert_array_equal(args[0], sample_collection.step)

        # 軸ラベルとタイトルの検証
        mock_ax.set_xlabel.assert_called_with("Step")
        mock_ax.set_ylabel.assert_called_with("y1 [kg]")
        mock_ax.set_title.assert_called_with("y1 vs Step")

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
        result = sample_collection.plot.plot(y_column=None, x_column="x", plot_type="scatter")

        # 検証: stepがy軸として使われ、適切なラベルが設定されるか
        mock_ax.scatter.assert_called_once()
        # 第2引数（y値）がstep.valuesである
        args, kwargs = mock_ax.scatter.call_args
        np.testing.assert_array_equal(args[1], sample_collection.step)

        # 軸ラベルとタイトルの検証
        mock_ax.set_xlabel.assert_called_with("x [m]")
        mock_ax.set_ylabel.assert_called_with("Step")
        mock_ax.set_title.assert_called_with("Step vs x")

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
        result = sample_collection.plot.plot(y_column=None, x_column=None, plot_type="scatter")

        # 検証: 両軸にstepが使われ、適切なラベルが設定されるか
        mock_ax.scatter.assert_called_once()
        # 両方の引数がstep.valuesである
        args, kwargs = mock_ax.scatter.call_args
        np.testing.assert_array_equal(args[0], sample_collection.step)
        np.testing.assert_array_equal(args[1], sample_collection.step)

        # 軸ラベルとタイトルの検証
        mock_ax.set_xlabel.assert_called_with("Step")
        mock_ax.set_ylabel.assert_called_with("Step")
        mock_ax.set_title.assert_called_with("Step vs Step")

        # Axesオブジェクトが返されることを確認
        assert result is mock_ax


class TestPlotOutliers:
    """plot_outliers: 外れ値フラグの列に基づいて色分けして描画する（判定は ops 側で行う）"""

    @staticmethod
    def _flagged(collection, flags):
        return collection.with_column("flag", flags, unit="")

    @patch("matplotlib.pyplot.subplots")
    def test_basic_visualization(self, mock_subplots, sample_collection):
        mock_ax = MagicMock()
        mock_subplots.return_value = (MagicMock(), mock_ax)
        flagged = self._flagged(sample_collection, [0, 1, 0, 1, 0])
        result = flagged.plot.plot_outliers("y1", flags_column="flag")
        assert result is mock_ax
        assert mock_ax.scatter.call_count >= 1
        mock_ax.set_title.assert_called_with("異常値検出: y1 (検出数: 2個)")
        mock_ax.set_xlabel.assert_called()
        mock_ax.set_ylabel.assert_called()

    def test_does_not_detect_outliers_itself(self, sample_collection):
        with patch("tascpy.numeric.stats.detect_outliers") as mock_detect:
            self._flagged(sample_collection, [0, 0, 0, 0, 0]).plot.plot_outliers("y1", flags_column="flag", ax=MagicMock())
        mock_detect.assert_not_called()

    @patch("matplotlib.pyplot.subplots")
    def test_no_outliers(self, mock_subplots, sample_collection):
        mock_ax = MagicMock()
        mock_subplots.return_value = (MagicMock(), mock_ax)
        with patch("builtins.print") as mock_print:
            self._flagged(sample_collection, [0, 0, 0, 0, 0]).plot.plot_outliers("y1", flags_column="flag")
            mock_print.assert_not_called()
        mock_ax.set_title.assert_called_with("異常値検出: y1 (検出数: 0個)")
        mock_ax.scatter.assert_called()

    def test_flags_from_detect_outliers(self, sample_collection):
        flagged = sample_collection.ops.detect_outliers("y1", result_column="flag").end()
        mock_ax = MagicMock()
        assert flagged.plot.plot_outliers("y1", flags_column="flag", ax=mock_ax, highlight_color="red") is mock_ax

    def test_missing_flags_column(self, sample_collection):
        with pytest.raises(KeyError):
            sample_collection.plot.plot_outliers("y1", flags_column="flag")


class TestPlotConstX:
    """plot_const_x: 指定した行の各列の値を、列ごとの位置に並べて描画する"""

    def test_basic_plot_const_x(self, sample_collection):
        ax = sample_collection.plot.plot_const_x(x_values=[10, 20], y_columns=["y1", "y2"])
        line = ax.lines[0]
        np.testing.assert_array_equal(line.get_xdata(), [10.0, 20.0])
        np.testing.assert_array_equal(line.get_ydata(), [10.0, 100.0])  # 先頭行
        assert ax.get_ylabel() == "Value"  # 単位が異なる (kg, N) ので単位なし
        plt.close(ax.figure)

    def test_row_and_common_unit(self, sample_collection):
        coll = sample_collection.with_meta("y2", unit="kg")
        ax = coll.plot.plot_const_x(x_values=[10, 20], y_columns=["y1", "y2"], row=-1, x_label="Position [mm]")
        np.testing.assert_array_equal(ax.lines[0].get_ydata(), [50.0, 500.0])
        assert ax.get_ylabel() == "Value [kg]"
        assert ax.get_xlabel() == "Position [mm]"
        assert ax.get_title() == "Value at step 5"
        plt.close(ax.figure)

    def test_length_mismatch_and_row_range(self, sample_collection):
        with pytest.raises(ValueError, match="一致しません"):
            sample_collection.plot.plot_const_x(x_values=[10], y_columns=["y1", "y2"])
        with pytest.raises(IndexError):
            sample_collection.plot.plot_const_x(x_values=[10], y_columns=["y1"], row=5)
