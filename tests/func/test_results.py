from pathlib import Path
import src.tascpy as tp
from matplotlib import pyplot as plt

class Test_results:
    def test_result(self):
        path = Path('./data/W-N.txt')
        with tp.Reader(path) as f:
            res = tp.Experimental_data(f)
        # res.plot_history("P_total")
        # res.plot_xy("梁変位", "P_total")
        ref_step = 1000
        step1 = res.get_step(ref_step)
        fig = plt.figure(figsize=(10, 5))
        ax1 = fig.add_subplot(1,2,1)
        plot_list = [["b11", "b21", "b31", "b41", "b51"], ["b12", "b22", "b32", "b42", "b52"]]
        step1.plot_const_x([0.0, 50.0, 100.0, 200.0, 300.0], plot_list, ax=ax1, marker="o")
        ax2 = fig.add_subplot(1,2,2)
        res.plot_history(["b11", "b21", "b31", "b41", "b51"], ax=ax2)
        ax2.plot([ref_step, ref_step], [0.0, 105.0], "k")
        ax2.legend()
        plt.show()
        # plt.show()
        #data = res["P_total"]
        #print(data.to_dict())
        #step = res.get_step(10)
        # print(step.to_dict())
        # assert res.dict

