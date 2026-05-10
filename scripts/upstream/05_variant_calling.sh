#!/bin/bash
# ==============================================================================
# Step 05: FreeBayes — Variant Calling
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(realpath "$SCRIPT_DIR/../..")}"
SRA_ID="${SRA_ID:-$(head -n 1 "$PROJECT_ROOT/data/accession.txt" | tr -d '[:space:]')}"

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate bwa-sam

REF="$PROJECT_ROOT/data/reference/reference.fasta"
BAM="$PROJECT_ROOT/results/mapping/${SRA_ID}.sorted.bam"
OUTDIR="$PROJECT_ROOT/results/vcf"
mkdir -p "$OUTDIR"

if [[ ! -s "$REF" ]]; then
    echo "ERROR: Reference genome not found: $REF"
    exit 1
fi
if [[ ! -s "$BAM" ]]; then
    echo "ERROR: Sorted BAM not found. Run step 4 (Mapping) first."
    exit 1
fi

# Index a local copy of the reference for freebayes
REF_VCF="$OUTDIR/reference.fasta"
cp "$REF" "$REF_VCF"
samtools faidx "$REF_VCF"

echo "Calling variants with FreeBayes for $SRA_ID..."
freebayes -f "$REF_VCF" "$BAM" > "$OUTDIR/${SRA_ID}.vcf"

echo "Compressing and indexing VCF..."
bgzip -f "$OUTDIR/${SRA_ID}.vcf"
tabix -p vcf "$OUTDIR/${SRA_ID}.vcf.gz"

echo "Variant calling complete → $OUTDIR/${SRA_ID}.vcf.gz"
