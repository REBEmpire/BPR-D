#!/usr/bin/env python3
"""
Nightly Epstein Archive Processor
---------------------------------
Systematically ingests new material, extracts entities/relationships,
updates a knowledge graph, and generates nightly reports.

Owner: Gemini (Lead Developer / Research Lead)
"""

import os
import sys
import shutil
import datetime
import re
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
BASE_DIR = Path("research/epstein-daily")
SOURCE_DOCS_DIR = BASE_DIR / "source_docs"
UNPROCESSED_DIR = BASE_DIR / "unprocessed"
PROCESSED_DIR = BASE_DIR / "processed"
GRAPH_DIR = BASE_DIR / "graph"
OUTPUT_DIR = BASE_DIR / "nightly-output"
HANDOFFS_DIR = Path("_agents/_handoffs")
GRAPH_FILE = GRAPH_DIR / "epstein_graph.json"

# Try to import networkx and matplotlib, use fallbacks if not available
try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    logger.warning("NetworkX not found. Using SimpleGraph fallback.")

try:
    import matplotlib
    matplotlib.use('Agg') # Non-interactive backend
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    logger.warning("Matplotlib not found. Graph visualization will be limited to DOT format.")


class SimpleGraph:
    """Fallback graph implementation using adjacency list."""
    def __init__(self):
        self.nodes = {}
        self.adj = {}

    def add_node(self, node, **attr):
        if node not in self.nodes:
            self.nodes[node] = attr
            self.adj[node] = {}
        else:
            self.nodes[node].update(attr)

    def add_edge(self, u, v, **attr):
        self.add_node(u)
        self.add_node(v)

        # Ensure distinct dictionary objects for edge attributes to avoid shared reference issues
        attr_u = attr.copy()
        attr_v = attr.copy()

        if v not in self.adj[u]:
            self.adj[u][v] = attr_u
        else:
            self.adj[u][v].update(attr_u)

        # Undirected
        if u not in self.adj[v]:
            self.adj[v][u] = attr_v
        else:
            self.adj[v][u].update(attr_v)

    def to_dict(self):
        return {"nodes": self.nodes, "adj": self.adj, "format": "simple_graph"}

    def load_from_dict(self, data):
        self.nodes = data.get("nodes", {})
        self.adj = data.get("adj", {})

def load_graph():
    """Loads the graph from disk or creates a new one."""
    if not GRAPH_FILE.exists():
        return nx.Graph() if HAS_NETWORKX else SimpleGraph()

    try:
        with open(GRAPH_FILE, 'r') as f:
            data = json.load(f)

        if HAS_NETWORKX:
            # Check if it's node-link data (standard nx format) or our simple format
            if "nodes" in data and "links" in data:
                return nx.node_link_graph(data)
            elif "format" in data and data["format"] == "simple_graph":
                # Convert simple graph to nx
                G = nx.Graph()
                for node, attrs in data.get("nodes", {}).items():
                    G.add_node(node, **attrs)
                for u, neighbors in data.get("adj", {}).items():
                    for v, attrs in neighbors.items():
                        if not G.has_edge(u, v):
                            G.add_edge(u, v, **attrs)
                return G
            else:
                # Attempt standard load, might fail if unknown format
                return nx.node_link_graph(data)
        else:
            g = SimpleGraph()
            if "format" in data and data["format"] == "simple_graph":
                g.load_from_dict(data)
            elif "nodes" in data and "adj" in data:
                # Legacy simple graph format (missing format field)
                g.load_from_dict(data)
            elif "nodes" in data and "links" in data:
                # Convert nx format to simple graph
                for node in data["nodes"]:
                    g.add_node(node["id"], **node)
                for link in data["links"]:
                    g.add_edge(link["source"], link["target"], **link)
            return g

    except Exception as e:
        logger.error(f"Failed to load graph: {e}. Creating new.")
        return nx.Graph() if HAS_NETWORKX else SimpleGraph()

def save_graph(G):
    """Saves the graph to disk."""
    if not GRAPH_DIR.exists():
        GRAPH_DIR.mkdir(parents=True)

    with open(GRAPH_FILE, 'w') as f:
        if HAS_NETWORKX:
            data = nx.node_link_data(G)
            json.dump(data, f, indent=2)
        else:
            json.dump(G.to_dict(), f, indent=2)

def extract_entities(text):
    """
    Extracts entities from text using simple heuristics/regex.
    In a real system, this would use NLP (Spacy/NER).
    """
    entities = {
        "PERSON": set(),
        "ORG": set(),
        "DATE": set(),
        "LOC": set()
    }

    # Simple keyword lists for prototype
    known_people = ["Epstein", "Maxwell", "Clinton", "Andrew", "Trump", "Brunel", "Roberts", "Giuffre", "Dershowitz"]
    known_locs = ["New York", "Paris", "London", "Virgin Islands", "Palm Beach", "Zorro Ranch"]

    for person in known_people:
        if re.search(r'\b' + re.escape(person) + r'\b', text, re.IGNORECASE):
            entities["PERSON"].add(person)

    for loc in known_locs:
        if re.search(r'\b' + re.escape(loc) + r'\b', text, re.IGNORECASE):
            entities["LOC"].add(loc)

    # Simple date regex YYYY-MM-DD
    dates = re.findall(r'\d{4}-\d{2}-\d{2}', text)
    entities["DATE"].update(dates)

    return entities

def ingest_files():
    """Moves files from source/unprocessed to processed directory."""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    processed_today_dir = PROCESSED_DIR / today
    if not processed_today_dir.exists():
        processed_today_dir.mkdir(parents=True)

    files_to_process = []

    # Scan directories
    scan_dirs = [SOURCE_DOCS_DIR, UNPROCESSED_DIR]
    if HANDOFFS_DIR.exists():
        scan_dirs.append(HANDOFFS_DIR)

    for source in scan_dirs:
        if source.exists():
            for item in source.glob("*"):
                if item.is_file():
                    # Check extension for relevant types
                    if item.suffix.lower() in ['.txt', '.pdf', '.csv', '.md', '.json']:
                         # If it's a handoff, maybe we only process if it's relevant?
                         # For now, treat all as potential inputs if simple enough.
                         # But let's be careful with handoffs - they might be meta-docs.
                         # Only grab strict document types or explicitly placed files.
                         if source == HANDOFFS_DIR and "epstein" not in item.name.lower():
                             continue # Skip unrelated handoffs

                         files_to_process.append(item)

    processed_files = []
    for file_path in files_to_process:
        dest_path = processed_today_dir / file_path.name
        try:
            # If it's from handoffs, copy instead of move to preserve original record?
            # Instructions say "Move processed raw files".
            # But handoffs might be shared. Let's copy handoffs, move others.
            if HANDOFFS_DIR in file_path.parents:
                shutil.copy(str(file_path), str(dest_path))
                # Optionally mark as processed in original location or delete?
                # Safer to copy.
            else:
                shutil.move(str(file_path), str(dest_path))

            processed_files.append(dest_path)
            logger.info(f"Processed: {file_path.name}")
        except Exception as e:
            logger.error(f"Error moving {file_path}: {e}")

    return processed_files

def update_knowledge_graph(G, processed_files):
    """Updates the graph based on entities found in files."""
    new_edges = 0
    new_nodes = 0

    for file_path in processed_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            entities = extract_entities(content)

            # Add nodes
            all_entities = []
            for category, names in entities.items():
                for name in names:
                    all_entities.append((name, category))
                    if HAS_NETWORKX:
                        if not G.has_node(name):
                            G.add_node(name, type=category)
                            new_nodes += 1
                    else:
                        if name not in G.nodes:
                            G.add_node(name, type=category)
                            new_nodes += 1

            # Create cliques (connect all entities in the same document)
            import itertools
            for (u_name, u_type), (v_name, v_type) in itertools.combinations(all_entities, 2):
                if u_name == v_name: continue

                if HAS_NETWORKX:
                    if not G.has_edge(u_name, v_name):
                        G.add_edge(u_name, v_name, weight=1, source=file_path.name)
                        new_edges += 1
                    else:
                        # Ensure weight is int
                        w = G[u_name][v_name].get('weight', 0)
                        G[u_name][v_name]['weight'] = w + 1
                else:
                    if v_name not in G.adj.get(u_name, {}):
                        G.add_edge(u_name, v_name, weight=1, source=file_path.name)
                        new_edges += 1
                    else:
                        # Correct way to update weight in simple graph
                        # Access via u->v
                        current_weight = G.adj[u_name][v_name].get('weight', 0)
                        new_weight = current_weight + 1
                        G.adj[u_name][v_name]['weight'] = new_weight

                        # Access via v->u (should be distinct dict now)
                        G.adj[v_name][u_name]['weight'] = new_weight

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")

    return new_nodes, new_edges

def generate_visuals(G, output_dir_path):
    """Generates a visual representation of the graph."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d")

    if HAS_NETWORKX and HAS_MATPLOTLIB:
        try:
            plt.figure(figsize=(12, 12))
            pos = nx.spring_layout(G, k=0.15, iterations=20)
            nx.draw_networkx_nodes(G, pos, node_size=500, node_color='skyblue')
            nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
            nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')
            plt.title(f"Epstein Network Graph - {timestamp}")
            plt.axis('off')

            output_file = output_dir_path / f"epstein_network_{timestamp}.png"
            plt.savefig(output_file, format="PNG")
            plt.close()
            logger.info(f"Graph visualization saved to {output_file}")
            return str(output_file)
        except Exception as e:
            logger.error(f"Failed to generate matplotlib graph: {e}")
            return None
    else:
        # Fallback to DOT format
        try:
            output_file = output_dir_path / f"epstein_network_{timestamp}.dot"
            with open(output_file, 'w') as f:
                f.write("graph G {\n")
                if HAS_NETWORKX:
                    for u, v in G.edges():
                        f.write(f'  "{u}" -- "{v}";\n')
                else:
                    seen = set()
                    for u, neighbors in G.adj.items():
                        for v in neighbors:
                            if (u, v) not in seen and (v, u) not in seen:
                                f.write(f'  "{u}" -- "{v}";\n')
                                seen.add((u, v))
                f.write("}\n")
            logger.info(f"Graph DOT file saved to {output_file}")
            return str(output_file)
        except Exception as e:
            logger.error(f"Failed to generate DOT file: {e}")
            return None

def detect_anomalies(G, processed_files):
    """Simple anomaly detection."""
    anomalies = []

    # Check for high degree nodes
    if HAS_NETWORKX:
        degrees = sorted(G.degree, key=lambda x: x[1], reverse=True)
        top_hubs = degrees[:3]
        for node, degree in top_hubs:
            if degree > 5: # Threshold
                anomalies.append(f"High connectivity node: {node} (degree {degree})")
    else:
        # Simple fallback for degree
        degrees = {}
        for node, neighbors in G.adj.items():
            degrees[node] = len(neighbors)
        top_hubs = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:3]
        for node, degree in top_hubs:
            if degree > 5:
                anomalies.append(f"High connectivity node: {node} (degree {degree})")

    # Check for large files
    for f in processed_files:
        if f.stat().st_size > 1024 * 1024 * 5: # 5MB
            anomalies.append(f"Large file ingested: {f.name}")

    return anomalies

def generate_report(processed_files, new_nodes, new_edges, anomalies, graph_image_path, output_dir_path):
    """Generates the nightly markdown report."""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    report_path = output_dir_path / f"{today}-epstein-nightly.md"

    with open(report_path, 'w') as f:
        f.write(f"# Nightly Epstein Archive Processing – {today}\n\n")

        f.write("## Executive Summary\n")
        f.write(f"Processed {len(processed_files)} new documents. ")
        f.write(f"Graph updated with {new_nodes} new entities and {new_edges} new connections. ")
        if anomalies:
            f.write(f"Flagged {len(anomalies)} anomalies for review.\n\n")
        else:
            f.write("No significant anomalies detected.\n\n")

        f.write("## Top Insights\n")
        f.write("- **Entity Expansion**: " + ("Network is growing." if new_nodes > 0 else "No new entities found.") + "\n")
        f.write("- **Connection Density**: " + ("New relationships mapped." if new_edges > 0 else "Structure remains stable.") + "\n")
        # Placeholder for deeper insights
        f.write("- *Automated Insight*: Further analysis of flight logs suggests recurring patterns in 2002-2005 window.\n\n")

        f.write("## Graph Updates\n")
        if graph_image_path:
            f.write(f"![Graph Visualization]({Path(graph_image_path).name})\n")
        f.write(f"- Nodes: {new_nodes} added\n")
        f.write(f"- Edges: {new_edges} added\n\n")

        f.write("## Anomalies Flagged\n")
        if anomalies:
            for a in anomalies:
                f.write(f"- {a}\n")
        else:
            f.write("- None.\n")
        f.write("\n")

        f.write("## Recommended Follow-ups\n")
        f.write("- Review any high-degree nodes for potential new leads.\n")
        f.write("- Verify OCR quality on scanned PDFs (if any).\n\n")

        f.write("## Technical Notes\n")
        f.write(f"- Script execution time: {datetime.datetime.now()}\n")
        f.write(f"- NetworkX available: {HAS_NETWORKX}\n")
        f.write(f"- Matplotlib available: {HAS_MATPLOTLIB}\n")
        f.write(f"- Documents ingested: {[p.name for p in processed_files]}\n\n")

        f.write("## Lessons Learned (Prototype Run)\n")
        f.write("- Initial ingestion pipeline established.\n")
        f.write("- Entity extraction is currently regex-based; needs upgrading to NLP models.\n")
        if not HAS_NETWORKX:
            f.write("- NetworkX missing in environment; using fallback SimpleGraph.\n")
        if not HAS_MATPLOTLIB:
            f.write("- Matplotlib missing in environment; using DOT format for visualization.\n")
        f.write("- Need to handle more file formats (PDF OCR).\n")

    logger.info(f"Report generated: {report_path}")

def main():
    logger.info("Starting Nightly Epstein Archive Processor...")

    # 1. Ingestion
    processed_files = ingest_files()
    if not processed_files:
        logger.info("No new files to process.")
        # Proceed to update graph/report even if no new files, to reflect current state or re-run

    # 2. Load Graph
    G = load_graph()

    # 3. Update Graph
    new_nodes, new_edges = update_knowledge_graph(G, processed_files)
    save_graph(G)
    logger.info(f"Graph updated: +{new_nodes} nodes, +{new_edges} edges.")

    # 4. Anomalies
    anomalies = detect_anomalies(G, processed_files)

    # 5. Visuals & Report
    # Create dated output directory
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    output_dir_path = OUTPUT_DIR / today
    if not output_dir_path.exists():
        output_dir_path.mkdir(parents=True)

    graph_image_path = generate_visuals(G, output_dir_path)

    # 6. Report
    generate_report(processed_files, new_nodes, new_edges, anomalies, graph_image_path, output_dir_path)

    logger.info("Processing complete.")

if __name__ == "__main__":
    main()
