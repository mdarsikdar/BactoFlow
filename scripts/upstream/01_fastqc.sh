#!/bin/bash
# ==============================================================================
# Step 01: FastQC — Raw Read Quality Control
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(realpath "$SCRIPT_DIR/../..")}"
SRA_ID="${SRA_ID:-$(head -n 1 "$PROJECT_ROOT/data/accession.txt" | tr -d '[:space:]')}"

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate fastqc

INDIR="$PROJECT_ROOT/data/raw_reads"
OUTDIR="$PROJECT_ROOT/results/qc"
mkdir -p "$OUTDIR"

shopt -s nullglob
fastq_files=("$INDIR"/*.fastq "$INDIR"/*.fastq.gz)
shopt -u nullglob

if [[ ${#fastq_files[@]} -eq 0 ]]; then
    echo "ERROR: No FASTQ files found in $INDIR"
    exit 1
fi

echo "Running FastQC on ${#fastq_files[@]} file(s)..."
for fq in "${fastq_files[@]}"; do
    echo "  Processing: $(basename "$fq")"
    fastqc "$fq" -o "$OUTDIR" --threads 4
done

echo "FastQC complete → $OUTDIR"
