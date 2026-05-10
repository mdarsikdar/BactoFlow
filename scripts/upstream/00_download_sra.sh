#!/bin/bash
# ==============================================================================
# Step 00: Download SRA Reads
# ==============================================================================
set -euo pipefail

# Self-locate: works standalone or when called from RUN_PIPELINE.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(realpath "$SCRIPT_DIR/../..")}"
SRA_ID="${SRA_ID:-$(head -n 1 "$PROJECT_ROOT/data/accession.txt" | tr -d '[:space:]')}"

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate ncbi-sra

OUTDIR="$PROJECT_ROOT/data/raw_reads"
mkdir -p "$OUTDIR"

echo "Downloading SRA accession(s) from: $PROJECT_ROOT/data/accession.txt"
mapfile -t ACCESSIONS < "$PROJECT_ROOT/data/accession.txt"

for ACC in "${ACCESSIONS[@]}"; do
    ACC=$(echo "$ACC" | tr -d '[:space:]')
    [[ -z "$ACC" ]] && continue

    R1_FASTQ="$OUTDIR/${ACC}_1.fastq"
    R2_FASTQ="$OUTDIR/${ACC}_2.fastq"
    R1_GZ="$OUTDIR/${ACC}_1.fastq.gz"
    R2_GZ="$OUTDIR/${ACC}_2.fastq.gz"

    if [[ -s "$R1_FASTQ" && -s "$R2_FASTQ" ]]; then
        echo "  [$ACC] .fastq reads already exist. Skipping download."
        continue
    fi
    if [[ -s "$R1_GZ" && -s "$R2_GZ" ]]; then
        echo "  [$ACC] .fastq.gz reads already exist. Skipping download."
        continue
    fi

    echo "  [$ACC] Downloading with fasterq-dump..."
    fasterq-dump --split-files "$ACC" -O "$OUTDIR" --temp "$OUTDIR"
done

echo "All downloads complete → $OUTDIR"
