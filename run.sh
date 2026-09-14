#!/usr/bin/env bash
# Full pipeline vs MySQL scratch (butuh: docker mysql + migrate + seed + demo_data).
# Kredensial via env SB_* (default throwaway lokal, lihat README).
set -euo pipefail
cd "$(dirname "$0")"
python3 run.py
