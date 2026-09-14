"""Quality gates: gagalkan run bila data kotor."""
import pandas as pd


def check(df: dict) -> dict:
    errors: list[str] = []

    if len(df["employees"]) == 0:
        errors.append("employees: kosong")
    if len(df["shifts"]) == 0:
        errors.append("shifts: kosong (apply demo_data.sql dulu)")

    eids = set(df["employees"]["id"])
    for t in ["shifts", "attendance"]:
        orph = df[t][~df[t]["employee_id"].isin(eids)]
        if len(orph):
            errors.append(f"{t} orphan employee_id: {len(orph)}")

    # check_out <= check_in
    a = df["attendance"].dropna(subset=["check_out"])
    bad = pd.to_datetime(a["check_out"]) <= pd.to_datetime(a["check_in"])
    if bad.any():
        errors.append(f"attendance check_out<=check_in: {int(bad.sum())}")

    # shift end <= start (ekspektasi TIME string HH:MM:SS)
    s = df["shifts"]
    bad_s = s["end_time"].astype(str) <= s["start_time"].astype(str)
    if bad_s.any():
        errors.append(f"shifts end<=start: {int(bad_s.sum())}")

    # duplikat unik (emp,date,start)
    if s.duplicated(["employee_id", "date", "start_time"]).any():
        errors.append("shifts: duplikat (employee,date,start)")

    # 1 absensi per pegawai per tanggal
    if df["attendance"].duplicated(["employee_id", "date"]).any():
        errors.append("attendance: duplikat (employee,date)")

    report = {"tables": {t: len(df[t]) for t in df}, "errors": errors}
    if errors:
        raise SystemExit("QUALITY FAIL: " + "; ".join(errors))
    return report
