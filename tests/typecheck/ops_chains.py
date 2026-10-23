"""pyright で検査する型付けの回帰テスト（実行はしない）"""

from typing import assert_type

from tascpy.analytics.ops import CoordinateOps, CoreOps, LoadDisplacementOps, OpsList, StrainOps
from tascpy.core.collection import ColumnCollection
from tascpy.domains.coordinate import CoordinateCollection
from tascpy.domains.load_displacement import LoadDisplacementCollection
from tascpy.domains.strain import StrainCollection


def core_chain(col: ColumnCollection) -> None:
    ops = col.ops.add("A", "B").filter_by_value("S", "a").moving_average("A")
    assert_type(ops, CoreOps[ColumnCollection])
    assert_type(ops.end(), ColumnCollection)
    assert_type(col.ops.split_by_integers([1, 2]), OpsList[CoreOps[ColumnCollection]])


def ld_chain(ld: LoadDisplacementCollection) -> None:
    ops = ld.ops.remove_consecutive_duplicates_across().cycle_count().find_yield_point()
    assert_type(ops, LoadDisplacementOps)
    assert_type(ops.end(), LoadDisplacementCollection)
    assert_type(ops.split_by_cycles()[0], LoadDisplacementOps)
    assert_type(ops.analyze_hysteresis().end(), ColumnCollection)


def domain_conversion(col: ColumnCollection) -> None:
    assert_type(col.ops.as_load_displacement("P", "D").create_skeleton_curve(), LoadDisplacementOps)
    assert_type(col.ops.as_strain().calculate_rosette_strains(columns=["a", "b", "c"]), StrainOps)
    assert_type(col.ops.as_coordinate().interpolate_at_point(0.0, 0.0).end(), CoordinateCollection)


def strain_inherits_coordinate(sc: StrainCollection) -> None:
    assert_type(sc.ops.interpolate_at_point(0.0, 0.0).calculate_stress("F", 2.0), StrainOps)
    assert_type(sc.ops.end(), StrainCollection)


def coordinate_ops(cc: CoordinateCollection) -> None:
    assert_type(cc.ops, CoordinateOps[CoordinateCollection])


def immutable_updates_keep_type(ld: LoadDisplacementCollection, cc: CoordinateCollection) -> None:
    assert_type(ld.with_column("x", [1.0], unit="mm"), LoadDisplacementCollection)
    assert_type(ld.take([0]).rename({"x": "y"}), LoadDisplacementCollection)
    assert_type(cc.with_coordinates("x", 0.0, 0.0), CoordinateCollection)
