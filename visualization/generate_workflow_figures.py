"""
generate_workflow_figures.py
Generates three assembly and annotation summary figures:
  - Figure 1: Cumulative assembly length plot
  - Figure 2: Genomic feature distribution (CDS, tRNA, rRNA)
  - Figure 3: Key assembly metrics from QUAST
Works standalone or when called from RUN_PIPELINE.sh (uses PROJECT_ROOT env var).
"""

import os
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# ── Project Root Resolution ────────────────────────────────────────────────────
_env_root = os.environ.get("PROJECT_ROOT", "")
if _env_root:
    PROJECT_ROOT = Path(_env_root).resolve()
else:
    # visualization/generate_workflow_figures.py → parents[1] = PROJECT_ROOT
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

RESULTS_DIR  = PROJECT_ROOT / "results"
FIGURES_DIR  = RESULTS_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

ACCESSION_FILE = PROJECT_ROOT / "data" / "accession.txt"
SRA_ID = ACCESSION_FILE.read_text().strip().splitlines()[0]

QUAST_REPORT    = RESULTS_DIR / "quast" / "report.tsv"
ANNOTATION_TXT  = RESULTS_DIR / "annotation" / SRA_ID / f"{SRA_ID}.txt"
FNA_FILE        = RESULTS_DIR / "annotation" / SRA_ID / f"{SRA_ID}.fna"

# ── Style ──────────────────────────────────────────────────────────────────────
plt.style.use("seaborn-v0_8-muted")
PRIMARY   = "#3498db"
SECONDARY = "#2ecc71"
ACCENT    = "#e74c3c"

# ── Figure 1: Cumulative Assembly Length ──────────────────────────────────────
print(f"[1/3] Generating Assembly Cumulative Plot for {SRA_ID}...")
contig_lengths = []
if FNA_FILE.exists():
    current_len = 0
    with open(FNA_FILE) as fh:
        for line in fh:
            if line.startswith(">"):
                if current_len > 0:
                    contig_lengths.append(current_len)
                current_len = 0
            else:
                current_len += len(line.strip())
    if current_len > 0:
        contig_lengths.append(current_len)
else:
    print(f"  WARNING: {FNA_FILE} not found — plot will be empty.")

contig_lengths.sort(reverse=True)
cumulative   = np.cumsum(contig_lengths) if contig_lengths else np.array([])
contig_count = np.arange(1, len(contig_lengths) + 1)

fig, ax = plt.subplots(figsize=(10, 6))
if len(contig_count) > 0:
    ax.plot(contig_count, cumulative, marker="o", linestyle="-", color=PRIMARY, markersize=4)
    ax.fill_between(contig_count, cumulative, color=PRIMARY, alpha=0.2)
ax.set_xlabel("Contig Count (sorted by length)")
ax.set_ylabel("Cumulative Assembly Length (bp)")
ax.set_title(f"Cumulative Assembly Length — {SRA_ID}")
ax.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
out1 = FIGURES_DIR / "figure1_assembly_cumulative.png"
plt.savefig(out1, dpi=300)
plt.close()
print(f"  Saved → {out1}")

# ── Figure 2: Annotation Feature Distribution ─────────────────────────────────
print("[2/3] Generating Annotation Summary Plot...")
features: dict = {}
if ANNOTATION_TXT.exists():
    with open(ANNOTATION_TXT) as fh:
        for line in fh:
            if ":" in line:
                key, val = line.split(":", 1)
                key = key.strip()
                if key in ("CDS", "tRNA", "rRNA", "tmRNA"):
                    try:
                        features[key] = int(val.strip())
                    except ValueError:
                        pass
else:
    print(f"  WARNING: {ANNOTATION_TXT} not found — using zeros.")
    features = {"CDS": 0, "tRNA": 0, "rRNA": 0}

labels = list(features.keys())
counts = list(features.values())
colors = [PRIMARY, SECONDARY, ACCENT, "#f1c40f"][: len(labels)]

fig, ax = plt.subplots(figsize=(10, 6))
if counts:
    bars = ax.bar(labels, counts, color=colors)
    ax.set_ylabel("Count")
    ax.set_title(f"Distribution of Genomic Features — {SRA_ID}")
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 5,
                str(int(h)), ha="center", va="bottom", fontweight="bold")
plt.tight_layout()
out2 = FIGURES_DIR / "figure2_annotation_summary.png"
plt.savefig(out2, dpi=300)
plt.close()
print(f"  Saved → {out2}")

# ── Figure 3: Key Assembly Metrics (QUAST) ────────────────────────────────────
print("[3/3] Generating QUAST Metrics Plot...")
metrics: dict = {}
if QUAST_REPORT.exists():
    df_q = pd.read_csv(QUAST_REPORT, sep="\t", index_col=0)
    col  = df_q.columns[0]
    try:
        metrics["Total Length (Mb)"] = float(df_q.loc["Total length", col]) / 1e6
        metrics["N50 (kb)"]          = float(df_q.loc["N50",          col]) / 1e3
        metrics["L50"]               = float(df_q.loc["L50",          col])
        metrics["GC (%)"]            = float(df_q.loc["GC (%)",       col])
    except KeyError as e:
        print(f"  WARNING: QUAST metric not found: {e}")
else:
    print(f"  WARNING: {QUAST_REPORT} not found — using zeros.")
    metrics = {"Total Length (Mb)": 0, "N50 (kb)": 0, "L50": 0, "GC (%)": 0}

fig, ax = plt.subplots(figsize=(10, 6))
names  = list(metrics.keys())
values = list(metrics.values())
ax.barh(names, values, color=SECONDARY)
ax.set_title(f"Key Assembly Metrics — {SRA_ID}")
max_v = max(values) if values else 1
for i, v in enumerate(values):
    ax.text(v + max_v * 0.01, i, f"{v:.2f}", va="center", fontweight="bold")
plt.tight_layout()
out3 = FIGURES_DIR / "figure3_workflow_summary.png"
plt.savefig(out3, dpi=300)
plt.close()
print(f"  Saved → {out3}")

print("Workflow figures complete.")
