#!/bin/bash
# ==============================================================================
# Step 09: Downstream Analysis — MLST, ABRicate, PADLOC, PhiSpy
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(realpath "$SCRIPT_DIR/../..")}"
SRA_ID="${SRA_ID:-$(head -n 1 "$PROJECT_ROOT/data/accession.txt" | tr -d '[:space:]')}"

ASSEMBLY="$PROJECT_ROOT/results/assembly/scaffolds.fasta"
GBK_RAW="$PROJECT_ROOT/results/annotation/$SRA_ID/$SRA_ID.gbk"
OUTDIR="$PROJECT_ROOT/results/downstream"
THREADS=4

# Validate inputs
if [[ ! -s "$ASSEMBLY" ]]; then
    echo "ERROR: Assembly not found: $ASSEMBLY — run step 6 first."
    exit 1
fi
if [[ ! -s "$GBK_RAW" ]]; then
    echo "ERROR: GenBank annotation not found: $GBK_RAW — run step 8 first."
    exit 1
fi

mkdir -p "$OUTDIR"

# ── MLST ──────────────────────────────────────────────────────────────────────
echo "=== Running MLST ==="
conda run -n mlst mlst "$ASSEMBLY" > "$OUTDIR/mlst_results.tsv"
echo "  MLST complete."

# ── ABRicate ──────────────────────────────────────────────────────────────────
echo "=== Running ABRicate (all databases) ==="
mkdir -p "$OUTDIR/abricate"
DATABASES=(card resfinder vfdb plasmidfinder megares argannot ncbi)
for db in "${DATABASES[@]}"; do
    echo "  Processing $db..."
    conda run -n abricate \
        abricate --db "$db" --threads "$THREADS" "$ASSEMBLY" \
        > "$OUTDIR/abricate/abricate_${db}.tsv"
done
conda run -n abricate \
    abricate --summary "$OUTDIR/abricate"/abricate_*.tsv \
    > "$OUTDIR/abricate_summary.tsv"
echo "  ABRicate complete."

# ── PADLOC ────────────────────────────────────────────────────────────────────
echo "=== Running PADLOC (Defense Systems) ==="
mkdir -p "$OUTDIR/padloc"
# PADLOC requires the input to be in its working dir
TMP_FNA="$OUTDIR/padloc/scaffolds.fna"
cp "$ASSEMBLY" "$TMP_FNA"
conda run -n padloc \
    padloc --fna "$TMP_FNA" --outdir "$OUTDIR/padloc" --cpu "$THREADS"
rm -f "$TMP_FNA"
echo "  PADLOC complete."

# ── PhiSpy ────────────────────────────────────────────────────────────────────
echo "=== Running PhiSpy (Prophage Identification) ==="
# Fix the GenBank file for PhiSpy compatibility (unique LOCUS names)
FIXED_GBK="$OUTDIR/fixed_annotation.gbk"
echo "  Standardizing GenBank format..."
python "$PROJECT_ROOT/scripts/utils/fix_gbk_v3.py" "$GBK_RAW" "$FIXED_GBK"

mkdir -p "$OUTDIR/phispy"
conda run -n phispy \
    PhiSpy.py "$FIXED_GBK" -o "$OUTDIR/phispy" --threads "$THREADS"
echo "  PhiSpy complete."

# ── Patch GBK Species ──────────────────────────────────────────────────────────
echo "=== Patching GBK with MLST species ==="
python "$PROJECT_ROOT/scripts/utils/patch_gbk_species.py" "$GBK_RAW" "$OUTDIR/mlst_results.tsv"

echo "=== Downstream Analysis Complete → $OUTDIR ==="
