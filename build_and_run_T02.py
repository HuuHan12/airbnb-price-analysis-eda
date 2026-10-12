# -*- coding: utf-8 -*-
"""
Master runner for Giai đoạn 1 (IE313):
Task T02 (Data Ingestion & Quality Audit) and Task T03 (Data Dictionary & Redundancy Audit).
Directly executes build_and_run_T03.py to ensure consistency.
"""

import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

script_dir = Path(__file__).resolve().parent
t03_script = script_dir / "build_and_run_T03.py"

print(f"Executing Phase 1 pipeline via: {t03_script.name}")
result = subprocess.run([sys.executable, str(t03_script)], check=True)
sys.exit(result.returncode)
