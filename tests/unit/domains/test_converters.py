import pytest
from datetime import datetime, timedelta
import numpy as np
from src.tascpy.core.collection import ColumnCollection
from src.tascpy.core.column import Column
from src.tascpy.core.step import Step
from src.tascpy.domains.converters import _prepare_for_timeseries, _prepare_for_load_displacement, _prepare_for_signal

class TestDomainConverters:
    """ドメイン変換ヘルパー関数のテスト"""

    @pytest.fixture
    def basic_collection(self):
        return ColumnCollection(
            step=[0, 1, 2],
            columns={
                "val": Column("1", "val", "unit", [1.0, 2.0, 3.0]),
                "other": Column("2", "other", "unit", [4.0, 5.0, 6.0])
            }
        )

    def test_prepare_for_timeseries_custom_frequency(self, basic_collection):
        """時系列変換時のカスタム頻度解析テスト"""
        start_date = datetime(2023, 1, 1)
        
        # 2時間ごとのデータ
        kwargs = _prepare_for_timeseries(
            basic_collection, 
            start_date=start_date, 
            frequency="2H"
        )
        
        assert isinstance(basic_collection.step.values[0], datetime)
        assert basic_collection.step.values[1] == start_date + timedelta(hours=2)
        assert basic_collection.step.values[2] == start_date + timedelta(hours=4)

        # 30分ごとのデータ (リセットしてテスト)
        basic_collection.step = Step(values=[0, 1, 2])
        kwargs = _prepare_for_timeseries(
            basic_collection, 
            start_date=start_date, 
            frequency="30min"
        ) # "min" is not in standard processing but handled by regex fallback logic usually?
          # checking regex implementation: r"(\d+)([DHMSdhms])" -> "min" matches "m" if implemented correctly or might fail
          # The regex in code is: r"(\d+)([DHMSdhms])"
          # "30min" -> group 1="30", group 2="m" (re.match matches from beginning)
        
        # Check actual logic in converters.py
        # match = re.match(r"(\d+)([DHMSdhms])", freq)
        # "30min" matches "30m"
        
        assert basic_collection.step.values[1] == start_date + timedelta(minutes=30)
        
    def test_prepare_for_load_displacement_guessing(self):
        """荷重-変位カラムの自動推定テスト"""
        # ケース1: 名前で推定
        c1 = ColumnCollection(
            step=[1],
            columns={
                "Force [N]": Column("1", "Force", "N", [1.0]),
                "Displacement [mm]": Column("2", "Disp", "mm", [0.1]),
                "Temp": Column("3", "Temp", "C", [25.0])
            }
        )
        kwargs = _prepare_for_load_displacement(c1)
        assert kwargs["load_column"] == "Force [N]"
        assert kwargs["displacement_column"] == "Displacement [mm]"

        # ケース2: 名前が不明確だが数値カラムが2つある場合
        c2 = ColumnCollection(
            step=[1],
            columns={
                "ColA": Column("1", "A", "", [1.0]), # 数値
                "ColB": Column("2", "B", "", [0.1]), # 数値
                "ColC": Column("3", "C", "", ["str"]) # 文字列
            }
        )
        kwargs = _prepare_for_load_displacement(c2)
        assert kwargs["load_column"] == "ColA" # 最初の数値カラム
        assert kwargs["displacement_column"] == "ColB" # 2番目の数値カラム

        # ケース3: 特定できない場合のエラー
        c3 = ColumnCollection(
            step=[1],
            columns={
                "ColA": Column("1", "A", "", ["s"]),
            }
        )
        with pytest.raises(ValueError):
            _prepare_for_load_displacement(c3)

    def test_prepare_for_signal_warnings(self, basic_collection):
        """信号処理変換時の警告テスト"""
        # 不均等な時間ステップを作成
        basic_collection.step = Step([
            datetime(2023, 1, 1, 10, 0, 0),
            datetime(2023, 1, 1, 10, 0, 1), # +1s
            datetime(2023, 1, 1, 10, 0, 3)  # +2s (gap)
        ])
        
        _prepare_for_signal(basic_collection)
        
        assert "original_timestamps" in basic_collection.metadata
        assert "signal_warning" in basic_collection.metadata
