from pathlib import Path
import src.tascpy as tp
from matplotlib import pyplot as plt

from src.tascpy.utils.data import diff_step, smooth_data
from src.tascpy.plugins.load_displacement import cycle_count


class Test_results:
    def test_01(self):
        path = Path("./data/W-N.txt")
        with tp.Reader(path) as f:
            res = tp.Experiment.load(f)
        res.plot_history("P_total")
        res.plot_xy("梁変位", "P_total")
        req_steps = list(range(1, 400))
        req_names = [
            "P_total",
            "梁変位",
            "b11",
            "b21",
            "b31",
            "b41",
            "b51",
            "b12",
            "b22",
            "b32",
            "b42",
            "b52",
        ]
        extracted = res.extract_data(names=req_names, steps=req_steps)
        extracted.to_csv("./data/extracted_W-N.csv")
        ref_load1 = 200.0
        ref_load2 = 600.0
        fetched_step1 = extracted.fetch_near_step("P_total", ref_load1)
        fetched_step2 = extracted.fetch_near_step("P_total", ref_load2)
        fig = plt.figure(figsize=(10, 3))
        ax1 = fig.add_subplot(1, 3, 1)
        extracted.plot_xy("梁変位", "P_total", ax=ax1, linewidth=0.5)
        ax1.scatter(
            [fetched_step1["梁変位"].data],
            [fetched_step1["P_total"].data],
            marker="o",
            color="r",
        )
        ax1.scatter(
            [fetched_step2["梁変位"].data],
            [fetched_step2["P_total"].data],
            marker="^",
            color="b",
        )
        ax2 = fig.add_subplot(1, 3, 2)
        ax3 = fig.add_subplot(1, 3, 3)
        distance = [0.0, 50.0, 100.0, 200.0, 300.0]
        plot_list1 = ["b11", "b21", "b31", "b41", "b51"]
        plot_list2 = ["b12", "b22", "b32", "b42", "b52"]
        fetched_step1.plot_const_x(distance, plot_list1, ax=ax2, marker="o", color="r")
        fetched_step2.plot_const_x(distance, plot_list1, ax=ax2, marker="^", color="b")
        fetched_step1.plot_const_x(distance, plot_list2, ax=ax3, marker="o", color="r")
        fetched_step2.plot_const_x(distance, plot_list2, ax=ax3, marker="^", color="b")
        ax2.set_xlim(0, 300.0)
        ax2.set_ylim(50, 110.0)
        ax3.set_xlim(0, 300.0)
        ax3.set_ylim(50, 110.0)
        plt.show()

    def test_02(self):
        path = Path("./data/W-N.txt")
        with tp.Reader(path) as f:
            res = tp.Experiment.load(f)
        """
        res.plot_xy("梁変位ﾜｲﾔ", "P_total")
        plt.show()
        """
        pd = res.extract_data(["P_total", "梁変位ﾜｲﾔ"])
        pd_rmn = pd.remove_none()
        pd_rmdup = pd_rmn.remove_consecutive_duplicates_across(["P_total", "梁変位ﾜｲﾔ"])
        p = pd_rmdup["P_total"].data
        markers = cycle_count(p)
        dived = pd_rmdup.split_by_integers(markers)
        dived_pos = [
            d.split_by_ref_ch_condition("P_total", lambda x: x > 0.0)[0] for d in dived
        ]

        count = 1
        from src.tascpy.utils.data import detect_outliers_ratio

        for d in dived_pos:
            outliers = detect_outliers_ratio(d["梁変位ﾜｲﾔ"].data, 3, 0.1)
            remove_steps = [d.steps[i] for i, x in outliers]
            if not remove_steps:
                d_removed_outliers = d
            else:
                d_removed_outliers = d.remove_data(names=None, steps=remove_steps)
            fig = plt.figure()
            ax = fig.add_subplot(111)
            max_index = d_removed_outliers["梁変位ﾜｲﾔ"].max_index
            splitted = d_removed_outliers.split_at_indices(max_index + 1)
            splitted[0].plot_xy("梁変位ﾜｲﾔ", "P_total", ax=ax)
            splitted[1].plot_xy("梁変位ﾜｲﾔ", "P_total", ax=ax)
            ax.set_title(f"step {count}")

            from src.tascpy.plugins.load_displacement import (
                find_general_yield_point,
                offset_yield_point,
            )

            p = splitted[0]["P_total"].data
            d = splitted[0]["梁変位ﾜｲﾔ"].data
            p_smooth = smooth_data(p, 3)
            d_smooth = smooth_data(d, 3)
            print(len(d_smooth), len(p_smooth))
            print(len(d), len(p))
            ax.plot(d_smooth, p_smooth, label="smoothed")
            yield_point = offset_yield_point(
                d, p, offset_value=2, r_lower=0.1, r_upper=0.3
            )
            print(f"yield_point: {yield_point}")
            from src.tascpy.utils.plot import add_point

            add_point(ax, yield_point[1], yield_point[0])
            plt.show()

    def test_03(self):
        path = Path("./data/W-N.txt")
        with tp.Reader(path) as f:
            res = tp.Experiment.load(f)
        pd = res.extract_data(["P_total", "梁変位ﾜｲﾔ"])
        pd_rmn = pd.remove_none()
        pd_rmdup = pd_rmn.remove_consecutive_duplicates_across(["P_total", "梁変位ﾜｲﾔ"])
        p = pd_rmdup["P_total"].data
        d = pd_rmdup["梁変位ﾜｲﾔ"].data
        from src.tascpy.utils.data import detect_outliers_ratio

        d_outliers = detect_outliers_ratio(d, 3, 0.1)
        remove_steps = [pd_rmdup.steps[i] for i, x in d_outliers]
        if not remove_steps:
            pd_removed_outliers = pd_rmdup
        else:
            pd_removed_outliers = pd_rmdup.remove_data(names=None, steps=remove_steps)
        max_index = pd_removed_outliers["P_total"].max_index
        ax = pd_removed_outliers.plot_xy(
            "梁変位ﾜｲﾔ", "P_total", linewidth=0.5, label="removed outliers"
        )
        pd_rmdup.plot_xy("梁変位ﾜｲﾔ", "P_total", ax=ax, linewidth=0.5, label="original")
        plt.show()

        from src.tascpy.plugins.load_displacement import create_skeleton_curve

        p_cyc = pd_removed_outliers["P_total"].data
        d_cyc = pd_removed_outliers["梁変位ﾜｲﾔ"].data
        p_ske, d_ske = create_skeleton_curve(
            d_cyc, p_cyc, has_decrease=True, decrease_type="envelope"
        )
        p_ske2, d_ske2 = create_skeleton_curve(
            d_cyc, p_cyc, has_decrease=True, decrease_type="continuous_only"
        )

        from src.tascpy.plugins.load_displacement import (
            find_general_yield_point,
            find_offset_yield_point,
        )

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(d_ske, p_ske, label="envelope")
        ax.plot(d_ske2, p_ske2, label="continuous_only")
        py1, dy1, stiff1 = find_general_yield_point(
            d_ske, p_ske, r_lower=0.33, r_upper=0.66
        )
        py2, dy2, stiff2 = find_offset_yield_point(
            d_ske, p_ske, offset_value=2, r_lower=0.33, r_upper=0.66
        )
        print(f"yield_point: {py1}, {dy1}, {stiff1}")
        from src.tascpy.utils.plot import (
            add_point,
            add_vertical_line,
            add_origin_line,
            add_line_with_slope,
        )

        add_origin_line(ax=ax, slope=stiff1, text="slope1")
        add_line_with_slope(ax=ax, slope=stiff2, point=(2, 0), text="slope2")
        add_point(ax, dy1, py1, text="yield_point")
        add_point(ax, dy2, py2, text="offset_yield_point")
        ax.legend()
        plt.show()

    def test_04(self):
        path = Path("./data/W-N.txt")
        with tp.Reader(path) as f:
            res = tp.Experiment.load(f)
        pd = res.extract_data(["P_total", "梁変位ﾜｲﾔ"])
        pd_rmn = pd.remove_none()
        pd_rmdup = pd_rmn.remove_consecutive_duplicates_across(
            ["P_total", "梁変位ﾜｲﾔ"], dup_type="all"
        )
        p = pd_rmdup["P_total"].data
        d = pd_rmdup["梁変位ﾜｲﾔ"].data
        from src.tascpy.utils.data import detect_outliers_ratio

        d_outliers = detect_outliers_ratio(d, 3, 0.1)
        remove_steps = [pd_rmdup.steps[i] for i, x in d_outliers]
        remove_steps = [pd_rmdup.steps[1]] + remove_steps
        if not remove_steps:
            pd_removed_outliers = pd_rmdup
        else:
            pd_removed_outliers = pd_rmdup.remove_data(names=None, steps=remove_steps)
        max_index = pd_removed_outliers["P_total"].max_index

        from src.tascpy.plugins.load_displacement import (
            create_skeleton_curve,
            cycle_count,
            create_cumulative_curve,
        )

        p_cyc = pd_removed_outliers["P_total"].data
        d_cyc = pd_removed_outliers["梁変位ﾜｲﾔ"].data
        p_cum, d_cum = create_cumulative_curve(d_cyc, p_cyc)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(d_cum, p_cum, label="envelope")
        # ax.plot(d_cyc, p_cyc, label="original")
        plt.show()
