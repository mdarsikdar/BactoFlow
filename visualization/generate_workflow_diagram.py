import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def generate_premium_workflow(output_path):
    # Set a clean white background
    plt.rcParams['figure.facecolor'] = 'white'
    # Increase figure size slightly for better proportions
    fig, ax = plt.subplots(figsize=(16, 20))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 110) # Increased Y limit to avoid title overlap
    ax.axis('off')

    # Premium Vibrant Palette (Darker shades for white text contrast)
    PALETTE = {
        'input': '#2C3E50',      # Midnight Blue
        'qc': '#16A085',         # Dark Teal
        'mapping': '#2980B9',    # Soft Blue
        'assembly': '#8E44AD',   # Soft Purple
        'annotation': '#D35400', # Burnt Orange
        'downstream': '#C0392B', # Classy Red
        'report': '#192A56',     # Navy Blue
        'arrow': '#7F8C8D'       # Darker Grey for better visibility
    }

    def draw_box(x, y, w, h, text, color, title=None, subtitle=None):
        # Subtle shadow for depth
        shadow = patches.FancyBboxPatch((x+0.4, y-0.4), w, h, boxstyle="round,pad=1.5", 
                                        linewidth=0, facecolor='#DFE6E9', zorder=1, alpha=0.4)
        ax.add_patch(shadow)
        
        # Main Colored Box
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=1.5", 
                                      linewidth=0, facecolor=color, zorder=2)
        ax.add_patch(rect)
        
        if title:
            # White text for premium contrast
            ax.text(x + w/2, y + h*0.75, title, ha='center', va='center', 
                    fontweight='bold', fontsize=16, color='white', family='sans-serif')
            ax.text(x + w/2, y + h*0.35, subtitle, ha='center', va='center', 
                    fontsize=11, color='#F5F6FA', family='sans-serif', style='italic')
        else:
            ax.text(x + w/2, y + h/2, text, ha='center', va='center', 
                    fontweight='bold', fontsize=13, color='white', family='sans-serif')

    def draw_arrow(start_pos, end_pos):
        # shrinkA/B to keep space from boxes
        ax.annotate('', xy=end_pos, xytext=start_pos, 
                    arrowprops=dict(arrowstyle='-|>', lw=2.5, color=PALETTE['arrow'], 
                                   shrinkA=15, shrinkB=15, mutation_scale=25), zorder=1)

    # Title - High and centered
    plt.text(50, 105, "BactoFlow: The Bacterial Genomics Workhorse", 
             ha='center', va='center', fontsize=26, fontweight='bold', color='#2C3E50')

    # 1. INPUT LAYER
    draw_box(40, 92, 20, 6, "RAW DATA", PALETTE['input'], "INPUT", "SRA ID or FASTQ.GZ")
    
    # 2. QC LAYER
    draw_arrow((50, 92), (50, 80))
    draw_box(20, 72, 60, 8, "QC & TRIMMING", PALETTE['qc'], "QUALITY CONTROL", "FastQC • MultiQC • Trimmomatic")
    
    # 3. SPLIT PATH
    draw_arrow((50, 72), (30, 62)) # To Mapping
    draw_arrow((50, 72), (70, 62)) # To Assembly

    # 4. MAPPING
    draw_box(10, 52, 40, 10, "VARIANT ANALYSIS", PALETTE['mapping'], "UPSTREAM (REF)", "BWA-MEM • FreeBayes • SAMtools")
    
    # 5. ASSEMBLY
    draw_box(50, 52, 40, 10, "DE NOVO ASSEMBLY", PALETTE['assembly'], "UPSTREAM (GENOME)", "SPAdes • QUAST • Assembly-Stats")

    # 6. REJOIN
    draw_arrow((30, 52), (50, 42))
    draw_arrow((70, 52), (50, 42))

    # 7. ANNOTATION
    draw_box(20, 34, 60, 8, "GENOME ANNOTATION", PALETTE['annotation'], "ANNOTATION", "Prokka • fix_gbk_v3 • Species Patching")

    # 8. DOWNSTREAM GRID
    draw_arrow((50, 34), (50, 26))
    
    y_ds = 18
    draw_box(5, y_ds, 20, 7, "MLST", PALETTE['downstream'], "Typing", "Strain ID")
    draw_box(28.5, y_ds, 20, 7, "ABRicate", PALETTE['downstream'], "AMR/VF", "Resistance")
    draw_box(52, y_ds, 20, 7, "PADLOC", PALETTE['downstream'], "Defense", "CRISPR/Cas")
    draw_box(75.5, y_ds, 20, 7, "PhiSpy", PALETTE['downstream'], "Phage", "Prophages")

    # 9. FINAL STEP
    draw_arrow((50, 18), (50, 10))
    draw_box(25, 2, 50, 8, "FINAL OUTPUTS", PALETTE['report'], "RESULTS & REPORTS", "GenBank • TSV Summaries • Visualization")

    plt.tight_layout()
    # High resolution 600 DPI
    plt.savefig(output_path, dpi=600, bbox_inches='tight', facecolor='white')
    print(f"Premium 600 DPI workflow diagram saved to: {output_path}")

if __name__ == "__main__":
    os.makedirs("results/figures", exist_ok=True)
    generate_premium_workflow("results/figures/figure0_workflow_diagram.png")
