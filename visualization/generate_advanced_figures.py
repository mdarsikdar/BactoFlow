"""
generate_advanced_figures.py
Generates two downstream analysis figures:
  - Figure 7: ABRicate AMR/Virulence/Plasmid screening profile
               (reads counts DYNAMICALLY from actual TSV files)
  - Figure 8: PADLOC defense system distribution (pie chart)
Works standalone or when called from RUN_PIPELINE.sh (uses PROJECT_ROOT env var).
"""

import os
import glob
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# ── Project Root Resolution ────────────────────────────────────────────────────
_env_root = os.environ.get("PROJECT_ROOT", "")
if _env_root:
    PROJECT_ROOT = Path(_env_root).resolve()
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

RESULTS_DIR    = PROJECT_ROOT / "results"
FIGURES_DIR    = RESULTS_DIR / "figures"
DOWNSTREAM_DIR = RESULTS_DIR / "downstream"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

plt.style.use("seaborn-v0_8-muted")
PRIMARY   = "#34495e"
SECONDARY = "#e67e22"
ACCENT    = "#27ae60"

# ── Figure 7: ABRicate Screening Profile ──────────────────────────────────────
print("[1/2] Generating Advanced Screening Figure (ABRicate)...")

abricate_dir   = DOWNSTREAM_DIR / "abricate"
abricate_files = sorted(glob.glob(str(abricate_dir / "abricate_*.tsv")))

db_counts: dict = {}
if abricate_files:
    for f in abricate_files:
        db_name = Path(f).stem.replace("abricate_", "")
        try:
            df = pd.read_csv(f, sep="\t")
            count = len(df)
        except Exception:
            count = 0
        # Format display name
        label = f"{db_name.upper()}"
        db_counts[label] = count
else:
    print(f"  WARNING: No ABRicate TSV files found in {abricate_dir}")
    print("  Using placeholder zeros for figure.")
    db_counts = {
        "CARD": 0, "RESFINDER": 0, "VFDB": 0,
        "PLASMIDFINDER": 0, "MEGARES": 0, "ARGANNOT": 0, "NCBI": 0
    }

names  = list(db_counts.keys())
values = list(db_counts.values())
colors = [
    SECONDARY if any(k in n for k in ("CARD", "MEGARES", "RESFINDER", "ARGANNOT", "NCBI"))
    else ACCENT if "VFDB" in n
    else PRIMARY
    for n in names
]

fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.bar(names, values, color=colors)
ax.set_xticks(range(len(names)))
ax.set_xticklabels(names, rotation=45, ha="right")
ax.set_ylabel("Number of Genes Identified")
ax.set_title("Genomic Screening Profile: AMR, Virulence, and Plasmids")
for bar in bars:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, h + 0.5,
            str(int(h)), ha="center", va="bottom", fontweight="bold")
plt.tight_layout()
out7 = FIGURES_DIR / "figure7_advanced_screening.png"
plt.savefig(out7, dpi=300)
plt.close()
print(f"  Saved → {out7}")

# ── Figure 8: PADLOC Defense System Pie ───────────────────────────────────────
print("[2/2] Generating Defense System Figure (PADLOC)...")
padloc_csv = DOWNSTREAM_DIR / "padloc" / "scaffolds_padloc.csv"

if padloc_csv.exists():
    df_pad = pd.read_csv(padloc_csv)
    if not df_pad.empty:
        system_counts = df_pad["system"].value_counts()
        fig, ax = plt.subplots(figsize=(10, 8))
        palette = sns.color_palette("viridis", len(system_counts))
        ax.pie(system_counts.values, labels=system_counts.index,
               autopct="%1.1f%%", colors=palette)
        ax.set_title("Distribution of Identified Bacterial Defense Systems (PADLOC)")
        plt.tight_layout()
        out8 = FIGURES_DIR / "figure8_defense_systems.png"
        plt.savefig(out8, dpi=300)
        plt.close()
        print(f"  Saved → {out8}")
    else:
        print("  INFO: PADLOC CSV is empty — no defense systems found.")
else:
    print(f"  INFO: PADLOC CSV not found: {padloc_csv}")

print("Advanced figures complete.")
