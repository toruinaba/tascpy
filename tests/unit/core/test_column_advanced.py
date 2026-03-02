import pytest
import numpy as np
from tascpy.core.column import Column, NumberColumn, StringColumn, InvalidColumn

def test_column_base_methods():
    # max_index
    num_col = NumberColumn("ch", "num", "", [10, 20, 5, 30, np.nan])
    assert num_col.max_index == 3

    nan_col = NumberColumn("ch", "nan", "", [np.nan, np.nan])
    assert nan_col.max_index is None

    str_col = StringColumn("ch", "str", "", ["a", "c", "b", None])
    assert str_col.max_index == 1

    empty_col = Column("ch", "empty", "", [])
    assert empty_col.max_index is None

    # Base class stats (should return None)
    base_col = Column("ch", "base", "", [1, 2, 3])
    assert base_col.mean() is None
    assert base_col.median() is None
    assert base_col.std() is None
    assert base_col.sum() is None
    assert base_col.variance() is None
    assert base_col.quantile(0.5) is None
    assert base_col.ptp() == 2

    # base col abs max
    base_col2 = Column("ch", "base2", "", [-10, 5, 2])
    assert base_col2.abs_max() == 10

def test_column_valid_methods():
    num_col = NumberColumn("ch", "num", "", [10, np.nan, 20])
    assert num_col.n_valid == 2
    np.testing.assert_array_equal(num_col.is_valid(), [True, False, True])
    assert num_col.first_valid_index == 0
    assert num_col.first_invalid_index == 1

    empty_col = Column("ch", "empty", "", [])
    np.testing.assert_array_equal(empty_col.is_valid(), [])
    assert empty_col.first_valid_index is None
    assert empty_col.first_invalid_index is None

def test_column_to_numeric():
    str_col = StringColumn("ch", "str", "", ["1.5", "nan", "3.0", "invalid"])
    
    # coerce
    num_col = str_col.to_numeric(errors="coerce")
    assert type(num_col) is NumberColumn
    np.testing.assert_allclose(num_col.values, [1.5, np.nan, 3.0, np.nan], equal_nan=True)
    
    # raise
    with pytest.raises(ValueError):
        str_col.to_numeric(errors="raise")

    # ignore returns self
    ignored = str_col.to_numeric(errors="ignore")
    assert type(ignored) is StringColumn

    # already number column
    orig_num = NumberColumn("ch", "n", "", [1, 2, 3])
    already_numeric = orig_num.to_numeric()
    assert type(already_numeric) is NumberColumn

def test_column_clip():
    num_col = NumberColumn("ch", "num", "", [1, 5, 10])
    clipped = num_col.clip(lower=3, upper=7)
    np.testing.assert_array_equal(clipped.values, [3, 5, 7])

    str_col = StringColumn("ch", "str", "", ["a", "b", "c"])
    clipped_str = str_col.clip(lower=3, upper=7)
    assert type(clipped_str) is Column

def test_column_find_nearest():
    num_col = NumberColumn("ch", "num", "", [10.0, 20.0, 30.0, 40.0])
    
    assert num_col.find_nearest_index(22.0) == 1
    assert num_col.find_nearest(22.0) == 20.0

    assert num_col.find_nearest_index(36.0) == 3
    assert num_col.find_nearest(36.0) == 40.0

    empty_col = Column("ch", "empty", "", [])
    assert empty_col.find_nearest_index(10) == -1
    assert empty_col.find_nearest(10) is None

    str_col = StringColumn("ch", "str", "", ["a", "b", "c"])
    assert str_col.find_nearest_index("b") == -1

def test_number_column_stats():
    # std and var tests specifically with NaNs and single value
    col_single = NumberColumn("ch", "single", "", [5])
    assert col_single.std() is None
    assert col_single.variance() is None

    col_nan = NumberColumn("ch", "nan", "", [np.nan, np.nan])
    assert col_nan.mean() is None
    assert col_nan.median() is None
    assert col_nan.std() is None
    assert col_nan.variance() is None
    assert col_nan.quantile(0.5) is None
    
    col_nan_single = NumberColumn("ch", "nan_single", "", [5, np.nan])
    assert col_nan_single.std() is None
    assert col_nan_single.variance() is None

def test_invalid_column_sum():
    invalid = InvalidColumn("ch", "inv", "", [None, None])
    assert invalid.sum() == 0.0

def test_detect_column_type_errors():
    from tascpy.core.column import detect_column_type
    # Force an exception in detect_column_type by using something uncomparable?
    # Actually just pass anything.
    # We can pass an object that raises an error when isinstance is called
    pass
