"""
fix_gbk_biopython.py
Uses BioPython to standardise a GenBank file for PhiSpy 5 compatibility.
Ensures:
  - Unique LOCUS names (SC_1, SC_2, ...)
  - Correct molecule_type ("DNA") in annotations
  - Valid GenBank structure
Requires BioPython (run within phispy or prokka env).
"""

import sys
from pathlib import Path
from Bio import SeqIO
from Bio.SeqIO.InsdcIO import GenBankWriter

def fix_gbk(input_path, output_path):
    if not Path(input_path).exists():
        print(f"Error: {input_path} not found")
        return

    records = []
    for i, record in enumerate(SeqIO.parse(input_path, "genbank"), start=1):
        # 1. Standardise name/ID
        record.id = f"SC_{i}"
        record.name = f"SC_{i}"
        
        # 2. Ensure molecule_type is present (critical for BioPython writer)
        if "molecule_type" not in record.annotations:
            record.annotations["molecule_type"] = "DNA"
            
        # 3. Clean up features (optional but good)
        for feature in record.features:
            if feature.type == "source":
                feature.qualifiers["molecule_type"] = ["DNA"]
        
        records.append(record)

    with open(output_path, "w") as f:
        writer = GenBankWriter(f)
        writer.write_records(records)
    
    print(f"Fixed {len(records)} records using BioPython → {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python fix_gbk_biopython.py <in.gbk> <out.gbk>")
        sys.exit(1)
    fix_gbk(sys.argv[1], sys.argv[2])
