#core/ → „Was ist der Scheduler?“ (Herzstück)

process.py

Prozess-Objekt

Attribute: pid, nice, weight, vruntime, exec_time

scheduler.py

CFS-Logik

Auswahl: kleinste vruntime gewinnt ← Aha-Moment

runqueue.py (optional, aber elegant)

Verwaltung aller lauffähigen Prozesse

Sortierung nach vruntime

constants.py

NICE-to-WEIGHT Tabelle

Zeitscheiben-Parameter

👉 Merksatz:
core enthält alles, was man theoretisch auch im Linux-Kernel finden würde – nur vereinfacht.

#metric/ → „Wie fair ist das Ganze?“

metrics.py

Fairness-Metriken

Vergleich: reale Laufzeit vs. ideale Laufzeit

vruntime_tracker.py

Verlauf der virtuellen Laufzeiten

Wer „benachteiligt“ wird

statistics.py

Durchschnittswerte

Wartezeiten

Turnaround-Time

👉 Aha-Moment:
CFS misst Fairness nicht in Zeit, sondern in virtueller Zeit.

#scenarios/ → „Zeig mir, dass es funktioniert“

simple_equal.py

Mehrere Prozesse, gleiche Priorität

different_nice.py

Unterschiedliche Nice-Werte

Sichtbar: vruntime wächst unterschiedlich schnell

interactive_vs_cpu.py

Kurz laufende vs. lange Prozesse

starvation_test.py

Nachweis: keine Verhungern

👉 Prüfungs-Gold:
Hier entstehen die Screenshots / Diagramme / Demo-Runs für Präsentation & Doku.

Faustregel

core = Logik

metric = Bewertung

scenarios = Beweis
