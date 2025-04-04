import pytest
import codecs
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from src.tascpy.io import Reader


class TestReader:
    def test_init_with_str(self):
        """Test Reader initialization with string path"""
        reader = Reader("test_path.txt")
        assert isinstance(reader.path, Path)
        assert str(reader.path) == "test_path.txt"

    def test_init_with_path(self):
        """Test Reader initialization with Path object"""
        path = Path("test_path.txt")
        reader = Reader(path)
        assert reader.path == path

    def test_init_with_invalid_type(self):
        """Test Reader initialization with invalid type"""
        with pytest.raises(ValueError, match="ファイルパスはpathlibオブジェクトまたはstrで指定してください."):
            Reader(123)

    @patch('codecs.open')
    def test_enter(self, mock_codecs_open):
        """Test __enter__ method"""
        mock_file = MagicMock()
        mock_codecs_open.return_value = mock_file
        
        reader = Reader("test_path.txt")
        result = reader.__enter__()
        
        mock_codecs_open.assert_called_once_with(Path("test_path.txt"), "r", "shift-jis")
        assert reader.io == mock_file
        assert result == reader

    @patch('codecs.open')
    def test_exit_without_exception(self, mock_codecs_open):
        """Test __exit__ method without exception"""
        mock_file = MagicMock()
        mock_codecs_open.return_value = mock_file
        
        reader = Reader("test_path.txt")
        reader.__enter__()
        reader.__exit__(None, None, None)
        
        mock_file.close.assert_called_once()

    @patch('codecs.open')
    @patch('builtins.print')
    def test_exit_with_exception(self, mock_print, mock_codecs_open):
        """Test __exit__ method with exception"""
        mock_file = MagicMock()
        mock_codecs_open.return_value = mock_file
        
        reader = Reader("test_path.txt")
        reader.__enter__()
        
        exc_type = ValueError
        reader.__exit__(exc_type, None, None)
        
        mock_file.close.assert_called_once()
        mock_print.assert_called_once_with(exc_type)

    @patch('codecs.open')
    def test_context_manager(self, mock_codecs_open):
        """Test Reader as context manager"""
        mock_file = MagicMock()
        mock_codecs_open.return_value = mock_file
        
        with Reader("test_path.txt") as reader:
            assert reader.io == mock_file
        
        mock_file.close.assert_called_once()
