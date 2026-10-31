"""荷重-変位ドメインのコレクションクラスのテスト"""

import numpy as np
import pytest

from tascpy.domains import LoadDisplacementOps
from tascpy.core.collection import ColumnCollection
from tascpy.domains.load_displacement import LoadDisplacementCollection
from tascpy.domains import as_load_displacement


class TestLoadDisplacementCollection:
    def setup_method(self):
        self.steps = list(range(5))
        self.loads = [0.0, 10.0, 20.0, 15.0, 5.0]
        self.displacements = [0.0, 0.1, 0.2, 0.15, 0.05]
        self.columns = {"load": self.loads, "displacement": self.displacements}
        self.collection = ColumnCollection(self.columns, step=self.steps)

    def _ld(self, **kwargs):
        return LoadDisplacementCollection(
            self.columns, step=self.steps, load_column="load", displacement_column="displacement", **kwargs
        )

    def test_initialization(self):
        ld = self._ld()
        assert ld.load_column == "load"
        assert ld.displacement_column == "displacement"
        assert ld["load"].to_list() == self.loads
        assert ld["displacement"].to_list() == self.displacements
        assert ld.domain == "load_displacement"

    def test_initialization_custom_columns(self):
        ld = LoadDisplacementCollection(
            {"force": self.loads, "disp": self.displacements}, step=self.steps,
            load_column="force", displacement_column="disp",
        )
        assert ld.load_column == "force"
        assert ld.displacement_column == "disp"
        assert ld["force"].to_list() == self.loads
        assert ld["disp"].to_list() == self.displacements

    def test_load_and_displacement_properties(self):
        ld = LoadDisplacementCollection(
            {"force": self.loads, "disp": self.displacements}, step=self.steps,
            units={"force": "kN", "disp": "mm"}, load_column="force", displacement_column="disp",
        )
        assert ld.load.unit == "kN"
        assert ld.displacement.unit == "mm"
        np.testing.assert_array_equal(ld.load_data, self.loads)
        np.testing.assert_array_equal(ld.displacement_data, self.displacements)

    def test_from_collection(self):
        ld = self.collection.ops.end_as(as_load_displacement, load_column="load", displacement_column="displacement")
        assert isinstance(ld, LoadDisplacementCollection)
        assert ld.load_column == "load"
        assert ld.displacement_column == "displacement"
        assert ld["load"].to_list() == self.loads

    def test_from_collection_custom_columns(self):
        collection = ColumnCollection({"force": self.loads, "disp": self.displacements}, step=self.steps)
        ld = collection.ops.end_as(as_load_displacement, load_column="force", displacement_column="disp")
        assert isinstance(ld, LoadDisplacementCollection)
        assert ld.load_column == "force"
        assert ld.displacement_column == "disp"

    def test_missing_columns(self):
        load_only = ColumnCollection({"load": self.loads}, step=self.steps)
        with pytest.raises(ValueError) as exc_info:
            load_only.ops.end_as(as_load_displacement, load_column="load", displacement_column="displacement")
        assert "displacement_column" in str(exc_info.value)

        disp_only = ColumnCollection({"displacement": self.displacements}, step=self.steps)
        with pytest.raises(ValueError) as exc_info:
            disp_only.ops.end_as(as_load_displacement, load_column="load", displacement_column="displacement")
        assert "load_column" in str(exc_info.value)

    def test_columns_are_not_guessed_from_names(self):
        # 列名に "load" / "displacement" を含んでいても、指定しなければ推測しない
        with pytest.raises(TypeError):
            self.collection.ops.end_as(as_load_displacement)  # pyright: ignore[reportCallIssue]

    def test_direct_invalid_columns(self):
        with pytest.raises(ValueError) as exc_info:
            LoadDisplacementCollection(self.columns, step=self.steps,
                                       load_column="nonexistent", displacement_column="displacement")
        assert "load_column" in str(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            LoadDisplacementCollection(self.columns, step=self.steps,
                                       load_column="load", displacement_column="nonexistent")
        assert "displacement_column" in str(exc_info.value)

    def test_non_numeric_column_rejected(self):
        with pytest.raises(ValueError):
            LoadDisplacementCollection({"load": list("abcde"), "displacement": self.displacements},
                                       step=self.steps, load_column="load", displacement_column="displacement")

    def test_settings_follow_rename_and_drop(self):
        ld = self._ld()
        renamed = ld.rename({"load": "P"})
        assert isinstance(renamed, LoadDisplacementCollection)
        assert renamed.load_column == "P"
        with pytest.raises(ValueError):
            ld.drop("load")

    def test_default_operations(self):
        ops = self._ld().ops

        filtered = ops.filter_by_value("load", 10.0).end()
        assert len(filtered) == 1
        assert filtered["load"].values[0] == 10.0

        added = ops.add("load", 5.0, result_column="load_plus_5").end()
        assert added["load_plus_5"].values[0] == 5.0

        selected = ops.select(steps=[1, 2]).end()
        assert len(selected) == 2
        np.testing.assert_array_equal(selected.step, [1, 2])

    def test_domain_operations(self):
        ops = self._ld().ops
        assert isinstance(ops, LoadDisplacementOps)
        chained = ops.add("load", 1.0, result_column="load1")
        assert isinstance(chained, LoadDisplacementOps)
        assert isinstance(chained.end(), LoadDisplacementCollection)

    def test_getitem_error_handling(self):
        ld = self._ld()
        with pytest.raises(KeyError) as exc_info:
            _ = ld["nonexistent_column"]
        assert "nonexistent_column" in str(exc_info.value)
