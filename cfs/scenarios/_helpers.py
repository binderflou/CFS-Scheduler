# 01_src/scenarios/_helpers.py

from __future__ import annotations
from typing import List, Dict

from ..core.scheduler import CFSScheduler
from ..core.process import Process


def run_simulation(
    scheduler: CFSScheduler,
    max_steps: int = 10_000,
    print_every: int = 1,
) -> Dict[str, object]:
    """
    Läuft den Scheduler bis keine Prozesse mehr da sind (oder max_steps erreicht).
    Gibt Timeline + Summary zurück.
    """
    timeline: List[int] = []
    steps = 0

    while steps < max_steps:
        p = scheduler.step()
        if p is None:
            break

        timeline.append(p.pid)

        if print_every > 0 and (steps % print_every == 0):
            print(
                f"t={scheduler.time:>6.1f}  ran pid={p.pid:>3}  "
                f"vr={p.vruntime:>8.2f}  rt={p.runtime:>6.1f}  rem={p.work_remaining:>6.1f}"
            )
        steps += 1

    # Prozesse sind in der RunQueue ggf. schon entfernt → Summary über alle, die wir kennen:
    # Wir nehmen aus dem Timeline-Run die PIDs und holen uns die letzten Zustände aus scheduler.current
    # Besser: Scenarios halten eigene Prozessliste und geben sie rein (machen wir in den Scenarios).
    return {"timeline": timeline, "steps": steps}


def print_timeline(timeline: List[int], width: int = 60) -> None:
    """
    Kompakte Darstellung: pro Tick eine PID.
    """
    if not timeline:
        print("Timeline: (leer)")
        return

    print("\nTimeline (jede Zahl = ein Tick):")
    line: List[str] = []
    for i, pid in enumerate(timeline, start=1):
        line.append(str(pid))
        if i % width == 0:
            print(" ".join(line))
            line = []
    if line:
        print(" ".join(line))


def print_summary(processes: List[Process]) -> None:
    """
    Kurze Auswertung pro Prozess.
    """
    print("\nSummary:")
    print("pid | nice | weight | runtime | vruntime")
    print("----------------------------------------")
    for p in sorted(processes, key=lambda x: x.pid):
        print(f"{p.pid:>3} | {p.nice:>4} | {p.weight:>6} | {p.runtime:>7.1f} | {p.vruntime:>8.2f}")


