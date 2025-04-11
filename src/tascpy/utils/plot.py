# Import matplotlib at module level for proper mocking in tests
from matplotlib import pyplot as plt

def plot_helper(x_data, y_data, x_label=None, y_label=None, ax=None, **kwargs):
    """プロット処理の共通ヘルパー関数"""
    if ax:
        ax.plot(x_data, y_data, **kwargs)
        if x_label:
            ax.set_xlabel(x_label)
        if y_label:
            ax.set_ylabel(y_label)
        return ax
    else:
        fig = plt.figure()
        plt.plot(x_data, y_data, **kwargs)
        if x_label:
            plt.xlabel(x_label)
        if y_label:
            plt.ylabel(y_label)
        return fig
