from pathlib import Path
import src.tascpy as tp
from matplotlib import pyplot as plt

class Test_results:
    def test_result(self):
        path = Path('./data/W-N.txt')
        with tp.Reader(path) as f:
            res = tp.Experimental_data.load(f)
        # res.plot_history("P_total")
        # res.plot_xy("梁変位", "P_total")
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

