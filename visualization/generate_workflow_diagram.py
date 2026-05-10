"""
generate_workflow_diagram.py
Generates a visual diagram of the full bioinformatics workflow.
  - Figure 0: Pipeline workflow diagram (saved to results/figures/)
Works standalone or when called from RUN_PIPELINE.sh (uses PROJECT_ROOT env var).
"""

import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ── Project Root Resolution ────────────────────────────────────────────────────
_env_root = os.environ.get("PROJECT_ROOT", "")
if _env_root:
    PROJECT_ROOT = Path(_env_root).resolve()
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

FIGURES_DIR = PROJECT_ROOT / "results" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def draw_workflow() -> None:
    fig, ax = plt.subplots(figsize=(10, 14))

    # (x, y, width, height, label, fill_color)
    boxes = [
        (0.35, 0.92, 0.30, 0.05, "Raw Reads (SRA)",             "#3498db"),
        (0.35, 0.84, 0.30, 0.05, "Quality Control (FastQC)",     "#2ecc71"),
        (0.35, 0.76, 0.30, 0.05, "Trimming (Trimmomatic)",       "#2ecc71"),
        # --- parallel paths ---
        (0.05, 0.63, 0.35, 0.05, "Reference Mapping (BWA)",      "#e67e22"),
        (0.60, 0.63, 0.35, 0.05, "De Novo Assembly (SPAdes)",    "#9b59b6"),
        (0.05, 0.55, 0.35, 0.05, "Variant Calling (FreeBayes)",  "#e67e22"),
        (0.60, 0.55, 0.35, 0.05, "Assembly QC (QUAST)",          "#9b59b6"),
        # --- converge ---
        (0.30, 0.43, 0.40, 0.05, "Functional Annotation (Prokka)","#f1c40f"),
        # --- downstream ---
        (0.05, 0.30, 0.38, 0.05, "MLST & Prophage (PhiSpy)",     "#e74c3c"),
        (0.57, 0.30, 0.38, 0.05, "AMR / Plasmid / Defense\n(ABRicate, PADLOC)", "#e74c3c"),
        # --- final ---
        (0.30, 0.16, 0.40, 0.05, "Summarize & Visualize",        "#1abc9c"),
        (0.30, 0.06, 0.40, 0.05, "Final Genomic Profile",        "#2c3e50"),
    ]

    for x, y, w, h, label, color in boxes:
        rect = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.01",
            linewidth=1.5, edgecolor="white",
            facecolor=color, alpha=0.88
        )
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, label,
                ha="center", va="center",
                fontweight="bold", fontsize=9, color="white",
                wrap=True)

    # Arrows
    ap = dict(arrowstyle="->", lw=1.8, color="#555555")
    arrows = [
        # Top straight section
        ((0.50, 0.89), (0.50, 0.92)),
        ((0.50, 0.81), (0.50, 0.84)),
        # Split at trimming
        ((0.23, 0.68), (0.50, 0.76)),
        ((0.77, 0.68), (0.50, 0.76)),
        # Down each branch
        ((0.23, 0.63), (0.23, 0.68)),
        ((0.77, 0.63), (0.77, 0.68)),
        # Converge to Prokka
        ((0.50, 0.48), (0.23, 0.55)),
        ((0.50, 0.48), (0.77, 0.55)),
        # Prokka to downstream
        ((0.24, 0.35), (0.50, 0.43)),
        ((0.76, 0.35), (0.50, 0.43)),
        # Downstream to summarize
        ((0.50, 0.21), (0.24, 0.30)),
        ((0.50, 0.21), (0.76, 0.30)),
        # Summarize to final
        ((0.50, 0.16), (0.50, 0.21)),
        ((0.50, 0.11), (0.50, 0.16)),
    ]
    for (x2, y2), (x1, y1) in arrows:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=ap)

    ax.set_xlim(0, 1)
    ax.set_ylim(0.0, 1.0)
    ax.set_facecolor("#f8f9fa")
    fig.patch.set_facecolor("#f8f9fa")
    ax.axis("off")
    ax.set_title(
        "Bacterial Genomics Pipeline — End-to-End Workflow",
        fontsize=13, fontweight="bold", pad=12, color="#2c3e50"
    )
    plt.tight_layout()

    out = FIGURES_DIR / "figure0_workflow_diagram.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Workflow diagram saved → {out}")


if __name__ == "__main__":
    draw_workflow()
