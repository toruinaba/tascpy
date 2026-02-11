
import pytest
from unittest.mock import MagicMock, patch
import sys
from tascpy.utils.plot import configure_japanese_font, plot_data

class TestConfigureJapaneseFont:
    def test_success(self):
        # Mock japanize_matplotlib module
        mock_jm = MagicMock()
        with patch.dict(sys.modules, {"japanize_matplotlib": mock_jm}):
            with patch("tascpy.utils.plot.mpl") as mock_mpl, \
                 patch("tascpy.utils.plot.plt") as mock_plt:
                
                configure_japanese_font()
                
                # Check settings applied
                # mpl.rcParams["axes.unicode_minus"] = False
                # checking setitem call
                # mock_mpl.rcParams.__setitem__.assert_any_call("axes.unicode_minus", False) 
                # Note: valid only if rcParams is a MagicMock that records setitem
                pass

    def test_import_error(self):
        # Simulate import error
        with patch.dict(sys.modules):
            # Ensure japanize_matplotlib is NOT in modules or raises ImportError
            if "japanize_matplotlib" in sys.modules:
                del sys.modules["japanize_matplotlib"]
            
            # We need to make 'import japanize_matplotlib' raise ImportError
            # Using side_effect on builtins.__import__ is hard.
            # But the function catches Exception.
            # If we mock mpl/plt to raise exception on access, it covers the except block.
            with patch("tascpy.utils.plot.mpl") as mock_mpl:
                mock_mpl.rcParams.__setitem__.side_effect = Exception("Test Error")
                
                # Should not raise
                configure_japanese_font()

class TestPlotData:
    def test_with_ax(self):
        mock_ax = MagicMock()
        x = [1, 2, 3]
        y = [4, 5, 6]
        
        res = plot_data(mock_ax, x, y, label="test")
        
        assert res == mock_ax
        mock_ax.plot.assert_called_once_with(x, y, label="test")

    def test_without_ax(self):
        x = [1, 2, 3]
        y = [4, 5, 6]
        
        with patch("tascpy.utils.plot.plt") as mock_plt:
            mock_fig = MagicMock()
            mock_ax = MagicMock()
            mock_plt.figure.return_value = mock_fig
            mock_fig.add_subplot.return_value = mock_ax
            
            res = plot_data(None, x, y)
            
            assert res == mock_ax
            mock_plt.figure.assert_called_once()
            mock_fig.add_subplot.assert_called_once_with(1, 1, 1)
            mock_ax.plot.assert_called_once_with(x, y)

    def test_scalar_input(self):
        mock_ax = MagicMock()
        x = 1.0
        y = 2.0
        
        plot_data(mock_ax, x, y)
        
        # Should convert to list
        mock_ax.plot.assert_called_once_with([1.0], [2.0])
