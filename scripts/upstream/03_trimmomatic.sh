#!/bin/bash
# ==============================================================================
# Step 03: Trimmomatic — Adapter Trimming & Quality Filtering
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(realpath "$SCRIPT_DIR/../..")}"
SRA_ID="${SRA_ID:-$(head -n 1 "$PROJECT_ROOT/data/accession.txt" | tr -d '[:space:]')}"

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate trimmomatic

INDIR="$PROJECT_ROOT/data/raw_reads"
OUTDIR="$PROJECT_ROOT/results/trimming"
mkdir -p "$OUTDIR"

# Detect input files (.fastq or .fastq.gz)
if [[ -s "$INDIR/${SRA_ID}_1.fastq.gz" ]]; then
    READ_F_IN="$INDIR/${SRA_ID}_1.fastq.gz"
    READ_R_IN="$INDIR/${SRA_ID}_2.fastq.gz"
elif [[ -s "$INDIR/${SRA_ID}_1.fastq" ]]; then
    READ_F_IN="$INDIR/${SRA_ID}_1.fastq"
    READ_R_IN="$INDIR/${SRA_ID}_2.fastq"
else
    echo "ERROR: Raw reads not found in $INDIR for $SRA_ID"
    echo "  Expected: ${SRA_ID}_1.fastq[.gz] and ${SRA_ID}_2.fastq[.gz]"
    exit 1
fi

READ_F_PAIRED="$OUTDIR/${SRA_ID}_1_paired.fastq"
READ_F_UNPAIRED="$OUTDIR/${SRA_ID}_1_unpaired.fastq"
READ_R_PAIRED="$OUTDIR/${SRA_ID}_2_paired.fastq"
READ_R_UNPAIRED="$OUTDIR/${SRA_ID}_2_unpaired.fastq"

echo "Running Trimmomatic on $SRA_ID..."
trimmomatic PE -threads 4 \
  "$READ_F_IN" "$READ_R_IN" \
  "$READ_F_PAIRED" "$READ_F_UNPAIRED" \
  "$READ_R_PAIRED" "$READ_R_UNPAIRED" \
  LEADING:3 TRAILING:3 SLIDINGWINDOW:4:15 MINLEN:50

echo "Trimming complete → $OUTDIR"
