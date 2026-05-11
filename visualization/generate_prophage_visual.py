"""
generate_prophage_visual.py
Generates Figure 5: Prophage Genomic Map from PhiSpy results.
"""

import os
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# ── Project Root Resolution ────────────────────────────────────────────────────
_env_root = os.environ.get("PROJECT_ROOT", "")
if _env_root:
    PROJECT_ROOT = Path(_env_root).resolve()
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"
PHISPY_DIR  = RESULTS_DIR / "downstream" / "phispy"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ── Aesthetic Configuration ───────────────────────────────────────────────────
plt.style.use("seaborn-v0_8-muted")
PRIMARY = "#34495e"
PHAGE_COLOR = "#9b59b6"  # Purple

def generate_mock_phispy():
    print("  INFO: Generating mock PhiSpy data...")
    PHISPY_DIR.mkdir(parents=True, exist_ok=True)
    content = "Prophage_1\tscaffold_1\t50000\t85000\nProphage_2\tscaffold_1\t1200000\t1245000\nProphage_3\tscaffold_1\t2500000\t2530000\n"
    (PHISPY_DIR / "prophage_coordinates.tsv").write_text(content)

def main():
    parser = argparse.ArgumentParser(description="Generate Prophage Map")
    parser.add_argument("--mock", action="store_true", help="Use mock data")
    args = parser.parse_args()

    phispy_file = PHISPY_DIR / "prophage_coordinates.tsv"
    
    if not phispy_file.exists():
        if args.mock: generate_mock_phispy()
        else:
            print(f"  ERROR: {phispy_file} not found.")
            return

    print("=== Generating Figure 5: Prophage Genomic Map ===")
    try:
        # PhiSpy TSV: ID, Contig, Start, End + other columns
        df = pd.read_csv(phispy_file, sep="\t", header=None, 
                         names=["ID", "Contig", "Start", "End"], 
                         usecols=[0, 1, 2, 3])
        
        if df.empty:
            print("  INFO: No prophages found.")
            return

        # Ensure numeric
        df["Start"] = pd.to_numeric(df["Start"])
        df["End"] = pd.to_numeric(df["End"])

        genome_size = df["End"].max() + 500_000
        
        fig, ax = plt.subplots(figsize=(15, 4))
        
        # Draw Genome Line
        ax.hlines(1, 0, genome_size, colors=PRIMARY, linewidth=3, alpha=0.3)
        
        # Draw Prophages
        for idx, row in df.iterrows():
            ax.broken_barh([(row["Start"], row["End"] - row["Start"])], (0.8, 0.4), 
                           facecolors=PHAGE_COLOR, edgecolor="white", label="Prophage" if idx == 0 else "")
            # Label
            ax.text((row["Start"] + row["End"])/2, 1.25, row["ID"], 
                    ha="center", va="bottom", fontsize=10, fontweight="bold", color=PHAGE_COLOR)

        ax.set_ylim(0, 2)
        ax.set_yticks([])
        ax.set_xlabel("Genomic Position (bp)", fontsize=14, fontweight="bold")
        ax.set_title("Identified Prophage Regions across Genome (PhiSpy)", fontsize=18, fontweight="bold", pad=20)
        
        # Set x-axis labels to Mb
        ticks = ax.get_xticks()
        ax.set_xticklabels([f"{t/1e6:.1f} Mb" for t in ticks])
        
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        
        plt.tight_layout()
        out = FIGURES_DIR / "figure05_prophage_map.png"
        plt.savefig(out, dpi=300)
        plt.close()
        print(f"  ✔ Saved → {out}")
    except Exception as e:
        print(f"  ERROR: {e}")

if __name__ == "__main__":
    main()
