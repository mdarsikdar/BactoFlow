import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def generate_perfect_workflow(output_path):
    plt.rcParams['figure.facecolor'] = 'white'
    fig, ax = plt.subplots(figsize=(16, 22))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 115)
    ax.axis('off')

    PALETTE = {
        'input': '#2C3E50',      # Midnight
        'qc': '#16A085',         # Teal
        'mapping': '#2980B9',    # Blue
        'assembly': '#8E44AD',   # Purple
        'annotation': '#D35400', # Orange
        'downstream': '#C0392B', # Red
        'report': '#192A56',     # Navy
        'arrow': '#34495E'       # Dark Slate for arrows
    }

    def draw_box(x, y, w, h, text, color, title=None, subtitle=None):
        # Premium Shadow
        shadow = patches.FancyBboxPatch((x+0.5, y-0.5), w, h, boxstyle="round,pad=1.5", 
                                        linewidth=0, facecolor='#DFE6E9', zorder=1, alpha=0.5)
        ax.add_patch(shadow)
        
        # Solid Colored Box
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=1.5", 
                                      linewidth=0, facecolor=color, zorder=2)
        ax.add_patch(rect)
        
        if title:
            ax.text(x + w/2, y + h*0.75, title, ha='center', va='center', 
                    fontweight='bold', fontsize=18, color='white')
            ax.text(x + w/2, y + h*0.35, subtitle, ha='center', va='center', 
                    fontsize=12, color='#F5F6FA', style='italic')
        else:
            ax.text(x + w/2, y + h/2, text, ha='center', va='center', 
                    fontweight='bold', fontsize=14, color='white')

    def draw_elbow_arrow(x_start, y_start, x_end, y_end, padding=2):
        # padding ensures it doesn't touch boxes
        # We'll draw this manually with a line + arrow head
        mid_y = (y_start + y_end) / 2
        
        # Line path
        path_x = [x_start, x_start, x_end, x_end]
        path_y = [y_start - padding, mid_y, mid_y, y_end + padding]
        
        ax.plot(path_x, path_y, lw=2.5, color=PALETTE['arrow'], zorder=1)
        
        # Add arrowhead at the end
        ax.annotate('', xy=(x_end, y_end + padding), xytext=(x_end, y_end + padding + 0.1),
                    arrowprops=dict(arrowstyle='-|>', lw=2.5, color=PALETTE['arrow'], 
                                   mutation_scale=20), zorder=1)

    def draw_straight_arrow(x_start, y_start, x_end, y_end, padding=2):
        ax.annotate('', xy=(x_end, y_end + padding), xytext=(x_start, y_start - padding),
                    arrowprops=dict(arrowstyle='-|>', lw=2.5, color=PALETTE['arrow'], 
                                   mutation_scale=20), zorder=1)

    # Title
    plt.text(50, 110, "BactoFlow: The Bacterial Genomics Workhorse", 
             ha='center', va='center', fontsize=28, fontweight='bold', color='#2C3E50')

    # 1. INPUT
    draw_box(40, 95, 20, 6, "RAW DATA", PALETTE['input'], "INPUT", "SRA ID or FASTQ.GZ")
    
    # 2. QC
    draw_straight_arrow(50, 95, 50, 82)
    draw_box(20, 74, 60, 8, "QC & TRIMMING", PALETTE['qc'], "QUALITY CONTROL", "FastQC • MultiQC • Trimmomatic")
    
    # 3. SPLIT (Elbows)
    draw_elbow_arrow(50, 74, 30, 64) # To Mapping
    draw_elbow_arrow(50, 74, 70, 64) # To Assembly

    # 4. MAPPING
    draw_box(10, 54, 40, 10, "VARIANT ANALYSIS", PALETTE['mapping'], "UPSTREAM (REF)", "BWA-MEM • FreeBayes • SAMtools")
    
    # 5. ASSEMBLY
    draw_box(50, 54, 40, 10, "DE NOVO ASSEMBLY", PALETTE['assembly'], "UPSTREAM (GENOME)", "SPAdes • QUAST • Assembly-Stats")

    # 6. REJOIN (Elbows)
    draw_elbow_arrow(30, 54, 50, 44)
    draw_elbow_arrow(70, 54, 50, 44)

    # 7. ANNOTATION
    draw_box(20, 36, 60, 8, "GENOME ANNOTATION", PALETTE['annotation'], "ANNOTATION", "Prokka • fix_gbk_v3 • Species Patching")

    # 8. DOWNSTREAM GRID
    # Vertical line down to a split
    ax.plot([50, 50], [34, 28], lw=2.5, color=PALETTE['arrow'])
    ax.plot([16, 84], [28, 28], lw=2.5, color=PALETTE['arrow'])
    
    y_ds = 20
    # Downward arrows from the horizontal line
    for x in [16, 39, 61, 84]:
        draw_straight_arrow(x, 28, x, y_ds + 7, padding=0.5)

    draw_box(6, y_ds, 20, 7, "MLST", PALETTE['downstream'], "Typing", "Strain ID")
    draw_box(29, y_ds, 20, 7, "ABRicate", PALETTE['downstream'], "AMR/VF", "Resistance")
    draw_box(51, y_ds, 20, 7, "PADLOC", PALETTE['downstream'], "Defense", "CRISPR/Cas")
    draw_box(74, y_ds, 20, 7, "PhiSpy", PALETTE['downstream'], "Phage", "Prophages")

    # 9. FINAL STEP
    draw_straight_arrow(50, 20, 50, 10)
    draw_box(25, 2, 50, 8, "FINAL OUTPUTS", PALETTE['report'], "RESULTS & REPORTS", "GenBank • TSV Summaries • Visualization")

    plt.tight_layout()
    plt.savefig(output_path, dpi=600, bbox_inches='tight', facecolor='white')
    print(f"Perfected 600 DPI workflow diagram saved to: {output_path}")

if __name__ == "__main__":
    os.makedirs("results/figures", exist_ok=True)
    generate_perfect_workflow("results/figures/figure01_workflow_diagram.png")
