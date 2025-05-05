import pytest
from unittest.mock import patch, MagicMock
import matplotlib.pyplot as plt

from src.tascpy.operations.core.plot import plot
from src.tascpy.core.collection import ColumnCollection
from src.tascpy.core.column import Column


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

    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.subplots')
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
        mock_show.assert_called_once()
        
        # 元のコレクションが返されることを確認
        assert result is sample_collection

    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.subplots')
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
        mock_show.assert_called_once()
        
        # 元のコレクションが返されることを確認
        assert result is sample_collection
    
    @patch('matplotlib.pyplot.show')
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
        mock_show.assert_called_once()
        
        # 元のコレクションが返されることを確認
        assert result is sample_collection
    
    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.subplots')
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
    
    @patch('matplotlib.pyplot.subplots')
    def test_invalid_plot_type(self, mock_subplots, sample_collection):
        """無効なプロットタイプを指定した場合にValueErrorが発生することを確認"""
        # モックの設定
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)
        
        # 無効なプロットタイプでの呼び出し
        with pytest.raises(ValueError, match="plot_type は 'scatter' または 'line' のいずれかである必要があります"):
            plot(sample_collection, "x", "y1", plot_type="invalid_type")

    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.subplots')
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
        
    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.subplots')
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
        
    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.subplots')
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
        
    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.subplots')
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