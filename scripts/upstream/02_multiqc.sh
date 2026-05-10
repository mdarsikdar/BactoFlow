#!/bin/bash
# ==============================================================================
# Step 02: MultiQC — Aggregate QC Reports
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(realpath "$SCRIPT_DIR/../..")}"

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate multiqc

INDIR="$PROJECT_ROOT/results/qc"
OUTDIR="$PROJECT_ROOT/results/multiqc"
mkdir -p "$OUTDIR"

echo "Running MultiQC on FastQC reports in $INDIR..."
multiqc "$INDIR" -o "$OUTDIR" --force

echo "MultiQC complete → $OUTDIR"
