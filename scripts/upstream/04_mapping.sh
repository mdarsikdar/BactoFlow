#!/bin/bash
# ==============================================================================
# Step 04: BWA + SAMtools — Reference Mapping
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(realpath "$SCRIPT_DIR/../..")}"
SRA_ID="${SRA_ID:-$(head -n 1 "$PROJECT_ROOT/data/accession.txt" | tr -d '[:space:]')}"

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate bwa-sam

REF="$PROJECT_ROOT/data/reference/reference.fasta"
READ_F="$PROJECT_ROOT/results/trimming/${SRA_ID}_1_paired.fastq"
READ_R="$PROJECT_ROOT/results/trimming/${SRA_ID}_2_paired.fastq"
OUTDIR="$PROJECT_ROOT/results/mapping"
mkdir -p "$OUTDIR"

# Validate inputs
if [[ ! -s "$REF" ]]; then
    echo "ERROR: Reference genome not found: $REF"
    echo "  Place your reference FASTA at: data/reference/reference.fasta"
    exit 1
fi
if [[ ! -s "$READ_F" || ! -s "$READ_R" ]]; then
    echo "ERROR: Trimmed reads not found. Run step 3 (Trimmomatic) first."
    exit 1
fi

echo "Indexing reference genome..."
bwa index "$REF"
samtools faidx "$REF"

echo "Mapping $SRA_ID reads to reference..."
bwa mem -t 4 "$REF" "$READ_F" "$READ_R" > "$OUTDIR/${SRA_ID}.sam"

echo "Converting SAM → sorted BAM..."
samtools view  -@ 4 -S -b "$OUTDIR/${SRA_ID}.sam"         > "$OUTDIR/${SRA_ID}.bam"
samtools sort  -@ 4 -m 500M                                \
    -o "$OUTDIR/${SRA_ID}.sorted.bam" "$OUTDIR/${SRA_ID}.bam"
samtools index "$OUTDIR/${SRA_ID}.sorted.bam"

# Remove intermediate SAM/unsorted BAM to save space
rm -f "$OUTDIR/${SRA_ID}.sam" "$OUTDIR/${SRA_ID}.bam"

echo "Mapping complete → $OUTDIR/${SRA_ID}.sorted.bam"
