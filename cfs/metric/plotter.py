from __future__ import annotations
from typing import List

import matplotlib.pyplot as plt

from .metrics import compute_process_metrics
from ..core.process import Process


def plot_cpu_share_vs_expected(processes: List[Process], title: str = "") -> None:
    pms = compute_process_metrics(processes)

    labels = [f"pid {x.pid}\n(nice {x.nice})" for x in pms]
    expected = [x.expected_share for x in pms]
    actual = [x.cpu_share for x in pms]

    x = range(len(labels))

    plt.figure()
    plt.bar(x, expected)
    plt.bar(x, actual)
    plt.xticks(list(x), labels)
    plt.xlabel("Process")
    plt.ylabel("CPU share")
    plt.title(title or "CPU Share: Expected vs Actual")
    plt.legend(["Expected (weight)", "Actual (runtime)"])
    plt.tight_layout()
    plt.show()
