"""
generate_mapping_vcf_figures.py
Generates three variant-analysis figures from the FreeBayes VCF output:
  - Figure 4: Variant density across the genome
  - Figure 5: Variant type distribution (Transitions vs Transversions)
  - Figure 6: Variant quality score histogram
Works standalone or when called from RUN_PIPELINE.sh (uses PROJECT_ROOT env var).
"""

import os
import gzip
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# ── Project Root Resolution ────────────────────────────────────────────────────
_env_root = os.environ.get("PROJECT_ROOT", "")
if _env_root:
    PROJECT_ROOT = Path(_env_root).resolve()
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

SRA_ID  = (PROJECT_ROOT / "data" / "accession.txt").read_text().strip().splitlines()[0]
VCF_FILE = RESULTS_DIR / "vcf" / f"{SRA_ID}.vcf.gz"

plt.style.use("seaborn-v0_8-muted")
PRIMARY   = "#3498db"
SECONDARY = "#2ecc71"
ACCENT    = "#e74c3c"

# ── Parse VCF ─────────────────────────────────────────────────────────────────
print(f"Parsing VCF: {VCF_FILE}")
positions: list     = []
qualities: list     = []
substitutions: list = []

if VCF_FILE.exists():
    with gzip.open(VCF_FILE, "rt") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 6:
                continue
            pos = int(parts[1])
            ref = parts[3]
            alt = parts[4]
            try:
                qual = float(parts[5])
            except ValueError:
                qual = 0.0
            positions.append(pos)
            qualities.append(qual)
            if len(ref) == 1 and len(alt) == 1:
                substitutions.append(f"{ref}>{alt}")
else:
    print(f"  WARNING: VCF file not found: {VCF_FILE}")

# ── Figure 4: Variant Density ─────────────────────────────────────────────────
print("[1/3] Generating Variant Density Plot...")
if positions:
    ref_length  = max(positions) + 100_000
    window_size = 50_000
    bins = np.arange(0, ref_length + window_size, window_size)
    hist, _ = np.histogram(positions, bins=bins)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(bins[:-1] / 1e6, hist, color=PRIMARY, linewidth=2)
    ax.fill_between(bins[:-1] / 1e6, hist, color=PRIMARY, alpha=0.2)
    ax.set_xlabel("Genomic Position (Mb)")
    ax.set_ylabel(f"Variant Count (per {window_size // 1000} kb window)")
    ax.set_title(f"Variant Density across Genome — {SRA_ID}")
    ax.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    out4 = FIGURES_DIR / "figure4_variant_density.png"
    plt.savefig(out4, dpi=300)
    plt.close()
    print(f"  Saved → {out4}")
else:
    print("  Skipped (no variant data).")

# ── Figure 5: Transition / Transversion ───────────────────────────────────────
print("[2/3] Generating Variant Type Plot...")
if substitutions:
    transitions  = {"A>G", "G>A", "C>T", "T>C"}
    transversions = {"A>C", "A>T", "C>A", "C>G", "G>C", "G>T", "T>A", "T>G"}
    ti_count = sum(1 for s in substitutions if s in transitions)
    tv_count = sum(1 for s in substitutions if s in transversions)
    ratio    = ti_count / tv_count if tv_count > 0 else 0

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(["Transitions (Ti)", "Transversions (Tv)"],
           [ti_count, tv_count], color=[SECONDARY, ACCENT])
    ax.set_ylabel("Count")
    ax.set_title(f"Variant Type Distribution  (Ti/Tv = {ratio:.2f}) — {SRA_ID}")
    for i, v in enumerate([ti_count, tv_count]):
        ax.text(i, v + 1, str(v), ha="center", va="bottom", fontweight="bold")
    plt.tight_layout()
    out5 = FIGURES_DIR / "figure5_variant_types.png"
    plt.savefig(out5, dpi=300)
    plt.close()
    print(f"  Saved → {out5}")
else:
    print("  Skipped (no substitution data).")

# ── Figure 6: Variant Quality Histogram ───────────────────────────────────────
print("[3/3] Generating Variant Quality Plot...")
if qualities:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(qualities, bins=50, color="#9b59b6", alpha=0.7, edgecolor="black")
    ax.set_xlabel("Phred-scaled Quality Score")
    ax.set_ylabel("Frequency")
    ax.set_title(f"Distribution of Variant Quality Scores — {SRA_ID}")
    ax.set_yscale("log")
    ax.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    out6 = FIGURES_DIR / "figure6_variant_quality.png"
    plt.savefig(out6, dpi=300)
    plt.close()
    print(f"  Saved → {out6}")
else:
    print("  Skipped (no quality data).")

print("Mapping & VCF figures complete.")
