import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def generate_comprehensive_workflow(output_path):
    fig, ax = plt.subplots(figsize=(12, 16))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Color Palette
    COLORS = {
        'input': '#3498db',     # Blue
        'qc': '#1abc9c',        # Teal
        'mapping': '#f1c40f',   # Yellow
        'assembly': '#e67e22',  # Orange
        'annotation': '#9b59b6',# Purple
        'downstream': '#e74c3c',# Red
        'report': '#2c3e50'      # Dark Blue
    }

    def draw_box(x, y, w, h, text, color, title=None, subtitle=None):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=2", 
                                      linewidth=2, edgecolor=color, facecolor='white', zorder=2)
        ax.add_patch(rect)
        if title:
            ax.text(x + w/2, y + h*0.75, title, ha='center', va='center', fontweight='bold', fontsize=12, color=color)
            ax.text(x + w/2, y + h*0.4, subtitle, ha='center', va='center', fontsize=9, color='#7f8c8d')
        else:
            ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontweight='bold', fontsize=11)

    # 1. INPUT
    draw_box(40, 92, 20, 6, "RAW DATA", COLORS['input'], "INPUT", "SRA ID or Local FASTQ")
    
    # Arrow Input to QC
    ax.annotate('', xy=(50, 85), xytext=(50, 92), arrowprops=dict(arrowstyle='->', lw=2, color='#bdc3c7'))

    # 2. QC BLOCK
    draw_box(15, 75, 70, 10, "QC & TRIMMING", COLORS['qc'], "PRE-PROCESSING", "FastQC | MultiQC | Trimmomatic")
    
    # 3. SPLIT PATH (Mapping vs Assembly)
    ax.annotate('', xy=(30, 65), xytext=(50, 75), arrowprops=dict(arrowstyle='->', lw=2, color='#bdc3c7'))
    ax.annotate('', xy=(70, 65), xytext=(50, 75), arrowprops=dict(arrowstyle='->', lw=2, color='#bdc3c7'))

    # 4. MAPPING
    draw_box(10, 55, 40, 10, "VARIANT ANALYSIS", COLORS['mapping'], "UPSTREAM (REF)", "BWA | SAMtools | FreeBayes")
    
    # 5. ASSEMBLY
    draw_box(50, 55, 40, 10, "DE NOVO ASSEMBLY", COLORS['assembly'], "UPSTREAM (GENOME)", "SPAdes | QUAST")

    # 6. REJOIN AT ANNOTATION
    ax.annotate('', xy=(50, 45), xytext=(30, 55), arrowprops=dict(arrowstyle='->', lw=2, color='#bdc3c7'))
    ax.annotate('', xy=(50, 45), xytext=(70, 55), arrowprops=dict(arrowstyle='->', lw=2, color='#bdc3c7'))

    # 7. ANNOTATION
    draw_box(15, 35, 70, 10, "GENOME ANNOTATION", COLORS['annotation'], "ANNOTATION", "Prokka | fix_gbk_v3.py")

    # 8. DOWNSTREAM GRID
    ax.annotate('', xy=(50, 25), xytext=(50, 35), arrowprops=dict(arrowstyle='->', lw=2, color='#bdc3c7'))
    
    # Mini boxes for downstream
    y_ds = 18
    draw_box(10, y_ds, 18, 7, "MLST", COLORS['downstream'], "Typing", "Species ID")
    draw_box(32, y_ds, 18, 7, "ABRicate", COLORS['downstream'], "Screening", "AMR & VF")
    draw_box(54, y_ds, 18, 7, "PADLOC", COLORS['downstream'], "Defense", "CRISPR/Cas")
    draw_box(76, y_ds, 18, 7, "PhiSpy", COLORS['downstream'], "Prophage", "Phage ID")

    # 9. FINAL STEP
    ax.annotate('', xy=(50, 5), xytext=(50, 18), arrowprops=dict(arrowstyle='->', lw=2, color='#bdc3c7'))
    draw_box(25, 2, 50, 8, "FINAL OUTPUTS", COLORS['report'], "RESULTS", "Patched GBK | Summary Report | Figures")

    plt.title("BactoFlow: Comprehensive Bacterial Genomics Workflow", fontsize=18, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Workflow diagram saved to: {output_path}")

if __name__ == "__main__":
    os.makedirs("results/figures", exist_ok=True)
    generate_comprehensive_workflow("results/figures/figure0_workflow_diagram.png")
