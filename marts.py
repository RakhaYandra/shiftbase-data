"""Marts HR (DuckDB + parquet di work/). Rumus lembur = API: GREATEST(jam-8,0)."""
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "work"


def _hours(df):
    a = df.copy()
    a["check_in"] = pd.to_datetime(a["check_in"])
    a["check_out"] = pd.to_datetime(a["check_out"])
    a["hours"] = (a["check_out"] - a["check_in"]).dt.total_seconds() / 3600
    a["date"] = pd.to_datetime(a["date"]).dt.date.astype(str)
    return a


def _hhmm(v) -> str:
    import datetime
    if isinstance(v, datetime.timedelta):
        s = int(v.total_seconds())
        return f"{s // 3600:02d}:{(s % 3600) // 60:02d}"
    return str(v)[:5]


def build(df: dict, names: dict) -> dict:
    a = _hours(df["attendance"]).dropna(subset=["hours"])
    a["overtime"] = (a["hours"] - 8).clip(lower=0).round(2)
    a["name"] = a["employee_id"].map(names)
    marts = {"hours_daily": a[["employee_id", "name", "date", "hours", "overtime"]]}

    marts["overtime_employee"] = (a.groupby(["employee_id", "name"], as_index=False)
                                  .agg(total_hours=("hours", "sum"), overtime_hours=("overtime", "sum"),
                                       days=("date", "count")).round(2))

    s = df["shifts"].copy()
    s["date"] = pd.to_datetime(s["date"]).dt.date.astype(str)
    marts["coverage_daily"] = (s.groupby("date", as_index=False)
                               .agg(headcount=("employee_id", "nunique"),
                                    shifts=("id", "count")))

    days = pd.DataFrame({"date": sorted(set(s["date"]) | set(a["date"]))})
    tot_emp = df["employees"]["id"].nunique()
    pres = a.groupby("date")["employee_id"].nunique().reset_index(name="present")
    cov = days.merge(pres, on="date", how="left").fillna({"present": 0})
    cov["rate"] = (cov["present"] / tot_emp).round(3)
    marts["attendance_rate"] = cov

    sh = s[["employee_id", "date", "start_time"]].copy()
    sh["start_time"] = sh["start_time"].apply(_hhmm)
    at = a[["employee_id", "date", "check_in"]].copy()
    at["ci_time"] = pd.to_datetime(at["check_in"]).dt.strftime("%H:%M")
    late = sh.merge(at, on=["employee_id", "date"], how="inner")
    late["late_min"] = ((pd.to_datetime(late["date"] + " " + late["ci_time"])
                         - pd.to_datetime(late["date"] + " " + late["start_time"]))
                        .dt.total_seconds() / 60).round(0)
    late = late[late["late_min"] > 5]
    late["name"] = late["employee_id"].map(names)
    marts["late_arrivals"] = late[["employee_id", "name", "date", "start_time", "ci_time", "late_min"]]
    return marts


def save(marts: dict) -> None:
    WORK.mkdir(exist_ok=True)
    con = duckdb.connect()
    for name, frame in marts.items():
        con.register("m", frame)
        con.execute(f"COPY m TO '{WORK / (name + '.parquet')}' (FORMAT PARQUET)")
    con.close()
