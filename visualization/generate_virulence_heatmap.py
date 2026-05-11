"""
generate_virulence_heatmap.py
Generates Figure 4: Virulence Factor Heatmap from VFDB results.
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

RESULTS_DIR    = PROJECT_ROOT / "results"
FIGURES_DIR    = RESULTS_DIR / "figures"
ABRICATE_DIR   = RESULTS_DIR / "downstream" / "abricate"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ── Aesthetic Configuration ───────────────────────────────────────────────────
plt.style.use("seaborn-v0_8-muted")
VIR_PALETTE = sns.color_palette("GnBu", as_cmap=True)
PRIMARY = "#34495e"

def generate_mock_vfdb():
    print("  INFO: Generating mock VFDB data...")
    ABRICATE_DIR.mkdir(parents=True, exist_ok=True)
    rows = [
        {"GENE": "hlyA", "%IDENTITY": 99.5, "PRODUCT": "Hemolysin A"},
        {"GENE": "cnf1", "%IDENTITY": 100.0, "PRODUCT": "Cytotoxic necrotizing factor 1"},
        {"GENE": "fyuA", "%IDENTITY": 98.2, "PRODUCT": "Yersiniabactin receptor"},
        {"GENE": "aer", "%IDENTITY": 95.0, "PRODUCT": "Aerobactin receptor"},
        {"GENE": "iutA", "%IDENTITY": 100.0, "PRODUCT": "Ferric aerobactin receptor"}
    ]
    pd.DataFrame(rows).to_csv(ABRICATE_DIR / "abricate_vfdb.tsv", sep="\t", index=False)

def main():
    parser = argparse.ArgumentParser(description="Generate Virulence Heatmap")
    parser.add_argument("--mock", action="store_true", help="Use mock data")
    args = parser.parse_args()

    vfdb_file = ABRICATE_DIR / "abricate_vfdb.tsv"
    
    if not vfdb_file.exists():
        if args.mock: generate_mock_vfdb()
        else:
            print(f"  ERROR: {vfdb_file} not found.")
            return

    print("=== Generating Figure 4: Virulence Factor Heatmap ===")
    try:
        df = pd.read_csv(vfdb_file, sep="\t")
        if df.empty:
            print("  INFO: No virulence factors found.")
            return
            
        # Normalize gene names and deduplicate (take max identity)
        df["GENE"] = df["GENE"].str.upper()
        df = df.groupby("GENE").agg({"%IDENTITY": "max"}).reset_index()
        
        # Sort by Identity then Gene name
        df = df.sort_values(["%IDENTITY", "GENE"], ascending=[False, True])
        
        # Prepare for heatmap
        plot_df = df.set_index("GENE")[["%IDENTITY"]]
        
        # Dynamic height based on number of genes
        fig_height = max(8, len(plot_df) * 0.35)
        plt.figure(figsize=(12, fig_height))
        
        ax = sns.heatmap(
            plot_df, 
            annot=True, 
            fmt=".1f", 
            cmap=VIR_PALETTE, 
            linewidths=.5,
            cbar_kws={'label': '% Identity'}, 
            vmin=80, vmax=100
        )
        
        plt.title("Identified Virulence Factors (VFDB)", fontsize=22, fontweight="bold", pad=25)
        plt.ylabel("Virulence Gene", fontsize=16, fontweight="bold", labelpad=15)
        plt.xlabel("", fontsize=1) 
        
        plt.tight_layout()
        out = FIGURES_DIR / "figure04_virulence_heatmap.png"
        plt.savefig(out, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"  ✔ Saved → {out}")
        print(f"  Summary: {len(plot_df)} virulence factors visualized.")
    except Exception as e:
        print(f"  ERROR: {e}")

if __name__ == "__main__":
    main()
