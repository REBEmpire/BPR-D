import os
import sys
import json
import logging
import datetime
import shutil
from pathlib import Path
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
BASE_DIR = Path("research/epstein-daily")
SOURCE_DIR = BASE_DIR / "source_docs"
UNPROCESSED_DIR = BASE_DIR / "unprocessed"
PROCESSED_DIR = BASE_DIR / "processed"
OUTPUT_DIR = BASE_DIR / "nightly-output"
GRAPH_FILE = BASE_DIR / "graph/epstein_graph.json"
HANDOFFS_DIR = Path("_agents/_handoffs")

# Ensure directories exist
for d in [UNPROCESSED_DIR, PROCESSED_DIR, OUTPUT_DIR, GRAPH_FILE.parent, HANDOFFS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Third-party imports check
try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    logger.warning("networkx not found. Graph operations will be limited.")

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    logger.warning("matplotlib not found. Visualization will be limited to DOT/HTML.")

try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False
    logger.warning("pypdf not found. PDF text extraction will be disabled.")

try:
    from abacusai import ApiClient
    HAS_ABACUS = True
except ImportError:
    HAS_ABACUS = False
    logger.warning("abacusai not found. LLM features will be disabled.")

try:
    import pydot
    HAS_PYDOT = True
except ImportError:
    HAS_PYDOT = False

# --- LLM Configuration ---
ABACUS_API_KEY = os.environ.get("ABACUS_PRIMARY_KEY") or os.environ.get("ABACUS_API_KEY") or "s2_1e30fa4a3d834bffb1b465d67eb1809e"
ABACUS_DEPLOYMENT_TOKEN = os.environ.get("ABACUS_DEPLOYMENT_TOKEN") or "77467e7299eb40a29b6234556cb414e5"
ABACUS_DEPLOYMENT_ID = os.environ.get("ABACUS_DEPLOYMENT_ID") or "7cde35efc"

def get_llm_client():
    if not HAS_ABACUS:
        return None
    try:
        return ApiClient(api_key=ABACUS_API_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize Abacus client: {e}")
        return None

def call_llm(prompt, client=None):
    if not client:
        client = get_llm_client()
    if not client:
        return None
    messages = [{"is_user": True, "text": prompt}]
    try:
        response = client.get_chat_response(
            deployment_token=ABACUS_DEPLOYMENT_TOKEN,
            deployment_id=ABACUS_DEPLOYMENT_ID,
            messages=messages
        )
        if isinstance(response, dict):
            msgs = response.get('messages', [])
            if msgs: return msgs[-1].get('text', '')
            return str(response)
        else:
            if hasattr(response, 'messages'):
                msgs = response.messages
                if msgs: return msgs[-1].text
            return str(response)
    except Exception as e:
        logger.error(f"LLM Call Failed: {e}")
        return None

def extract_text_from_pdf(file_path):
    if not HAS_PYPDF: return ""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logger.error(f"Error reading PDF {file_path}: {e}")
        return ""

def analyze_document_llm(content, filename):
    if not content or not content.strip(): return None
    prompt = f"""You are an expert investigative analyst processing the Epstein Archive.
Analyze the following text from document '{filename}'.
Extract:
1. Entities: People, Organizations, Locations, Dates.
2. Relationships: Interactions between entities.
3. Anomalies: Suspicious patterns, contradictions, or oddities.
Format as JSON:
{{
    "entities": [{{"name": "Name", "type": "PERSON/ORG/LOC/DATE", "confidence": 0-100}}],
    "relationships": [{{"source": "Entity1", "target": "Entity2", "type": "met/flew/associated", "confidence": 0-100, "rationale": "Why", "provenance": "quote"}}],
    "anomalies": ["Anomaly 1"]
}}
Strictly JSON only.
Text: {content[:15000]}"""
    response_text = call_llm(prompt)
    if not response_text: return None

    # Try to extract JSON block
    match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if match:
        clean_text = match.group(0)
    else:
        clean_text = response_text

    try:
        data = json.loads(clean_text)
        return data
    except json.JSONDecodeError:
        logger.error(f"Failed to parse LLM JSON for {filename}")
        logger.debug(f"Raw response: {response_text}")
        return None

def ingest_files():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    dest_dir = PROCESSED_DIR / today
    dest_dir.mkdir(parents=True, exist_ok=True)
    files_to_process = []
    processed_data = []

    for file_path in UNPROCESSED_DIR.glob("*"):
        if file_path.is_file():
            try:
                dest_path = dest_dir / file_path.name
                shutil.move(str(file_path), str(dest_path))
                files_to_process.append(dest_path)
            except Exception as e:
                logger.error(f"Error moving {file_path}: {e}")

    # Copy handoffs
    handoff_files = list(HANDOFFS_DIR.glob("*.md")) + list(HANDOFFS_DIR.glob("*.txt"))
    for file_path in handoff_files:
        if file_path.name.startswith("handoff-epstein"): continue
        try:
            dest_path = dest_dir / file_path.name
            shutil.copy(str(file_path), str(dest_path))
            files_to_process.append(dest_path)
        except Exception as e:
            logger.error(f"Error copying handoff {file_path}: {e}")

    for file_path in files_to_process:
        logger.info(f"Processing {file_path.name}...")
        content = ""
        if file_path.suffix.lower() == ".pdf":
            content = extract_text_from_pdf(file_path)
            if not content.strip():
                logger.warning(f"PDF {file_path.name} appears empty or scanned.")
        else:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                logger.error(f"Error reading text file {file_path}: {e}")

        if content:
            analysis = analyze_document_llm(content, file_path.name)
            if analysis:
                processed_data.append((file_path, analysis))
            else:
                logger.warning(f"No analysis result for {file_path.name}")
    return processed_data

def load_graph():
    if GRAPH_FILE.exists():
        try:
            with open(GRAPH_FILE, 'r') as f:
                data = json.load(f)
            if HAS_NETWORKX:
                # Check for legacy format
                if 'adj' in data:
                    logger.info("Migrating legacy graph format...")
                    G = nx.Graph()
                    for node, attrs in data.get('nodes', {}).items():
                        G.add_node(node, **attrs)
                    for u, neighbors in data.get('adj', {}).items():
                        for v, edge_attrs in neighbors.items():
                            if not G.has_edge(u, v):
                                G.add_edge(u, v, **edge_attrs)
                    return G
                else:
                    return nx.node_link_graph(data)
            else: return data
        except Exception as e:
            logger.error(f"Error loading graph: {e}")
            return nx.Graph() if HAS_NETWORKX else {"nodes": {}, "links": []}
    return nx.Graph() if HAS_NETWORKX else {"nodes": {}, "links": []}

def save_graph(G):
    try:
        if HAS_NETWORKX: data = nx.node_link_data(G)
        else: data = G
        with open(GRAPH_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving graph: {e}")

def update_knowledge_graph(G, processed_data):
    new_nodes_count = 0
    new_edges_count = 0
    anomalies = []
    for file_path, analysis in processed_data:
        for ent in analysis.get("entities", []):
            name = ent.get("name")
            etype = ent.get("type", "UNKNOWN")
            conf = ent.get("confidence", 0)
            if HAS_NETWORKX:
                if not G.has_node(name):
                    G.add_node(name, type=etype, confidence=conf, sources=[file_path.name])
                    new_nodes_count += 1
                else:
                    G.nodes[name]['sources'] = G.nodes[name].get('sources', []) + [file_path.name]

        for rel in analysis.get("relationships", []):
            src = rel.get("source")
            tgt = rel.get("target")
            rtype = rel.get("type", "associated")
            conf = rel.get("confidence", 0)
            rat = rel.get("rationale", "")
            prov = rel.get("provenance", "")
            if src and tgt:
                if HAS_NETWORKX:
                    if not G.has_edge(src, tgt):
                        G.add_edge(src, tgt, type=rtype, confidence=conf, rationale=rat, provenance=[prov], weight=1)
                        new_edges_count += 1
                    else:
                        G[src][tgt]['weight'] = G[src][tgt].get('weight', 0) + 1
                        G[src][tgt]['provenance'] = G[src][tgt].get('provenance', []) + [prov]

        for anom in analysis.get("anomalies", []):
            anomalies.append(f"[{file_path.name}] {anom}")
    return new_nodes_count, new_edges_count, anomalies

def detect_anomalies(G, processed_data):
    anomalies = []
    if HAS_NETWORKX:
        degrees = sorted(G.degree, key=lambda x: x[1], reverse=True)[:5]
        for n, d in degrees:
            if d > 10: anomalies.append(f"High Degree Node: {n} ({d} connections)")
    return anomalies

def generate_visuals(G, output_dir):
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    dot_path = output_dir / f"epstein_network_{timestamp}.dot"
    try:
        if HAS_NETWORKX:
            nx.drawing.nx_pydot.write_dot(G, dot_path)
            logger.info(f"DOT file saved to {dot_path}")
    except Exception as e:
        logger.warning(f"Failed to generate DOT with pydot: {e}. Trying manual fallback.")
        try:
             with open(dot_path, 'w') as f:
                f.write("graph G {\n")
                if HAS_NETWORKX:
                    for u, v in G.edges():
                        f.write(f'  "{u}" -- "{v}";\n')
                f.write("}\n")
             logger.info(f"Manual DOT file saved to {dot_path}")
        except Exception as e2:
            logger.error(f"Manual DOT fallback failed: {e2}")

    html_path = output_dir / f"report_{timestamp}.html"
    try:
        if HAS_NETWORKX: graph_data = nx.node_link_data(G)
        else: graph_data = G
        json_str = json.dumps(graph_data)
        html_content = f"""<!DOCTYPE html><html><head><title>Epstein Network Graph</title>
<style>body{{margin:0;overflow:hidden}}#graph{{width:100vw;height:100vh}}</style>
<script src="https://d3js.org/d3.v7.min.js"></script></head><body><div id="graph"></div>
<script>const data={json_str};const width=window.innerWidth;const height=window.innerHeight;
const svg=d3.select("#graph").append("svg").attr("width",width).attr("height",height);
const simulation=d3.forceSimulation(data.nodes).force("link",d3.forceLink(data.links).id(d=>d.id).distance(100))
.force("charge",d3.forceManyBody().strength(-300)).force("center",d3.forceCenter(width/2,height/2));
const link=svg.append("g").selectAll("line").data(data.links).enter().append("line").attr("stroke","#999").attr("stroke-width",d=>Math.sqrt(d.weight||1));
const node=svg.append("g").selectAll("circle").data(data.nodes).enter().append("circle").attr("r",5).attr("fill",d=>d.type==='PERSON'?'blue':'orange')
.call(d3.drag().on("start",dragstarted).on("drag",dragged).on("end",dragended));
node.append("title").text(d=>d.id);
simulation.on("tick",()=>{{link.attr("x1",d=>d.source.x).attr("y1",d=>d.source.y).attr("x2",d=>d.target.x).attr("y2",d=>d.target.y);
node.attr("cx",d=>d.x).attr("cy",d=>d.y);}});
function dragstarted(event,d){{if(!event.active)simulation.alphaTarget(0.3).restart();d.fx=d.x;d.fy=d.y;}}
function dragged(event,d){{d.fx=event.x;d.fy=event.y;}}
function dragended(event,d){{if(!event.active)simulation.alphaTarget(0);d.fx=null;d.fy=null;}}</script></body></html>"""
        with open(html_path, 'w') as f: f.write(html_content)
        logger.info(f"HTML report saved to {html_path}")
    except Exception as e: logger.error(f"Failed HTML: {e}")
    return str(html_path)

def generate_handoff_brief(processed_data, new_nodes, new_edges, anomalies, output_dir):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    handoff_path = HANDOFFS_DIR / f"handoff-epstein-{today.replace('-','')}.md"
    with open(handoff_path, 'w') as f:
        f.write(f"# Nightly Epstein Archive Handoff – {today}\n\n")
        f.write("## Executive Summary\n")
        f.write(f"Processed {len(processed_data)} documents. Added {new_nodes} entities, {new_edges} edges.\n\n")
        f.write("## Anomalies\n")
        for a in anomalies: f.write(f"- {a}\n")
        f.write("\n## Sources\n")
        for p, _ in processed_data: f.write(f"- {p.name}\n")
    logger.info(f"Handoff brief generated: {handoff_path}")

def main():
    logger.info("Starting Nightly Epstein Archive Processor...")
    processed_data = ingest_files()
    G = load_graph()
    new_nodes, new_edges, doc_anomalies = update_knowledge_graph(G, processed_data)
    save_graph(G)
    logger.info(f"Graph updated: +{new_nodes} nodes, +{new_edges} edges")
    all_anomalies = doc_anomalies + detect_anomalies(G, processed_data)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    daily_output_dir = OUTPUT_DIR / today
    daily_output_dir.mkdir(parents=True, exist_ok=True)
    generate_visuals(G, daily_output_dir)
    generate_handoff_brief(processed_data, new_nodes, new_edges, all_anomalies, daily_output_dir)
    logger.info("Processing complete.")

if __name__ == "__main__":
    main()
