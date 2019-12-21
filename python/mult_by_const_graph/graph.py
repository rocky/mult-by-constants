import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import os
import os.path as osp

# Interactive sessions don't set __file__
if "__file__" in globals():
    def get_srcdir():
        filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
        return osp.realpath(filename)

    os.chdir(get_srcdir())

colors = ("gray", "blue")
alphas = (0.3, 1.0)
labels = ("binary method", "alpha-beta search")
sizes = (100, 10000)
for size in sizes:
    plt.ylabel("cost")
    plt.xlabel("n")
    for i, path in enumerate(
        (f"../tables/{size}-bincost.csv", f"../tables/{size}-stdcost.csv")
    ):
        data = pd.read_csv(path, dialect="excel-tab")
        marker = "o" if size < 200 else ""
        plt.plot(
            data.n,
            data.cost,
            color=colors[i],
            alpha=alphas[i],
            marker=marker,
            label=labels[i],
        )
        pass
    plt.legend(loc=len(labels), ncol=len(labels))
    plt.title("Multiplication by constants: optimal vs. binary method")
    plt.savefig(f"../graphs/{size}-bin-vs-stdcost.svg")
    if size != sizes[-1]:
        # Clearing the graph is done only for jupyter
        plt.clf()
    pass
