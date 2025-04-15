from pathlib import Path
import src.tascpy as tp
from matplotlib import pyplot as plt

from src.tascpy.utils.data import diff_step, smooth_data
from src.tascpy.plugins.load_displacement import cycle_count

class Test_results:
    def test_01(self):
        path = Path('./data/W-N.txt')
        with tp.Reader(path) as f:
            res = tp.Experiment.load(f)
        res.plot_history("P_total")
        res.plot_xy("梁変位", "P_total")
        req_steps = list(range(1, 400))
        req_names = ["P_total", "梁変位", "b11", "b21", "b31", "b41", "b51", "b12", "b22", "b32", "b42", "b52"]
        extracted = res.extract_data(names=req_names, steps=req_steps)
        extracted.to_csv("./data/extracted_W-N.csv")
        ref_load1 = 200.0
        ref_load2 = 600.0
        fetched_step1 = extracted.fetch_near_step("P_total", ref_load1)
        fetched_step2 = extracted.fetch_near_step("P_total", ref_load2)
        fig = plt.figure(figsize=(10, 3))
        ax1 = fig.add_subplot(1,3,1)
        extracted.plot_xy("梁変位", "P_total", ax=ax1, linewidth=0.5)
        ax1.scatter([fetched_step1["梁変位"].data], [fetched_step1["P_total"].data], marker="o", color="r")
        ax1.scatter([fetched_step2["梁変位"].data], [fetched_step2["P_total"].data], marker="^", color="b")
        ax2 = fig.add_subplot(1,3,2)
        ax3 = fig.add_subplot(1,3,3)
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
        path = Path('./data/W-N.txt')
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
            d.split_by_ref_ch_condition("P_total", lambda x: x > 0.0)[0]
            for d in dived
        ]

        count = 1
        for d in dived_pos:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            smoothed = smooth_data(d["梁変位ﾜｲﾔ"].data, 10)
            diff = diff_step(smoothed)
            markers = cycle_count(diff, step=1)
            dv = d.split_by_integers(markers)
            dv[0].plot_xy("梁変位ﾜｲﾔ", "P_total", ax=ax)
            dv[1].plot_xy("梁変位ﾜｲﾔ", "P_total", ax=ax)
            plt.show()
