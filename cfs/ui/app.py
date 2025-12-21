# 01_src/ui/app.py

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

from ..core.scheduler import CFSScheduler
from ..core.process import Process

# Optional: Metrics/Plot/Export für different_nice direkt aus der UI
from ..metric.metrics import print_report
from ..metric.plotter import plot_cpu_share_vs_expected
from ..metric.export import export_metrics_csv


# ---------------------------
# Scenario Factory Functions
# ---------------------------

@dataclass
class Scenario:
    name: str
    build: Callable[[], Tuple[CFSScheduler, List[Process]]]


def build_simple_equal() -> Tuple[CFSScheduler, List[Process]]:
    s = CFSScheduler(tick=10.0)
    procs = [
        Process(pid=1, nice=0, total_work=100, work_remaining=100),
        Process(pid=2, nice=0, total_work=100, work_remaining=100),
        Process(pid=3, nice=0, total_work=100, work_remaining=100),
    ]
    for p in procs:
        s.add_process(p)
    return s, procs


def build_different_nice() -> Tuple[CFSScheduler, List[Process]]:
    s = CFSScheduler(tick=10.0)
    procs = [
        Process(pid=1, nice=0, total_work=200, work_remaining=200),
        Process(pid=2, nice=5, total_work=200, work_remaining=200),
        Process(pid=3, nice=10, total_work=200, work_remaining=200),
    ]
    for p in procs:
        s.add_process(p)
    return s, procs


def build_interactive_vs_cpu() -> Tuple[CFSScheduler, List[Process]]:
    s = CFSScheduler(tick=5.0)
    cpu = Process(pid=1, nice=0, total_work=300, work_remaining=300)
    i1 = Process(pid=2, nice=0, total_work=40, work_remaining=40)
    i2 = Process(pid=3, nice=0, total_work=40, work_remaining=40)
    i3 = Process(pid=4, nice=0, total_work=40, work_remaining=40)
    procs = [cpu, i1, i2, i3]
    for p in procs:
        s.add_process(p)
    return s, procs


def build_starvation_test() -> Tuple[CFSScheduler, List[Process]]:
    s = CFSScheduler(tick=2.0)
    vip = Process(pid=1, nice=-5, total_work=200, work_remaining=200)
    procs = [vip]
    for i in range(2, 12):
        procs.append(Process(pid=i, nice=10, total_work=60, work_remaining=60))
    for p in procs:
        s.add_process(p)
    return s, procs


SCENARIOS: List[Scenario] = [
    Scenario("simple_equal (Fairness)", build_simple_equal),
    Scenario("different_nice (Prioritäten)", build_different_nice),
    Scenario("interactive_vs_cpu", build_interactive_vs_cpu),
    Scenario("starvation_test", build_starvation_test),
]


# ---------------------------
# UI App
# ---------------------------

class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("CFS Scheduler – Minimal UI")
        self.geometry("980x620")

        self.scheduler: Optional[CFSScheduler] = None
        self.procs: List[Process] = []
        self.timeline: List[int] = []
        self.running: bool = False
        self._after_id: Optional[str] = None

        self._build_widgets()
        self._load_scenario(SCENARIOS[0].name)

    # ---------- UI Layout ----------
    def _build_widgets(self) -> None:
        # Top controls
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Scenario:").pack(side="left")

        self.scenario_var = tk.StringVar(value=SCENARIOS[0].name)
        self.scenario_combo = ttk.Combobox(
            top,
            textvariable=self.scenario_var,
            values=[s.name for s in SCENARIOS],
            state="readonly",
            width=35,
        )
        self.scenario_combo.pack(side="left", padx=(8, 12))
        self.scenario_combo.bind("<<ComboboxSelected>>", self._on_scenario_changed)

        ttk.Button(top, text="Reset", command=self._on_reset).pack(side="left", padx=4)
        ttk.Button(top, text="Step (1 Tick)", command=self._on_step).pack(side="left", padx=4)
        self.run_btn = ttk.Button(top, text="Run", command=self._on_toggle_run)
        self.run_btn.pack(side="left", padx=4)

        ttk.Separator(top, orient="vertical").pack(side="left", fill="y", padx=10)

        ttk.Button(top, text="Run to End", command=self._on_run_to_end).pack(side="left", padx=4)

        ttk.Separator(top, orient="vertical").pack(side="left", fill="y", padx=10)

        ttk.Button(top, text="Metrics (console)", command=self._on_metrics).pack(side="left", padx=4)
        ttk.Button(top, text="Plot (Expected vs Actual)", command=self._on_plot).pack(side="left", padx=4)
        ttk.Button(top, text="Export CSV", command=self._on_export_csv).pack(side="left", padx=4)

        # Status line
        status = ttk.Frame(self, padding=(10, 0, 10, 10))
        status.pack(fill="x")

        self.time_var = tk.StringVar(value="t = 0.0")
        self.last_var = tk.StringVar(value="last pid = -")
        self.left_var = tk.StringVar(value="runnable = 0")

        ttk.Label(status, textvariable=self.time_var).pack(side="left", padx=(0, 12))
        ttk.Label(status, textvariable=self.last_var).pack(side="left", padx=(0, 12))
        ttk.Label(status, textvariable=self.left_var).pack(side="left")

        # Main area
        main = ttk.Frame(self, padding=10)
        main.pack(fill="both", expand=True)

        # Table
        table_frame = ttk.LabelFrame(main, text="Prozesse (Zustand)", padding=8)
        table_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        cols = ("pid", "nice", "weight", "runtime", "vruntime", "remaining")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=18)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120, anchor="center")
        self.tree.column("pid", width=60)
        self.tree.column("nice", width=60)
        self.tree.pack(fill="both", expand=True)

        # Timeline / log
        right = ttk.Frame(main)
        right.pack(side="right", fill="both", expand=False)

        tl_frame = ttk.LabelFrame(right, text="Timeline (letzte 120 Ticks)", padding=8)
        tl_frame.pack(fill="both", expand=True)

        self.timeline_text = tk.Text(tl_frame, height=18, width=32)
        self.timeline_text.pack(fill="both", expand=True)

        help_frame = ttk.LabelFrame(right, text="Hinweise", padding=8)
        help_frame.pack(fill="x", expand=False, pady=(10, 0))

        ttk.Label(
            help_frame,
            text=(
                "Step: 1 Tick ausführen\n"
                "Run: läuft automatisch (20 ms pro UI-Loop)\n"
                "Reset: Scenario neu laden\n"
                "Metrics/Plot/CSV: besonders sinnvoll bei different_nice"
            ),
            justify="left",
        ).pack(anchor="w")

    # ---------- Scenario loading ----------
    def _on_scenario_changed(self, _evt: object) -> None:
        self._load_scenario(self.scenario_var.get())

    def _load_scenario(self, name: str) -> None:
        self._stop_run()
        scenario = next(s for s in SCENARIOS if s.name == name)
        self.scheduler, self.procs = scenario.build()
        self.timeline = []
        self._refresh()

    # ---------- Controls ----------
    def _on_reset(self) -> None:
        self._load_scenario(self.scenario_var.get())

    def _on_step(self) -> None:
        self._do_one_step()

    def _on_toggle_run(self) -> None:
        if self.running:
            self._stop_run()
        else:
            self._start_run()

    def _start_run(self) -> None:
        self.running = True
        self.run_btn.configure(text="Stop")
        self._run_loop()

    def _stop_run(self) -> None:
        self.running = False
        self.run_btn.configure(text="Run")
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _run_loop(self) -> None:
        if not self.running:
            return

        # mehrere Steps pro UI-Loop, damit es nicht zu langsam wirkt
        for _ in range(3):
            if not self._do_one_step():
                self._stop_run()
                break

        self._after_id = self.after(20, self._run_loop)

    def _on_run_to_end(self) -> None:
        self._stop_run()
        # begrenzen, damit UI nicht einfriert
        for _ in range(200000):
            if not self._do_one_step():
                break

    # ---------- Metrics/Plot/Export ----------
    def _on_metrics(self) -> None:
        # Ausgabe in Konsole (Terminal), damit du es direkt in die Doku kopieren kannst
        print_report(self.procs)

    def _on_plot(self) -> None:
        plot_cpu_share_vs_expected(self.procs, title=f"{self.scenario_var.get()}: Expected vs Actual")

    def _on_export_csv(self) -> None:
        # einfacher Dateiname aus Scenario
        safe = self.scenario_var.get().split()[0].strip().replace("(", "").replace(")", "")
        filename = f"{safe}_metrics.csv"
        export_metrics_csv(self.procs, filename)
        self._append_timeline_line(f"\n[CSV geschrieben] {filename}\n")

    # ---------- Step logic ----------
    def _do_one_step(self) -> bool:
        if self.scheduler is None:
            return False

        p = self.scheduler.step()
        if p is None:
            self._refresh()
            return False

        self.timeline.append(p.pid)
        self._refresh(last_pid=p.pid)
        return True

    # ---------- Refresh UI ----------
    def _refresh(self, last_pid: Optional[int] = None) -> None:
        if self.scheduler is None:
            return

        self.time_var.set(f"t = {self.scheduler.time:.1f}")
        self.last_var.set(f"last pid = {last_pid if last_pid is not None else '-'}")

        # Wie viele runnable?
        runnable = len(self.scheduler.runqueue._queue)  # ok für UI/debug
        self.left_var.set(f"runnable = {runnable}")

        # Table: komplett neu zeichnen (einfach & stabil)
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Sortiert nach pid für Übersicht
        for p in sorted(self.procs, key=lambda x: x.pid):
            self.tree.insert(
                "",
                "end",
                values=(
                    p.pid,
                    p.nice,
                    p.weight,
                    f"{p.runtime:.1f}",
                    f"{p.vruntime:.2f}",
                    f"{p.work_remaining:.1f}",
                ),
            )

        # Timeline Anzeige (letzte 120)
        self.timeline_text.delete("1.0", "end")
        last = self.timeline[-120:]
        self.timeline_text.insert("end", " ".join(str(x) for x in last))

    def _append_timeline_line(self, s: str) -> None:
        self.timeline_text.insert("end", s)
        self.timeline_text.see("end")


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
