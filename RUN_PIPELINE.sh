#!/bin/bash

# ==============================================================================
# MASTER PIPELINE: BactoFlow — Bacterial Genomics Workflow
# ==============================================================================
# Fully reproducible and resumable pipeline.
#
# Usage:
#   bash RUN_PIPELINE.sh                 # Auto-resume from last completed step
#   bash RUN_PIPELINE.sh --from-step 4  # Force re-run from step 4 onwards
#   bash RUN_PIPELINE.sh --list-steps   # Print all step numbers and names
#
# Steps:
#   0  - Download SRA reads
#   1  - FastQC (raw read QC)
#   2  - MultiQC (aggregate QC report)
#   3  - Trimmomatic (adapter trimming)
#   4  - BWA Mapping (reference alignment)
#   5  - FreeBayes Variant Calling
#   6  - SPAdes De Novo Assembly
#   7  - QUAST Assembly Assessment
#   8  - Prokka Annotation
#   9  - Downstream Analysis (MLST, ABRicate, PADLOC, PhiSpy)
#   10 - Summarize Results
#   11 - Visualization Pipeline (6 Key Figures)
# ==============================================================================

set -euo pipefail

# ── Project Root (always the directory containing this script) ─────────────────
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PROJECT_ROOT

# ── Sub-directories ────────────────────────────────────────────────────────────
UPSTREAM_DIR="$PROJECT_ROOT/scripts/upstream"
DOWNSTREAM_DIR="$PROJECT_ROOT/scripts/downstream"
UTILS_DIR="$PROJECT_ROOT/scripts/utils"
VIS_DIR="$PROJECT_ROOT/visualization"
CHECKPOINT_DIR="$PROJECT_ROOT/results/.checkpoints"
LOG_FILE="$PROJECT_ROOT/results/pipeline.log"

# Create required directories
mkdir -p "$CHECKPOINT_DIR" \
         "$PROJECT_ROOT/results/figures" \
         "$PROJECT_ROOT/results/qc" \
         "$PROJECT_ROOT/results/multiqc" \
         "$PROJECT_ROOT/results/trimming" \
         "$PROJECT_ROOT/results/mapping" \
         "$PROJECT_ROOT/results/vcf" \
         "$PROJECT_ROOT/results/assembly" \
         "$PROJECT_ROOT/results/annotation" \
         "$PROJECT_ROOT/results/quast" \
         "$PROJECT_ROOT/results/downstream"

# ── Argument Parsing ───────────────────────────────────────────────────────────
FROM_STEP=0
FORCE_FROM=false

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --from-step)
            FROM_STEP="${2:-}"
            FORCE_FROM=true
            shift 2
            ;;
        --list-steps)
            echo "Pipeline Steps:"
            echo "  0  Download SRA reads"
            echo "  1  FastQC (raw read QC)"
            echo "  2  MultiQC (aggregate report)"
            echo "  3  Trimmomatic (adapter trimming)"
            echo "  4  BWA Mapping"
            echo "  5  FreeBayes Variant Calling"
            echo "  6  SPAdes De Novo Assembly"
            echo "  7  QUAST Assembly Assessment"
            echo "  8  Prokka Annotation"
            echo "  9  Downstream Analysis (MLST/ABRicate/PADLOC/PhiSpy)"
            echo " 10  Summarize Results"
            echo " 11  Visualization Pipeline"
            exit 0
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: bash RUN_PIPELINE.sh [--from-step N] [--list-steps]"
            exit 1
            ;;
    esac
done

# ── Logging ────────────────────────────────────────────────────────────────────
log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    echo "$msg"
    echo "$msg" >> "$LOG_FILE"
}

# ── Checkpoint Helpers ─────────────────────────────────────────────────────────
is_done() {
    local step="$1"
    # If force-rerun is active and this step is >= FROM_STEP, do NOT skip
    if [[ "$FORCE_FROM" == "true" && "$step" -ge "$FROM_STEP" ]]; then
        return 1  # not done (must run)
    fi
    [[ -f "$CHECKPOINT_DIR/step${step}.done" ]]
}

mark_done() {
    local step="$1"
    touch "$CHECKPOINT_DIR/step${step}.done"
    log "  ✔ Step $step complete."
}

# ── Step Runner ────────────────────────────────────────────────────────────────
run_step() {
    local step_num="$1"
    local step_name="$2"
    shift 2

    if is_done "$step_num"; then
        log "⏭  Step $step_num ($step_name): Already done — skipping."
        return 0
    fi

    log "▶  Step $step_num ($step_name): Starting..."
    "$@"
    mark_done "$step_num"
}

# ── Validate Input ─────────────────────────────────────────────────────────────
if [[ ! -f "$PROJECT_ROOT/data/accession.txt" ]]; then
    log "ERROR: data/accession.txt not found. Please add your SRA accession ID."
    exit 1
fi

SRA_ID=$(head -n 1 "$PROJECT_ROOT/data/accession.txt" | tr -d '[:space:]')
export SRA_ID

log "================================================================"
log "  BactoFlow"
log "  Sample : $SRA_ID"
log "  Root   : $PROJECT_ROOT"
if [[ "$FORCE_FROM" == "true" ]]; then
    log "  Mode   : Re-run from step $FROM_STEP"
else
    log "  Mode   : Auto-resume (skips completed steps)"
fi
log "================================================================"

# ── Run All Steps ──────────────────────────────────────────────────────────────
run_step 0  "Download SRA reads"          bash "$UPSTREAM_DIR/00_download_sra.sh"
run_step 1  "FastQC"                      bash "$UPSTREAM_DIR/01_fastqc.sh"
run_step 2  "MultiQC"                     bash "$UPSTREAM_DIR/02_multiqc.sh"
run_step 3  "Trimmomatic"                 bash "$UPSTREAM_DIR/03_trimmomatic.sh"
run_step 4  "BWA Mapping"                 bash "$UPSTREAM_DIR/04_mapping.sh"
run_step 5  "FreeBayes Variant Calling"   bash "$UPSTREAM_DIR/05_variant_calling.sh"
run_step 6  "SPAdes Assembly"             bash "$UPSTREAM_DIR/06_assembly.sh"
run_step 7  "QUAST Assessment"            bash "$UPSTREAM_DIR/07_quast.sh"
run_step 8  "Prokka Annotation"           bash "$UPSTREAM_DIR/08_prokka.sh"
run_step 9  "Downstream Analysis"         bash "$DOWNSTREAM_DIR/09_run_downstream_analysis.sh"
run_step 10 "Summarize Results"           python "$UTILS_DIR/summarize_results.py"

# ── Visualization Pipeline (6 Figures) ─────────────────────────────────────────
run_visualization_pipeline() {
    log "  Generating Workflow Diagram (Figure 0)..."
    python "$VIS_DIR/generate_workflow_diagram.py"
    
    log "  Generating AMR Heatmap (Figure 9)..."
    python "$VIS_DIR/generate_amr_heatmap.py"
    
    log "  Generating Mapping Coverage (Figure 10)..."
    python "$VIS_DIR/generate_mapping_coverage_figures.py"
    
    log "  Generating Virulence Heatmap (Figure 11)..."
    python "$VIS_DIR/generate_virulence_heatmap.py"
    
    log "  Generating Prophage Map (Figure 12)..."
    python "$VIS_DIR/generate_prophage_visual.py"
    
    log "  Generating PADLOC Systems (Figure 13)..."
    python "$VIS_DIR/generate_padloc_visual.py"
}

run_step 11 "Visualization Pipeline" run_visualization_pipeline

log "================================================================"
log "  Pipeline Execution Complete!"
log "  All outputs are in: $PROJECT_ROOT/results/"
log "  Log file         : $LOG_FILE"
log "================================================================"
