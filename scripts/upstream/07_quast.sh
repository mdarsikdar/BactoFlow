#!/bin/bash
# ==============================================================================
# Step 07: QUAST — Assembly Quality Assessment
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(realpath "$SCRIPT_DIR/../..")}"
SRA_ID="${SRA_ID:-$(head -n 1 "$PROJECT_ROOT/data/accession.txt" | tr -d '[:space:]')}"

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate quast

ASSEMBLY="$PROJECT_ROOT/results/assembly/scaffolds.fasta"
OUTDIR="$PROJECT_ROOT/results/quast"
mkdir -p "$OUTDIR"

if [[ ! -s "$ASSEMBLY" ]]; then
    echo "ERROR: Assembly not found: $ASSEMBLY"
    echo "  Run step 6 (SPAdes Assembly) first."
    exit 1
fi

echo "Running QUAST on assembly for $SRA_ID..."
quast.py "$ASSEMBLY" -o "$OUTDIR" --threads 4

echo "QUAST assessment complete → $OUTDIR/report.tsv"
