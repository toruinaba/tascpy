import pytest
from src.tascpy.core.row import Row

class TestRow:
    """Rowクラスのテスト"""

    def test_row_access(self):
        """Rowオブジェクトへのアクセスをテスト"""
        row = Row(step=1, values={"A": 10, "B": 20})
        
        # 属性アクセス
        assert row.step == 1
        assert row.values == {"A": 10, "B": 20}
        
        # __getitem__アクセス
        assert row["step"] == 1
        assert row["A"] == 10
        assert row["B"] == 20
        
        # 存在しないキーへのアクセス
        with pytest.raises(KeyError):
            _ = row["C"]

    def test_row_iteration(self):
        """Rowオブジェクトの反復処理をテスト"""
        row = Row(step=1, values={"A": 10, "B": 20})
        
        # 辞書化して検証
        data = dict(row)
        assert data["step"] == 1
        assert data["A"] == 10
        assert data["B"] == 20
        
        # キーの存在確認
        assert "step" in data
        assert "A" in data
        assert "B" in data

    def test_to_dict(self):
        """to_dictメソッドのテスト"""
        row = Row(step=1, values={"A": 10, "B": 20})
        data = row.to_dict()
        
        assert isinstance(data, dict)
        assert data["step"] == 1
        assert data["A"] == 10
        assert data["B"] == 20
