"""
generate_amr_heatmap.py
Generates Figure 2: AMR Gene Heatmap comparing results across multiple databases.
Focuses on AMR genes only (CARD, ResFinder, MegaRes, ArgAnnot, NCBI).
"""

import os
import glob
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np

# ── Project Root Resolution ────────────────────────────────────────────────────
_env_root = os.environ.get("PROJECT_ROOT", "")
if _env_root:
    PROJECT_ROOT = Path(_env_root).resolve()
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

RESULTS_DIR    = PROJECT_ROOT / "results"
FIGURES_DIR    = RESULTS_DIR / "figures"
DOWNSTREAM_DIR = RESULTS_DIR / "downstream"
ABRICATE_DIR   = DOWNSTREAM_DIR / "abricate"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ── Aesthetic Configuration ───────────────────────────────────────────────────
plt.style.use("seaborn-v0_8-muted")
sns.set_context("talk")
AMR_PALETTE = sns.color_palette("YlOrRd", as_cmap=True)

def generate_mock_data():
    """Generates mock ABRicate TSV files for testing if no real data exists."""
    print("  INFO: No real ABRicate data found. Generating mock data for visualization demo...")
    ABRICATE_DIR.mkdir(parents=True, exist_ok=True)
    
    mock_genes = {
        "card": [("blaKPC-2", 100.0, 100.0), ("tet(A)", 98.5, 100.0), ("aac(6')-Ib-cr", 99.2, 95.0)],
        "resfinder": [("blaKPC-2", 100.0, 100.0), ("tet(A)", 99.0, 100.0), ("sul1", 100.0, 100.0)],
        "megares": [("KPC", 95.0, 100.0), ("TETRACYCLINE", 92.0, 98.0), ("SULPHONAMIDE", 100.0, 100.0)],
        "ncbi": [("blaKPC-2", 100.0, 100.0), ("tet(A)", 98.5, 100.0), ("sul1", 100.0, 100.0), ("mph(A)", 97.0, 100.0)],
        "argannot": [("blaKPC-2", 100.0, 100.0), ("tet(A)", 98.5, 100.0)]
    }
    
    for db, genes in mock_genes.items():
        rows = []
        for g, pid, cov in genes:
            rows.append({
                "#FILE": "mock_assembly.fasta",
                "SEQUENCE": "scaffold_1",
                "START": 100,
                "END": 1000,
                "STRAND": "+",
                "GENE": g,
                "COVERAGE": cov,
                "COVERAGE_MAP": "1-900/900",
                "GAPS": "0",
                "%COVERAGE": cov,
                "%IDENTITY": pid,
                "DATABASE": db,
                "ACCESSION": "MOCK001",
                "PRODUCT": f"Mock {g} gene",
                "RESISTANCE": "Mock Resistance"
            })
        df = pd.DataFrame(rows)
        df.to_csv(ABRICATE_DIR / f"abricate_{db}.tsv", sep="\t", index=False)

def main():
    parser = argparse.ArgumentParser(description="Generate AMR Gene Heatmap")
    parser.add_argument("--mock", action="store_true", help="Use mock data if real data is missing")
    args = parser.parse_args()

    print("=== Generating Figure 2: AMR Gene Heatmap ===")

    # 1. Collect ABRicate files
    amr_databases = ["card", "resfinder", "megares", "argannot", "ncbi"]
    abricate_files = []
    for db in amr_databases:
        f = ABRICATE_DIR / f"abricate_{db}.tsv"
        if f.exists():
            abricate_files.append(f)

    if not abricate_files:
        if args.mock:
            generate_mock_data()
            for db in amr_databases:
                f = ABRICATE_DIR / f"abricate_{db}.tsv"
                if f.exists():
                    abricate_files.append(f)
        else:
            print(f"  ERROR: No ABRicate TSV files found in {ABRICATE_DIR}")
            print("  Run step 9 first, or use --mock to generate a demo figure.")
            return

    # 2. Load and Aggregate Data
    all_data = []
    for f in abricate_files:
        try:
            df = pd.read_csv(f, sep="\t")
            if not df.empty:
                db_name = f.stem.replace("abricate_", "").upper()
                df["DB_DISPLAY"] = db_name
                # We only need Gene and Identity for the heatmap
                # Normalize gene names to uppercase for case-insensitive comparison
                df["GENE"] = df["GENE"].str.upper()
                all_data.append(df[["GENE", "DB_DISPLAY", "%IDENTITY"]])
        except Exception as e:
            print(f"  WARNING: Could not read {f.name}: {e}")

    if not all_data:
        print("  INFO: No AMR genes found in any database.")
        return

    combined_df = pd.concat(all_data, ignore_index=True)

    # 3. Create Pivot Table (Heatmap Matrix)
    # Rows: GENE, Columns: DATABASE, Values: %IDENTITY
    # If a gene is found multiple times in a DB, take the max identity
    heatmap_df = combined_df.pivot_table(
        index="GENE", 
        columns="DB_DISPLAY", 
        values="%IDENTITY", 
        aggfunc="max"
    )

    # Fill NaN with 0 for the heatmap
    plot_df = heatmap_df.fillna(0)

    # 4. Plotting
    plt.figure(figsize=(14, max(8, len(plot_df) * 0.4)))
    
    # Custom annotation: only show text if value > 0
    annot = plot_df.map(lambda v: f"{v:.1f}" if v > 0 else "")

    ax = sns.heatmap(
        plot_df,
        annot=annot,
        fmt="",
        cmap=AMR_PALETTE,
        linewidths=.5,
        cbar_kws={'label': '% Identity'},
        vmin=80, vmax=100  # Focused range for biological relevance
    )

    plt.title("AMR Gene Detection Across Different Databases", fontsize=20, pad=20, fontweight="bold")
    plt.xlabel("Reference Database", fontsize=16, labelpad=10)
    plt.ylabel("AMR Gene Name", fontsize=16, labelpad=10)
    
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    # 5. Save Output
    out_path = FIGURES_DIR / "figure02_amr_heatmap.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    
    print(f"  ✔ Heatmap saved to: {out_path}")
    print(f"  Summary: {len(plot_df)} genes detected across {len(abricate_files)} databases.")

if __name__ == "__main__":
    main()
