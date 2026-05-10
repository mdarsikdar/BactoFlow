#!/bin/bash
# ==============================================================================
# Step 08: Prokka — Functional Genome Annotation
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(realpath "$SCRIPT_DIR/../..")}"
SRA_ID="${SRA_ID:-$(head -n 1 "$PROJECT_ROOT/data/accession.txt" | tr -d '[:space:]')}"

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate prokka

ASSEMBLY="$PROJECT_ROOT/results/assembly/scaffolds.fasta"
OUTDIR="$PROJECT_ROOT/results/annotation"
mkdir -p "$OUTDIR"

if [[ ! -s "$ASSEMBLY" ]]; then
    echo "ERROR: Assembly not found: $ASSEMBLY"
    echo "  Run step 6 (SPAdes Assembly) first."
    exit 1
fi

echo "Running Prokka annotation for $SRA_ID..."
prokka \
    --outdir "$OUTDIR/$SRA_ID" \
    --prefix "$SRA_ID" \
    --cpus 4 \
    --force \
    "$ASSEMBLY"

echo "Annotation complete → $OUTDIR/$SRA_ID/$SRA_ID.gbk"
