"""Charts Nexus-style -> charts/*.png."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
CH = ROOT / "charts"

NAVY, SURF, BLUE, LBLUE, INK, MUT, RED = (
    "#0B1120", "#0F172A", "#3B82F6", "#60A5FA", "#F1F5F9", "#94A3B8", "#F87171")


def _fig():
    plt.rcParams.update({"figure.facecolor": NAVY, "axes.facecolor": SURF,
                         "text.color": INK, "axes.labelcolor": MUT,
                         "xtick.color": MUT, "ytick.color": MUT,
                         "font.family": "sans-serif"})
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for s in ax.spines.values():
        s.set_color("#1E293B")
    return fig, ax


def _save(fig, name):
    CH.mkdir(exist_ok=True)
    fig.tight_layout()
    fig.savefig(CH / name, dpi=110)
    plt.close(fig)


def overtime_employee(m):
    m = m.sort_values("overtime_hours", ascending=True)
    fig, ax = _fig()
    ax.barh(m["name"], m["overtime_hours"], color=BLUE)
    ax.set_title("OVERTIME HOURS PER EMPLOYEE", fontsize=10, loc="left", color=MUT, family="monospace")
    for i, v in enumerate(m["overtime_hours"]):
        ax.text(v, i, f" {v:.1f}h", va="center", fontsize=8, color=INK, family="monospace")
    _save(fig, "overtime_employee.png")


def coverage_trend(m):
    fig, ax = _fig()
    ax.plot(m["date"], m["headcount"], marker="o", color=BLUE)
    ax.set_title("DAILY COVERAGE HEADCOUNT", fontsize=10, loc="left", color=MUT, family="monospace")
    ax.tick_params(axis="x", labelsize=7, rotation=30)
    _save(fig, "coverage_trend.png")


def attendance_rate(m):
    fig, ax = _fig()
    ax.bar(m["date"], m["rate"], color=LBLUE)
    ax.set_ylim(0, 1.1)
    ax.set_title("ATTENDANCE RATE PER DAY", fontsize=10, loc="left", color=MUT, family="monospace")
    ax.tick_params(axis="x", labelsize=7, rotation=30)
    _save(fig, "attendance_rate.png")


def late_arrivals(m):
    d = m.groupby("name")["late_min"].max().sort_values(ascending=True)
    fig, ax = _fig()
    if len(d) == 0:
        ax.text(0.5, 0.5, "NO LATE ARRIVALS", ha="center", color=MUT, family="monospace")
    else:
        ax.barh(d.index, d.values, color=RED)
        for i, v in enumerate(d.values):
            ax.text(v, i, f" +{v:.0f}m", va="center", fontsize=8, color=INK, family="monospace")
    ax.set_title("MAX LATE MINUTES PER EMPLOYEE", fontsize=10, loc="left", color=MUT, family="monospace")
    _save(fig, "late_arrivals.png")


def all_charts(marts):
    overtime_employee(marts["overtime_employee"])
    coverage_trend(marts["coverage_daily"])
    attendance_rate(marts["attendance_rate"])
    late_arrivals(marts["late_arrivals"])
    print("charts: 4 png")
