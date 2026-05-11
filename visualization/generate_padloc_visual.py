"""
generate_padloc_visual.py
Generates Figure 6: PADLOC Defense System Analysis.
"""

import os
import argparse
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

RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"
PADLOC_DIR  = RESULTS_DIR / "downstream" / "padloc"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ── Aesthetic Configuration ───────────────────────────────────────────────────
plt.style.use("seaborn-v0_8-muted")
ACCENT = "#27ae60" # Green

def generate_mock_padloc():
    print("  INFO: Generating mock PADLOC data...")
    PADLOC_DIR.mkdir(parents=True, exist_ok=True)
    rows = [
        {"system": "CRISPR-Cas", "target": "Type I-E"},
        {"system": "CRISPR-Cas", "target": "Type I-E"},
        {"system": "RM", "target": "Type II"},
        {"system": "RM", "target": "Type I"},
        {"system": "RM", "target": "Type I"},
        {"system": "RM", "target": "Type I"},
        {"system": "Abortive Infection", "target": "AbiK"},
        {"system": "BREX", "target": "Type I"},
        {"system": "DISARM", "target": "Type I"}
    ]
    pd.DataFrame(rows).to_csv(PADLOC_DIR / "scaffolds_padloc.csv", index=False)

def main():
    parser = argparse.ArgumentParser(description="Generate PADLOC Analysis")
    parser.add_argument("--mock", action="store_true", help="Use mock data")
    args = parser.parse_args()

    padloc_file = PADLOC_DIR / "scaffolds_padloc.csv"
    
    if not padloc_file.exists():
        if args.mock: generate_mock_padloc()
        else:
            print(f"  ERROR: {padloc_file} not found.")
            return

    print("=== Generating Figure 6: PADLOC Defense Systems ===")
    try:
        df = pd.read_csv(padloc_file)
        if df.empty:
            print("  INFO: No defense systems found.")
            return

        system_counts = df["system"].value_counts()
        
        plt.figure(figsize=(12, 7))
        ax = sns.barplot(x=system_counts.index, y=system_counts.values, palette="viridis")
        
        plt.title("Bacterial Defense System Prevalence (PADLOC)", fontsize=18, fontweight="bold", pad=20)
        plt.xlabel("Defense System", fontsize=14, fontweight="bold")
        plt.ylabel("Gene Count", fontsize=14, fontweight="bold")
        plt.xticks(rotation=45, ha="right")
        
        # Add labels
        for p in ax.patches:
            ax.annotate(f'{int(p.get_height())}', 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha = 'center', va = 'center', 
                        xytext = (0, 9), 
                        textcoords = 'offset points',
                        fontweight='bold')

        plt.tight_layout()
        out = FIGURES_DIR / "figure06_padloc_systems.png"
        plt.savefig(out, dpi=300)
        plt.close()
        print(f"  ✔ Saved → {out}")
    except Exception as e:
        print(f"  ERROR: {e}")

if __name__ == "__main__":
    main()
