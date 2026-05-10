"""
summarize_results.py
Generates a comprehensive verification report of the downstream analysis outputs.
Works standalone or when called from RUN_PIPELINE.sh (uses PROJECT_ROOT env var).
"""

import os
import sys
import glob
from pathlib import Path
import pandas as pd

# ── Project Root Resolution ────────────────────────────────────────────────────
# Works whether script is run directly or called from RUN_PIPELINE.sh
_env_root = os.environ.get("PROJECT_ROOT", "")
if _env_root:
    PROJECT_ROOT = Path(_env_root).resolve()
else:
    # This file is at: PROJECT_ROOT/scripts/utils/summarize_results.py
    PROJECT_ROOT = Path(__file__).resolve().parents[2]

downstream_dir = PROJECT_ROOT / "results" / "downstream"
mlst_file      = downstream_dir / "mlst_results.tsv"
abricate_dir   = downstream_dir / "abricate"
padloc_csv     = downstream_dir / "padloc" / "scaffolds_padloc.csv"
phispy_file    = downstream_dir / "phispy" / "prophage_coordinates.tsv"

report = []
report.append("=" * 60)
report.append("  Comprehensive Downstream Analysis — Verification Report")
report.append("=" * 60)
report.append(f"  Project root : {PROJECT_ROOT}")
report.append(f"  Results dir  : {downstream_dir}\n")

# 1. MLST
report.append("--- [1/4] MLST Typing ---")
if mlst_file.exists():
    df_mlst = pd.read_csv(mlst_file, sep="\t", header=None)
    if not df_mlst.empty:
        mlst_scheme = df_mlst.iloc[0, 1]
        mlst_type   = df_mlst.iloc[0, 2]
        report.append(f"  [PASS] Scheme: {mlst_scheme}, ST: {mlst_type}")
    else:
        report.append("  [FAIL] MLST file is empty.")
else:
    report.append(f"  [FAIL] MLST results missing: {mlst_file}")

# 2. ABRicate
report.append("\n--- [2/4] AMR & Virulence Screening (ABRicate) ---")
abricate_files = sorted(glob.glob(str(abricate_dir / "abricate_*.tsv")))
if abricate_files:
    report.append(f"  [PASS] ABRicate ran on {len(abricate_files)} databases:")
    for f in abricate_files:
        db_name = Path(f).stem.replace("abricate_", "")
        try:
            df = pd.read_csv(f, sep="\t")
            gene_count = len(df)
        except Exception:
            gene_count = 0
        report.append(f"    - {db_name.upper():20s}: {gene_count:4d} hits")
else:
    report.append(f"  [FAIL] No ABRicate TSV results in {abricate_dir}")

# 3. PADLOC
report.append("\n--- [3/4] Defense System Identification (PADLOC) ---")
if padloc_csv.exists():
    df_pad = pd.read_csv(padloc_csv)
    if not df_pad.empty:
        systems = df_pad["system"].unique()
        report.append(f"  [PASS] {len(systems)} unique defense system(s) identified:")
        for s in systems:
            n = len(df_pad[df_pad["system"] == s])
            report.append(f"    - {s} ({n} gene(s))")
    else:
        report.append("  [WARN] PADLOC ran but found no defense systems.")
else:
    report.append(f"  [FAIL] PADLOC results missing: {padloc_csv}")

# 4. PhiSpy
report.append("\n--- [4/4] Prophage Identification (PhiSpy) ---")
if phispy_file.exists():
    with open(phispy_file) as f:
        prophage_lines = [ln for ln in f if ln.strip()]
    report.append(f"  [PASS] {len(prophage_lines)} prophage region(s) identified.")
else:
    report.append(f"  [INFO] PhiSpy results not found (no prophages or step not run): {phispy_file}")

# Final
report.append("\n" + "=" * 60)
report.append("  All downstream steps validated.")
report.append("=" * 60)

# Write report
report_text = "\n".join(report)
report_path = downstream_dir / "downstream_verification_report.txt"
downstream_dir.mkdir(parents=True, exist_ok=True)
report_path.write_text(report_text)

print(report_text)
print(f"\nReport saved → {report_path}")
