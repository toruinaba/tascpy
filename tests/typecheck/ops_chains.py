"""pyright で検査する型付けの回帰テスト（実行はしない）"""

from typing import Dict, assert_type

from tascpy.domains import CoordinateOps, LoadDisplacementOps, StrainOps
from tascpy.core import CoreOps, OpsList
from tascpy.core.collection import ColumnCollection
from tascpy.core.result import GridResult, PointResult, ScalarResult
from tascpy.core.row import Row
from tascpy.domains.coordinate import CoordinateCollection
from tascpy.domains.load_displacement import LoadDisplacementCollection
from tascpy.domains.strain import StrainCollection
from tascpy.domains import as_coordinate, as_load_displacement, as_strain


def core_chain(col: ColumnCollection) -> None:
    ops = col.ops.add("A", "B", result_column="A+B").filter_by_value("S", "a").moving_average("A", result_column="ma3(A)")
    assert_type(ops, CoreOps[ColumnCollection])
    assert_type(ops.end(), ColumnCollection)
    assert_type(col.ops.split_by_integers([1, 2]), OpsList[CoreOps[ColumnCollection]])


def ld_chain(ld: LoadDisplacementCollection) -> None:
    ops = ld.ops.remove_consecutive_duplicates_across().mark_cycles(result_column="cycle")
    assert_type(ops, LoadDisplacementOps)
    assert_type(ops.end(), LoadDisplacementCollection)
    assert_type(ops.split_by_cycles()[0], LoadDisplacementOps)
    assert_type(ops.to_hysteresis_table().end(), ColumnCollection)
    assert_type(ops.to_skeleton_curve().end(), LoadDisplacementCollection)


def reducers_end_the_chain(ld: LoadDisplacementCollection, sc: StrainCollection, cc: CoordinateCollection) -> None:
    assert_type(ld.ops.to_skeleton_curve().yield_point(offset_value=0.5), PointResult)
    assert_type(ld.ops.stiffness(range_start=0.1, range_end=0.5), ScalarResult)
    assert_type(sc.ops.yield_point(stress_column="s", strain_column="e"), PointResult)
    assert_type(cc.ops.grid(x_range=(0, 1), y_range=(0, 1)), GridResult)
    assert_type(cc.ops.clusters(n_clusters=2), Dict[str, int])
    assert_type(cc.ops.nearest_neighbors("a"), Dict[str, float])
    ld.ops.stiffness(0.1, 0.5)  # pyright: ignore[reportCallIssue]
    ld.ops.add("P", "d")  # pyright: ignore[reportCallIssue]
    ld.ops.mark_cycles()  # pyright: ignore[reportCallIssue]


def domain_conversion(col: ColumnCollection) -> None:
    assert_type(col.ops.end_as(as_load_displacement, load_column="P", displacement_column="D").ops.to_skeleton_curve(),
                LoadDisplacementOps)
    assert_type(col.ops.end_as(as_strain).ops.calculate_rosette_strains(columns=["a", "b", "c"], result_prefix="rosette"), StrainOps)
    assert_type(col.ops.end_as(as_coordinate).ops.interpolate_at_point(0.0, 0.0, result_column="interp(0, 0)").end(), CoordinateCollection)


def strain_inherits_coordinate(sc: StrainCollection) -> None:
    assert_type(sc.ops.interpolate_at_point(0.0, 0.0, result_column="interp(0, 0)").divide("F", 2.0, result_column="stress"), StrainOps)
    assert_type(sc.ops.end(), StrainCollection)


def coordinate_ops(cc: CoordinateCollection) -> None:
    assert_type(cc.ops, CoordinateOps[CoordinateCollection])


def immutable_updates_keep_type(ld: LoadDisplacementCollection, cc: CoordinateCollection) -> None:
    assert_type(ld.with_column("x", [1.0], unit="mm"), LoadDisplacementCollection)
    assert_type(ld.take([0]).rename({"x": "y"}), LoadDisplacementCollection)
    assert_type(cc.with_coordinates("x", 0.0, 0.0), CoordinateCollection)


def domain_conversion_arguments_are_checked(col: ColumnCollection) -> None:
    # end_as は変換関数のシグネチャで引数を検査する（不要な ignore は reportUnnecessaryTypeIgnoreComment で検出）
    col.ops.end_as(as_load_displacement, load_colum="P")  # pyright: ignore[reportCallIssue]
    col.ops.end_as(as_load_displacement, load_column=1, displacement_column="D")  # pyright: ignore[reportArgumentType]
    col.ops.end_as(as_load_displacement)  # pyright: ignore[reportCallIssue]
    col.ops.end_as(as_coordinate, {"a": {"x": 0.0}})  # pyright: ignore[reportCallIssue]


def collect_to_table(ld: LoadDisplacementCollection) -> None:
    parts = ld.ops.split_by_cycles()
    assert_type(parts.collect(lambda o: o.nearest_row("P", 1.0)).to_table(), LoadDisplacementOps)
    assert_type(parts.collect(lambda o: o.yield_point()).to_table(name="yp"), CoreOps[ColumnCollection])
    assert_type(ld.ops.nearest_row("P", 1.0), Row)
