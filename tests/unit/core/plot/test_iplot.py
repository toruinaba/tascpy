
import pytest
from unittest.mock import patch, MagicMock
import numpy as np
from tascpy.core.collection import ColumnCollection
from tascpy.core.column import Column

@pytest.fixture
def sample_collection():
    """テスト用のColumnCollectionフィクスチャ"""
    return ColumnCollection(
        step=[1, 2, 3, 4, 5],
        columns={
            "x": Column("x", [1, 2, 3, 4, 5], unit="m", ch="1"),
            "y1": Column("y1", [10, 20, 30, 40, 50], unit="kg", ch="2"),
        },
        metadata={"description": "Test Collection for IPlot"},
    )

class TestIPlot:
    """iplot関数のテスト"""

    @patch("tascpy.core.plot.plotly_backend.plot")
    def test_basic_iplot(self, mock_plotly_plot, sample_collection):
        """基本的なiplot呼び出しがbackend_plotly.plotに正しく委譲されることを確認"""
        # モックの戻り値設定
        mock_fig = MagicMock()
        mock_plotly_plot.return_value = mock_fig
        
        # iplot呼び出し
        result = sample_collection.plot.iplot(y_column="y1", x_column="x")
        
        # 検証
        mock_plotly_plot.assert_called_once()
        args, kwargs = mock_plotly_plot.call_args
        
        # 引数の検証 (@inject_plot_dataが機能しているか)
        assert "x_values" in kwargs
        assert "y_values" in kwargs
        assert "x_label" in kwargs
        assert "y_label" in kwargs
        assert "title" in kwargs
        
        np.testing.assert_array_equal(kwargs["x_values"], sample_collection["x"].values)
        np.testing.assert_array_equal(kwargs["y_values"], sample_collection["y1"].values)
        assert kwargs["x_label"] == "x [m]"
        assert kwargs["y_label"] == "y1 [kg]"
        assert kwargs["title"] == "y1 vs x"
        
        # 戻り値の検証
        assert result is mock_fig

    @patch("tascpy.core.plot.plotly_backend.plot")
    def test_iplot_kwargs(self, mock_plotly_plot, sample_collection):
        """キーワード引数がbackend_plotly.plotに渡されることを確認"""
        sample_collection.plot.iplot(y_column="y1", x_column="x", plot_type="line", color="red")
        
        args, kwargs = mock_plotly_plot.call_args
        assert kwargs.get("plot_type") == "line"
        assert kwargs.get("color") == "red"

    @patch("tascpy.core.plot.plotly_backend.plot")
    def test_iplot_name_extraction(self, mock_plotly_plot, sample_collection):
        """name引数またはy_labelからnameが抽出されることを確認"""
        # 1. 自動抽出 (y1 [kg] -> y1)
        # Note: functional_plot may extract name, but here we just check if it gets passed.
        # functional_plot.iplot extracts name from y_label if not provided. This is in functional layer.
        sample_collection.plot.iplot(y_column="y1", x_column="x")
        args, kwargs = mock_plotly_plot.call_args
        assert kwargs.get("name") == "y1"
        
        # 2. 明示的指定
        sample_collection.plot.iplot(y_column="y1", x_column="x", name="Custom Name")
        args, kwargs = mock_plotly_plot.call_args
        assert kwargs.get("name") == "Custom Name"


def test_plotter_iplot_argument_order_matches_plot():
    pytest.importorskip("plotly")
    from tascpy.core.collection import ColumnCollection

    coll = ColumnCollection({"P": [0.0, 1.0], "d": [0.0, 2.0]}, units={"P": "kN", "d": "mm"})
    fig = coll.plot.iplot("P", "d")
    assert list(fig.data[0].y) == [0.0, 1.0]
    assert fig.layout.xaxis.title.text == "d [mm]"
    assert coll.plot.iplot("P").layout.xaxis.title.text == "Step"
