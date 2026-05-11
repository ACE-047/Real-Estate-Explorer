import io
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')          # Non-interactive, fully thread-safe — no Tkinter needed
import matplotlib.pyplot as plt
import networkx as nx
from UTILITY import get_bracket,clean_area_list,clean_currency_list,get_area_bracket



# ── Internal helpers ────────────────────────────────────────────────────────

def kde(d, r):
    if d <= r:
        return (1 - (d / r) ** 2) ** 2
    return 0

def _fig_to_png(fig) -> bytes:
    """Render a matplotlib figure to PNG bytes and close it."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf.read()


# ── Public analysis functions ────────────────────────────────────────────────

def run_kde_analysis(area_nums, price_nums) -> bytes | None:
    """
    Returns PNG bytes of the KDE heatmap, or None if there is not enough data.
    Safe to call from any thread.
    """
    if len(area_nums) < 2 or (area_nums.max() == area_nums.min()):
        print("Not enough variation in data to generate a heatmap.")
        return None

    a_min, a_max = area_nums.min(), area_nums.max()
    p_min, p_max = price_nums.min(), price_nums.max()

    a_norm = (area_nums - a_min) / (a_max - a_min) if a_max != a_min else area_nums
    p_norm = (price_nums - p_min) / (p_max - p_min) if p_max != p_min else price_nums

    grid_size = 100
    a_grid = np.linspace(0, 1, grid_size)
    p_grid = np.linspace(0, 1, grid_size)
    Z = np.zeros((grid_size, grid_size))

    r = 0.2
    for i, ag in enumerate(a_grid):
        for j, pg in enumerate(p_grid):
            total = 0.0
            for an, pn in zip(a_norm, p_norm):
                d = np.sqrt((ag - an) ** 2 + (pg - pn) ** 2)
                total += kde(d, r)
            Z[j, i] = total

    a_axis = a_grid * (a_max - a_min) + a_min
    p_axis = p_grid * (p_max - p_min) + p_min

    fig, ax = plt.subplots(figsize=(10, 7))
    cf = ax.contourf(a_axis, p_axis, Z, levels=20, cmap='YlOrRd')
    fig.colorbar(cf, ax=ax, label='Density')
    ax.scatter(area_nums, price_nums, color='blue', s=15, alpha=0.5, label='Properties')
    ax.set_xlabel('Area (m²)')
    ax.set_ylabel('Price (EGP)')
    ax.set_title('KDE Heatmap: Property Area vs Price')
    ax.legend()
    fig.tight_layout()

    return _fig_to_png(fig)


def run_network_analysis(compounds, price_nums, area_nums) -> bytes | None:
    """
    Builds a compound similarity network and returns PNG bytes.
    Safe to call from any thread.
    """
    G = nx.Graph()

    compound_profiles: dict[str, set] = {}
    for compound, price, area in zip(compounds, price_nums, area_nums):
        if compound == "N/A":
            continue
        pb = get_bracket(price)
        ab = get_area_bracket(area)
        compound_profiles.setdefault(compound, set()).add((pb, ab))

    for compound in compound_profiles:
        G.add_node(compound)

    compound_list = list(compound_profiles.keys())
    for i in range(len(compound_list)):
        for j in range(i + 1, len(compound_list)):
            c1, c2 = compound_list[i], compound_list[j]
            if compound_profiles[c1] & compound_profiles[c2]:
                G.add_edge(c1, c2)

    if len(G.nodes) == 0:
        print("No compound data to build network.")
        return None

    centrality = nx.betweenness_centrality(G)

    print("\n--- Betweenness Centrality (Top Bridge Compounds) ---")
    for compound, score in sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {compound}: {score:.4f}")

    fig, ax = plt.subplots(figsize=(14, 9))
    pos = nx.spring_layout(G, seed=42, k=1.5)

    node_sizes  = [3000 * centrality[n] + 300 for n in G.nodes]
    node_colors = [centrality[n] for n in G.nodes]

    nodes = nx.draw_networkx_nodes(G, pos, node_size=node_sizes,node_color=node_colors, cmap=plt.cm.YlOrRd,alpha=0.9, ax=ax)
    nx.draw_networkx_edges(G, pos, alpha=0.3, edge_color='gray', ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=7, font_weight='bold', ax=ax)

    fig.colorbar(nodes, ax=ax, label='Betweenness Centrality')
    ax.set_title(
        "Compound Similarity Network\n"
        "(Node size & color = Betweenness Centrality — larger means more of a market bridge)"
    )
    ax.axis('off')
    fig.tight_layout()

    return _fig_to_png(fig)


def run_3d_cloud_analysis(df) -> bytes:
    fig = plt.figure(figsize=(10, 8))
    ax  = fig.add_subplot(111, projection='3d')

    x = df['area_clean']
    y = df['bed_clean']
    z = df['price_clean']

    sc = ax.scatter(x, y, z, c=z, cmap='viridis', marker='o', s=50, alpha=0.6)

    ax.set_xlabel('Area (m²)')
    ax.set_ylabel('Bedrooms')
    ax.set_zlabel('Price (EGP)')
    ax.set_title('3D Real Estate Point Cloud Analysis')
    fig.colorbar(sc, ax=ax, label='Price Scale')
    fig.tight_layout()

    return _fig_to_png(fig)
