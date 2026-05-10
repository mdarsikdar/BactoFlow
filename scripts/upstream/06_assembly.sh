#!/bin/bash
# ==============================================================================
# Step 06: SPAdes — De Novo Genome Assembly
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(realpath "$SCRIPT_DIR/../..")}"
SRA_ID="${SRA_ID:-$(head -n 1 "$PROJECT_ROOT/data/accession.txt" | tr -d '[:space:]')}"

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate spades

INDIR="$PROJECT_ROOT/results/trimming"
OUTDIR="$PROJECT_ROOT/results/assembly"
mkdir -p "$OUTDIR"

READ_F="$INDIR/${SRA_ID}_1_paired.fastq"
READ_R="$INDIR/${SRA_ID}_2_paired.fastq"

if [[ ! -s "$READ_F" || ! -s "$READ_R" ]]; then
    echo "ERROR: Trimmed reads not found. Run step 3 (Trimmomatic) first."
    echo "  Expected: $READ_F"
    exit 1
fi

echo "Running SPAdes assembly for $SRA_ID..."
spades.py \
    -1 "$READ_F" \
    -2 "$READ_R" \
    -o "$OUTDIR" \
    --threads 4 \
    --memory 8 \
    --only-assembler \
    --isolate \
    -k 21,33,55,77

echo "Assembly complete → $OUTDIR/scaffolds.fasta"
