"""
fix_gbk_v3.py
Fixes Prokka GenBank files for PhiSpy 5 compatibility.
Uses standard GenBank offsets but avoids the date field to minimize scanner errors.
"""

import sys
import re
import os
from pathlib import Path

def fix_gbk(input_path: str, output_path: str) -> None:
    with open(input_path, "r") as fh:
        lines = fh.readlines()

    counter = 1
    with open(output_path, "w") as out:
        for line in lines:
            if line.startswith("LOCUS"):
                length_match = re.search(r"length_(\d+)", line)
                if not length_match:
                    length_match = re.search(r"(\d+)\s+bp", line)
                length = length_match.group(1) if length_match else "1000"
                
                # Standard offsets: name starts at 13, length ends at 40
                name = f"SC_{counter}"
                # We use spaces to ensure DNA starts after bp, and avoid the date field entirely
                locus_line = f"LOCUS       {name:<16} {length:>11} bp    DNA     linear\n"
                out.write(locus_line)
                counter += 1
            elif line.startswith("FEATURES"):
                out.write("FEATURES             Location/Qualifiers\n")
            elif "source " in line and "1.." in line:
                out.write(line)
                out.write('                     /molecule_type="DNA"\n')
            else:
                if '/molecule_type="DNA"' in line:
                    continue
                out.write(line)

    print(f"Fixed {counter - 1} records → {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(1)
    fix_gbk(sys.argv[1], sys.argv[2])
