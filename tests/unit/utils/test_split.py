
import pytest
from tascpy.utils.split import (
    split_list_by_chunks,
    split_list_by_count,
    split_list_by_condition,
    split_list_at_indices,
    split_list_by_threshold,
    split_list_by_integers,
)

class TestSplitListByChunks:
    def test_even_split(self):
        data = [1, 2, 3, 4]
        res = split_list_by_chunks(data, 2)
        assert res == [[1, 2], [3, 4]]

    def test_uneven_split(self):
        data = [1, 2, 3, 4, 5]
        res = split_list_by_chunks(data, 2)
        assert res == [[1, 2], [3, 4], [5]]

    def test_empty(self):
        assert split_list_by_chunks([], 2) == []

    def test_invalid_chunk_size(self):
        with pytest.raises(ValueError):
            split_list_by_chunks([1, 2], 0)

class TestSplitListByCount:
    def test_even_split(self):
        data = [1, 2, 3, 4, 5, 6]
        res = split_list_by_count(data, 3)
        assert res == [[1, 2], [3, 4], [5, 6]]

    def test_uneven_split(self):
        # 10 items, 3 chunks. 10 // 3 = 3. remainder 1.
        # Chunks: 4, 3, 3.
        data = list(range(10))
        res = split_list_by_count(data, 3)
        assert len(res) == 3
        assert len(res[0]) == 4
        assert len(res[1]) == 3
        assert len(res[2]) == 3
        assert res[0] == [0, 1, 2, 3]

    def test_count_gt_len(self):
        data = [1, 2]
        res = split_list_by_count(data, 3)
        # 2 // 3 = 0. remainder 2.
        # chunks: 1, 1, 0.
        assert res == [[1], [2], []]

    def test_invalid_count(self):
        with pytest.raises(ValueError):
            split_list_by_count([1], 0)

class TestSplitListByCondition:
    def test_basic(self):
        data = [1, 2, 3, 4, 5]
        sat, not_sat = split_list_by_condition(data, lambda x: x % 2 == 0)
        assert sat == [2, 4]
        assert not_sat == [1, 3, 5]

class TestSplitListAtIndices:
    def test_basic(self):
        data = [10, 20, 30, 40, 50]
        # indices [1, 3] -> split at index 1 and 3.
        # [0:1], [1:3], [3:]
        # [10], [20, 30], [40, 50]
        res = split_list_at_indices(data, [1, 3])
        assert res == [[10], [20, 30], [40, 50]]

    def test_single_index(self):
        data = [1, 2]
        res = split_list_at_indices(data, 1)
        assert res == [[1], [2]]

    def test_out_of_bounds(self):
        data = [1, 2]
        res = split_list_at_indices(data, [5])
        # [0:5] -> [1, 2]
        # [5:] -> []
        assert res == [[1, 2], []]

class TestSplitListByThreshold:
    def test_basic(self):
        data = [1.0, 5.0, 2.0, 6.0]
        high, low = split_list_by_threshold(data, 4.0)
        assert high == [5.0, 6.0]
        assert low == [1.0, 2.0]

class TestSplitListByIntegers:
    def test_grouping(self):
        data = ['a', 'b', 'c', 'd']
        markers = [1, 2, 1, 2]
        # 1: a, c
        # 2: b, d
        # Returns sorted by marker key: [[a, c], [b, d]]
        res = split_list_by_integers(data, markers)
        assert len(res) == 2
        assert res[0] == ['a', 'c'] # group 1
        assert res[1] == ['b', 'd'] # group 2

    def test_len_mismatch(self):
        with pytest.raises(ValueError):
            split_list_by_integers(['a'], [1, 2])
