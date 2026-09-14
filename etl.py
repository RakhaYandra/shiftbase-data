"""Extract read-only dari MySQL scratch. DSN via env SB_DSN."""
import os

TABLES = ["employees", "shifts", "attendance"]


def dsn() -> dict:
    # format: host,port,user,pass,db (tanpa kredensial di repo)
    return {
        "host": os.environ.get("SB_HOST", "127.0.0.1"),
        "port": int(os.environ.get("SB_PORT", "13307")),
        "user": os.environ.get("SB_USER", "shift"),
        "password": os.environ.get("SB_PASS", "shiftpass"),
        "database": os.environ.get("SB_DB", "shiftbase_data"),
    }


def extract(d=None) -> dict:
    import pandas as pd
    import pymysql
    d = d or dsn()
    con = pymysql.connect(**d, read_timeout=10)
    try:
        out = {}
        for t in TABLES:
            out[t] = pd.read_sql(f"SELECT * FROM {t}", con)
    finally:
        con.close()
    return out
