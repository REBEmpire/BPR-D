#!/usr/bin/env python3
"""
Epstein Network Investigation - Infographic Generation
BPR&D Special Reports - February 2026
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, ConnectionPatch
import numpy as np
import networkx as nx
from datetime import datetime

# Set style for all plots
plt.style.use('dark_background')
GOLD = '#D4AF37'
CRIMSON = '#8B0000'
DARK_BLUE = '#1a1a2e'
TEAL = '#16213e'
SILVER = '#C0C0C0'
WHITE = '#FFFFFF'
PURPLE = '#6B2D5C'

# ============================================
# INFOGRAPHIC 1: Network Visualization
# ============================================
def create_network_visualization():
    fig, ax = plt.subplots(figsize=(16, 12), facecolor=DARK_BLUE)
    ax.set_facecolor(DARK_BLUE)
    
    # Create hierarchical network
    G = nx.DiGraph()
    
    # Central node
    G.add_node("Jeffrey Epstein", level=0, category="core")
    
    # Inner Circle (level 1)
    inner_circle = [
        ("Ghislaine Maxwell", "Recruiter/Groomer"),
        ("Lesley Groff", "Assistant"),
        ("Richard Kahn", "Accountant"),
        ("Darren Indyke", "Lawyer"),
        ("Jean-Luc Brunel", "Modeling Agent")
    ]
    for name, role in inner_circle:
        G.add_node(name, level=1, category="inner", role=role)
        G.add_edge("Jeffrey Epstein", name, weight=5)
    
    # Financial Enablers (level 2)
    financial = [
        ("Les Wexner", "L Brands"),
        ("Leon Black", "Apollo Global"),
        ("Deutsche Bank", "Banking"),
        ("JPMorgan Chase", "Banking"),
        ("Financial Trust Co", "Shell Company")
    ]
    for name, role in financial:
        G.add_node(name, level=2, category="financial", role=role)
        G.add_edge("Jeffrey Epstein", name, weight=3)
    
    # Political/Elite Associates (level 2)
    political = [
        ("Prince Andrew", "Royal"),
        ("Bill Clinton", "Political"),
        ("Donald Trump", "Political"),
        ("Peter Mandelson", "Political"),
        ("Ehud Barak", "Political")
    ]
    for name, role in political:
        G.add_node(name, level=2, category="political", role=role)
        G.add_edge("Jeffrey Epstein", name, weight=2)
    
    # Properties/Locations (level 2)
    locations = [
        ("Little Saint James", "Primary Trafficking Hub"),
        ("Zorro Ranch, NM", "Eugenics/Abuse Site"),
        ("Manhattan Townhouse", "NY Operations"),
        ("Palm Beach Estate", "FL Operations")
    ]
    for name, role in locations:
        G.add_node(name, level=2, category="location", role=role)
        G.add_edge("Jeffrey Epstein", name, weight=4)
    
    # Science/Transhumanism connections
    science = [
        ("Eugenics Project", "Baby Farm Plans"),
        ("Designer Baby\nProject", "Genetic Enhancement"),
        ("Scientific\nCommunity", "Legitimacy")
    ]
    for name, role in science:
        G.add_node(name, level=3, category="science", role=role)
        G.add_edge("Jeffrey Epstein", name, weight=2)
    
    # Position nodes
    pos = {}
    pos["Jeffrey Epstein"] = (0, 0)
    
    # Inner circle around center
    inner_angle = np.linspace(0, 2*np.pi, len(inner_circle), endpoint=False)
    for i, (name, _) in enumerate(inner_circle):
        pos[name] = (1.5 * np.cos(inner_angle[i]), 1.5 * np.sin(inner_angle[i]))
    
    # Financial - left sector
    for i, (name, _) in enumerate(financial):
        angle = np.pi - 0.8 + (i * 0.4)
        pos[name] = (3.5 * np.cos(angle), 3.5 * np.sin(angle))
    
    # Political - right sector
    for i, (name, _) in enumerate(political):
        angle = 0.8 - (i * 0.4)
        pos[name] = (3.5 * np.cos(angle), 3.5 * np.sin(angle))
    
    # Locations - bottom
    for i, (name, _) in enumerate(locations):
        angle = -np.pi/2 - 0.6 + (i * 0.4)
        pos[name] = (3.5 * np.cos(angle), 3.5 * np.sin(angle))
    
    # Science - top
    for i, (name, _) in enumerate(science):
        angle = np.pi/2 - 0.4 + (i * 0.4)
        pos[name] = (4.2 * np.cos(angle), 4.2 * np.sin(angle))
    
    # Draw edges
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        ax.plot([x0, x1], [y0, y1], color=SILVER, alpha=0.3, linewidth=1, zorder=1)
    
    # Draw nodes by category
    node_colors = {
        "core": CRIMSON,
        "inner": PURPLE,
        "financial": GOLD,
        "political": '#4a90a4',
        "location": '#2d5a27',
        "science": '#8B4513'
    }
    
    for node in G.nodes():
        x, y = pos[node]
        cat = G.nodes[node].get('category', 'other')
        color = node_colors.get(cat, SILVER)
        size = 800 if cat == "core" else 400 if cat == "inner" else 300
        
        # Draw node circle
        circle = plt.Circle((x, y), 0.4 if cat == "core" else 0.25, 
                           color=color, alpha=0.9, zorder=2)
        ax.add_patch(circle)
        
        # Node label
        fontsize = 9 if cat == "core" else 7
        ax.annotate(node, (x, y - 0.5 if cat in ["core", "inner"] else y - 0.4),
                   ha='center', va='top', fontsize=fontsize, color=WHITE,
                   fontweight='bold' if cat in ["core", "inner"] else 'normal')
    
    # Title and legend
    ax.text(0, 5.5, "THE EPSTEIN NETWORK", fontsize=24, ha='center', 
            color=GOLD, fontweight='bold', family='serif')
    ax.text(0, 5.0, "Structural Analysis of Key Entities & Relationships", 
            fontsize=12, ha='center', color=SILVER, style='italic')
    
    # Legend
    legend_items = [
        (CRIMSON, "Core Subject"),
        (PURPLE, "Inner Circle (5 key operatives)"),
        (GOLD, "Financial Enablers"),
        ('#4a90a4', "Political/Elite Associates"),
        ('#2d5a27', "Operational Locations"),
        ('#8B4513', "Eugenics/Science Projects")
    ]
    
    for i, (color, label) in enumerate(legend_items):
        ax.add_patch(Circle((-6, 4 - i*0.6), 0.15, color=color))
        ax.text(-5.6, 4 - i*0.6, label, va='center', fontsize=9, color=WHITE)
    
    # Statistics box
    stats_text = """NETWORK STATISTICS
━━━━━━━━━━━━━━━━━━━━
Documents Released: 3.5M+ pages
Inner Circle: 5 core operatives
Financial Entities: 15+ shell companies
Locations: 4 primary facilities
High-Profile Mentions: 150+ individuals
Criminal Investigations: 5+ countries"""
    
    ax.text(5, 3.5, stats_text, fontsize=9, color=WHITE, family='monospace',
           bbox=dict(boxstyle='round', facecolor=TEAL, alpha=0.8),
           verticalalignment='top')
    
    # BPR&D branding
    ax.text(6.5, -5.2, "BPR&D SPECIAL REPORTS", fontsize=10, ha='right',
           color=GOLD, fontweight='bold')
    ax.text(6.5, -5.6, "February 2026", fontsize=8, ha='right', color=SILVER)
    
    ax.set_xlim(-7, 7)
    ax.set_ylim(-6, 6)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/github_repos/BPR-D/research/special-reports/assets/epstein-network-map.png',
               dpi=150, facecolor=DARK_BLUE, bbox_inches='tight')
    plt.close()
    print("✓ Network visualization saved")


# ============================================
# INFOGRAPHIC 2: Timeline Visualization
# ============================================
def create_timeline():
    fig, ax = plt.subplots(figsize=(16, 10), facecolor=DARK_BLUE)
    ax.set_facecolor(DARK_BLUE)
    
    # Timeline events
    events = [
        ("Aug 2019", "Epstein dies in\nManhattan jail", CRIMSON, "top"),
        ("Jan 2024", "Giuffre v. Maxwell\ndocuments unsealed\n(1,000+ pages)", GOLD, "bottom"),
        ("Dec 2024", "Ghislaine Maxwell\ndeposition\n(pleads Fifth)", PURPLE, "top"),
        ("Nov 2025", "Epstein Files\nTransparency Act\nsigned into law", GOLD, "bottom"),
        ("Dec 2025", "First DOJ\ndocument release\n(redaction failures)", '#4a90a4', "top"),
        ("Jan 2026", "Second release\nexposes victim data\n(privacy crisis)", CRIMSON, "bottom"),
        ("Feb 2026", "3.5M pages released\nPrince Andrew arrested\nInternational probes", GOLD, "top"),
    ]
    
    # Draw main timeline
    ax.axhline(y=0, color=SILVER, linewidth=3, alpha=0.5, zorder=1)
    
    # Draw events
    for i, (date, event, color, position) in enumerate(events):
        x = i * 2
        y_offset = 1.5 if position == "top" else -1.5
        marker_y = 0.3 if position == "top" else -0.3
        
        # Vertical connector
        ax.plot([x, x], [0, marker_y], color=color, linewidth=2, alpha=0.8)
        
        # Event marker
        ax.scatter([x], [0], s=200, color=color, zorder=3, edgecolors=WHITE, linewidths=2)
        
        # Date label
        ax.text(x, -0.6 if position == "top" else 0.6, date, 
               ha='center', va='top' if position == "top" else 'bottom',
               fontsize=10, color=GOLD, fontweight='bold')
        
        # Event box
        bbox_props = dict(boxstyle='round,pad=0.5', facecolor=color, alpha=0.2,
                         edgecolor=color, linewidth=2)
        ax.text(x, y_offset, event, ha='center', 
               va='bottom' if position == "top" else 'top',
               fontsize=9, color=WHITE, bbox=bbox_props,
               multialignment='center')
    
    # Title
    ax.text(6, 4, "TIMELINE OF REVELATIONS", fontsize=22, ha='center',
           color=GOLD, fontweight='bold', family='serif')
    ax.text(6, 3.4, "Major Developments in the Epstein Investigation (2019-2026)", 
           fontsize=11, ha='center', color=SILVER, style='italic')
    
    # Key milestones summary
    summary = """KEY MILESTONES:
• 2019: Subject's death triggers years of legal battles
• 2024: Giuffre v. Maxwell unsealing reveals 150+ names
• 2025: Transparency Act mandates federal disclosure
• 2026: Largest document release in DOJ history
         International arrests begin"""
    
    ax.text(0.5, 3.5, summary, fontsize=9, color=WHITE, family='monospace',
           bbox=dict(boxstyle='round', facecolor=TEAL, alpha=0.8),
           verticalalignment='top')
    
    # BPR&D branding
    ax.text(12, -3.5, "BPR&D SPECIAL REPORTS", fontsize=10, ha='right',
           color=GOLD, fontweight='bold')
    ax.text(12, -3.8, "February 2026", fontsize=8, ha='right', color=SILVER)
    
    ax.set_xlim(-1, 13)
    ax.set_ylim(-4, 4.5)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/github_repos/BPR-D/research/special-reports/assets/epstein-timeline.png',
               dpi=150, facecolor=DARK_BLUE, bbox_inches='tight')
    plt.close()
    print("✓ Timeline visualization saved")


# ============================================
# INFOGRAPHIC 3: Operational Patterns Analysis
# ============================================
def create_pattern_analysis():
    fig = plt.figure(figsize=(16, 12), facecolor=DARK_BLUE)
    
    # Create grid
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.25)
    
    # Title
    fig.suptitle("OPERATIONAL PATTERN ANALYSIS", fontsize=22, 
                color=GOLD, fontweight='bold', family='serif', y=0.97)
    fig.text(0.5, 0.93, "The Four Pillars of the Criminal Enterprise", 
            ha='center', fontsize=12, color=SILVER, style='italic')
    
    # ---- Panel 1: Geographic Distribution ----
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor(DARK_BLUE)
    
    locations = ['Little Saint\nJames (USVI)', 'Zorro Ranch\n(New Mexico)', 
                'Manhattan\nTownhouse', 'Palm Beach\nEstate']
    purposes = ['Primary\nTrafficking Hub', 'Eugenics\nOperations', 
               'Elite\nNetworking', 'Initial\nCrimes']
    colors = [CRIMSON, '#8B4513', GOLD, '#4a90a4']
    sizes = [400, 300, 250, 200]
    
    y_pos = np.arange(len(locations))
    ax1.barh(y_pos, sizes, color=colors, alpha=0.8, edgecolor=WHITE, linewidth=1)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(locations, fontsize=9, color=WHITE)
    ax1.set_xlabel('Operational Significance', fontsize=9, color=SILVER)
    ax1.set_title('GEOGRAPHIC DISTRIBUTION', fontsize=12, color=GOLD, pad=10)
    ax1.tick_params(colors=SILVER)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_color(SILVER)
    ax1.spines['left'].set_color(SILVER)
    
    # Add purpose labels
    for i, (size, purpose) in enumerate(zip(sizes, purposes)):
        ax1.text(size + 10, i, purpose, va='center', fontsize=8, color=SILVER)
    
    # ---- Panel 2: Financial Flow ----
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor(DARK_BLUE)
    
    # Sankey-style flow visualization
    flow_data = [
        ("Billionaire\nClients", 150, GOLD),
        ("Financial Trust\nCompany", 100, '#4a90a4'),
        ("Shell\nCompanies", 75, PURPLE),
        ("Cash\nWithdrawals", 50, CRIMSON),
        ("Victim\nPayments", 30, '#8B4513')
    ]
    
    y_positions = [4, 3, 2, 1, 0]
    for (label, width, color), y in zip(flow_data, y_positions):
        rect = FancyBboxPatch((0, y-0.35), width/10, 0.7, 
                             boxstyle="round,pad=0.02", 
                             facecolor=color, alpha=0.8, edgecolor=WHITE)
        ax2.add_patch(rect)
        ax2.text(width/10 + 0.5, y, label, va='center', fontsize=9, color=WHITE)
        
        # Draw flow arrows
        if y > 0:
            ax2.annotate('', xy=(0, y-0.35), xytext=(width/10, y+0.35-1),
                        arrowprops=dict(arrowstyle='->', color=SILVER, alpha=0.5))
    
    ax2.set_xlim(-1, 20)
    ax2.set_ylim(-1, 5)
    ax2.axis('off')
    ax2.set_title('FINANCIAL FLOW PATTERN', fontsize=12, color=GOLD, pad=10)
    
    # ---- Panel 3: Modus Operandi Cycle ----
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.set_facecolor(DARK_BLUE)
    
    # Circular process diagram
    stages = [
        ("1. RECRUIT", "Target vulnerable\nyoung women", GOLD),
        ("2. GROOM", "False promises\nof opportunity", '#4a90a4'),
        ("3. ISOLATE", "Transport to\nremote locations", PURPLE),
        ("4. ABUSE", "Systematic\nexploitation", CRIMSON),
        ("5. COERCE", "Victims become\nrecruiters", '#8B4513'),
    ]
    
    center = (0, 0)
    radius = 2
    angles = np.linspace(np.pi/2, np.pi/2 - 2*np.pi, len(stages), endpoint=False)
    
    for (label, desc, color), angle in zip(stages, angles):
        x = center[0] + radius * np.cos(angle)
        y = center[1] + radius * np.sin(angle)
        
        circle = Circle((x, y), 0.5, color=color, alpha=0.8, zorder=2)
        ax3.add_patch(circle)
        ax3.text(x, y, label.split('.')[0], ha='center', va='center', 
                fontsize=8, color=WHITE, fontweight='bold')
        
        # Description outside
        desc_x = center[0] + (radius + 1.2) * np.cos(angle)
        desc_y = center[1] + (radius + 1.2) * np.sin(angle)
        ax3.text(desc_x, desc_y, f"{label}\n{desc}", ha='center', va='center',
                fontsize=7, color=SILVER, multialignment='center')
    
    # Central text
    ax3.text(0, 0, "CYCLE", ha='center', va='center', fontsize=10, 
            color=GOLD, fontweight='bold')
    
    ax3.set_xlim(-4.5, 4.5)
    ax3.set_ylim(-4, 4)
    ax3.axis('off')
    ax3.set_title('MODUS OPERANDI', fontsize=12, color=GOLD, pad=10)
    
    # ---- Panel 4: Entity Mention Frequency ----
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.set_facecolor(DARK_BLUE)
    
    entities = ['Lesley Groff\n(Assistant)', 'Richard Kahn\n(Accountant)', 
               'Darren Indyke\n(Lawyer)', 'Ghislaine Maxwell\n(Recruiter)']
    mentions = [157000, 52000, 17000, 13000]
    colors = [GOLD, '#4a90a4', PURPLE, CRIMSON]
    
    bars = ax4.barh(entities, [m/1000 for m in mentions], color=colors, alpha=0.8,
                   edgecolor=WHITE, linewidth=1)
    ax4.set_xlabel('Document Mentions (thousands)', fontsize=9, color=SILVER)
    ax4.set_title('INNER CIRCLE DOCUMENT MENTIONS', fontsize=12, color=GOLD, pad=10)
    ax4.tick_params(colors=SILVER)
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)
    ax4.spines['bottom'].set_color(SILVER)
    ax4.spines['left'].set_color(SILVER)
    
    # Add count labels
    for bar, count in zip(bars, mentions):
        ax4.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
                f'{count:,}', va='center', fontsize=8, color=SILVER)
    
    # BPR&D branding
    fig.text(0.95, 0.02, "BPR&D SPECIAL REPORTS | February 2026", 
            ha='right', fontsize=10, color=GOLD, fontweight='bold')
    
    plt.savefig('/home/ubuntu/github_repos/BPR-D/research/special-reports/assets/epstein-patterns.png',
               dpi=150, facecolor=DARK_BLUE, bbox_inches='tight')
    plt.close()
    print("✓ Pattern analysis visualization saved")


# ============================================
# Main execution
# ============================================
if __name__ == "__main__":
    print("Generating BPR&D Epstein Investigation Infographics...")
    print("=" * 50)
    
    create_network_visualization()
    create_timeline()
    create_pattern_analysis()
    
    print("=" * 50)
    print("All infographics generated successfully!")
    print("Location: /home/ubuntu/github_repos/BPR-D/research/special-reports/assets/")
