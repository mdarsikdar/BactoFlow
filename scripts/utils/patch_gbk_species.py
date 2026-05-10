"""
patch_gbk_species.py
Reads MLST results and patches the Prokka GenBank file with the correct species name.
Replaces "Genus species strain strain" with the identified species.
"""

import sys
import os
from pathlib import Path

def patch_gbk(gbk_path, mlst_path):
    if not Path(gbk_path).exists():
        print(f"  [SKIP] GBK not found: {gbk_path}")
        return
    if not Path(mlst_path).exists():
        print(f"  [SKIP] MLST not found: {mlst_path}")
        return

    # 1. Get species from MLST
    # Format: sample_id  scheme  st  ...
    species = "Bacterium"
    with open(mlst_path) as f:
        line = f.readline()
        if line:
            parts = line.strip().split("\t")
            if len(parts) > 1:
                scheme = parts[1]
                # Simple mapping for common schemes
                mapping = {
                    "paeruginosa": "Pseudomonas aeruginosa",
                    "saureus": "Staphylococcus aureus",
                    "ecoli": "Escherichia coli",
                    "kpneumoniae": "Klebsiella pneumoniae",
                    "abaumannii": "Acinetobacter baumannii",
                    "senterica": "Salmonella enterica",
                    "lmonocytogenes": "Listeria monocytogenes",
                    "campylobacter": "Campylobacter jejuni",
                }
                species = mapping.get(scheme, scheme.capitalize())

    print(f"  [PATCH] Identified species: {species}")

    # 2. Read and patch
    with open(gbk_path, "r") as f:
        lines = f.readlines()

    with open(gbk_path, "w") as f:
        for line in lines:
            if line.startswith("SOURCE"):
                f.write(f"SOURCE      {species}\n")
            elif line.startswith("  ORGANISM  "):
                f.write(f"  ORGANISM  {species}\n")
            elif line.startswith("DEFINITION"):
                # DEFINITION  Genus species strain strain genome...
                # We replace everything after DEFINITION up to the first ';' or end of line
                f.write(f"DEFINITION  {species} genome assembly\n")
            else:
                f.write(line)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python patch_gbk_species.py <gbk_file> <mlst_file>")
        sys.exit(1)
    patch_gbk(sys.argv[1], sys.argv[2])
