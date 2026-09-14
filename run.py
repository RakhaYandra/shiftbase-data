"""Orkestrasi: extract -> quality -> marts -> cross-check API -> charts."""
import json
import urllib.request

import charts as C
import etl
import marts as M
import quality as Q

API = "http://localhost:18092"


def api_overtime(token):
    req = urllib.request.Request(
        f"{API}/v1/reports/overtime?from=2026-09-01&to=2026-10-31",
        headers={"Authorization": "Bearer " + token})
    with urllib.request.urlopen(req, timeout=10) as r:
        return {o["employee_id"]: o["overtime_hours"] for o in json.load(r)}


def main():
    import os
    df = etl.extract()
    report = Q.check(df)
    names = dict(zip(df["employees"]["id"], df["employees"]["name"]))
    marts = M.build(df, names)
    M.save(marts)
    C.all_charts(marts)

    mine = (marts["overtime_employee"].set_index("employee_id")["overtime_hours"].to_dict())
    try:
        tok = json.load(urllib.request.urlopen(urllib.request.Request(
            f"{API}/v1/auth/login",
            data=json.dumps({"email": "admin@shiftbase.local",
                             "password": os.environ.get("SB_PASS_ADMIN", "Admin123!")}).encode(),
            headers={"Content-Type": "application/json"}), timeout=10))["token"]
        theirs = api_overtime(tok)
        match = all(abs(mine.get(k, 0) - v) < 0.01 for k, v in theirs.items())
        print(f"cross-check API overtime: {'MATCH' if match else 'MISMATCH'} "
              f"(pipeline={mine} api={theirs})")
    except Exception as e:  # API opsional (butuh server + seed yang sama)
        print(f"cross-check skip: {e}")

    open("work/quality_report.json", "w").write(json.dumps(report, indent=1))
    ot = marts["overtime_employee"].sort_values("overtime_hours", ascending=False).iloc[0]
    late = marts["late_arrivals"].sort_values("late_min", ascending=False)
    top_late = late.iloc[0] if len(late) else None
    print(f"insight: lembur top {ot['name']} {ot['overtime_hours']:.1f}h; "
          f"telat max {top_late['name'] + ' +' + str(int(top_late['late_min'])) + 'm' if top_late is not None else '-'}; "
          f"coverage min {marts['coverage_daily']['headcount'].min()}")
    print("OK: quality_report.json + 5 marts + 4 charts")


if __name__ == "__main__":
    main()
