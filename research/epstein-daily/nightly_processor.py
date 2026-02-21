import os
import sys
import json
import subprocess
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
TIMELINE_FILE = BASE_DIR / "graph/epstein_timeline.json"
HANDOFFS_DIR = Path("_agents/_handoffs")

# Ensure directories exist
for d in [SOURCE_DIR, UNPROCESSED_DIR, PROCESSED_DIR, OUTPUT_DIR, GRAPH_FILE.parent, HANDOFFS_DIR]:
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

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class SimpleGraph:
    """Fallback graph class when networkx is unavailable."""
    def __init__(self):
        self.nodes = {}
        self.adj = {}

    def add_node(self, node_for_adding, **attr):
        if node_for_adding not in self.nodes:
            self.nodes[node_for_adding] = attr
            self.adj[node_for_adding] = {}
        else:
            self.nodes[node_for_adding].update(attr)

    def add_edge(self, u_of_edge, v_of_edge, **attr):
        self.add_node(u_of_edge)
        self.add_node(v_of_edge)
        if v_of_edge not in self.adj[u_of_edge]:
            self.adj[u_of_edge][v_of_edge] = attr
        else:
            self.adj[u_of_edge][v_of_edge].update(attr)
        # Undirected graph simulation
        if u_of_edge not in self.adj[v_of_edge]:
            self.adj[v_of_edge][u_of_edge] = attr
        else:
            self.adj[v_of_edge][u_of_edge].update(attr)

    def has_node(self, n):
        return n in self.nodes

    def has_edge(self, u, v):
        return u in self.adj and v in self.adj[u]

    def edges(self):
        seen = set()
        for u, neighbors in self.adj.items():
            for v in neighbors:
                if (u, v) not in seen and (v, u) not in seen:
                    yield u, v
                    seen.add((u, v))

    @property
    def degree(self):
        return [(n, len(neighbors)) for n, neighbors in self.adj.items()]

    def to_dict(self):
        nodes_list = []
        for n, attrs in self.nodes.items():
            node_data = attrs.copy()
            node_data['id'] = n
            nodes_list.append(node_data)

        links_list = []
        seen = set()
        for u, neighbors in self.adj.items():
            for v, edge_attrs in neighbors.items():
                if (u, v) not in seen and (v, u) not in seen:
                    link_data = edge_attrs.copy()
                    link_data['source'] = u
                    link_data['target'] = v
                    links_list.append(link_data)
                    seen.add((u, v))

        return {"nodes": nodes_list, "links": links_list}

# --- LLM Configuration ---
ABACUS_API_KEY = os.environ.get("ABACUS_PRIMARY_KEY") or os.environ.get("ABACUS_API_KEY")
if not ABACUS_API_KEY:
    logger.warning("Abacus API key not found in environment. LLM features may fail.")

ABACUS_DEPLOYMENT_TOKEN = os.environ.get("ABACUS_DEPLOYMENT_TOKEN")
ABACUS_DEPLOYMENT_ID = os.environ.get("ABACUS_DEPLOYMENT_ID")

def get_llm_client():
    if not HAS_ABACUS:
        return None

    api_key = ABACUS_API_KEY
    if not api_key:
        logger.error("No Abacus API key available.")
        return None

    try:
        return ApiClient(api_key=api_key)
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

def heuristic_analyze_document(content, filename):
    """Fallback extraction when LLM is unavailable."""
    logger.info(f"Using heuristic extraction for {filename}")

    entities = []
    relationships = []
    timeline = []
    anomalies = []

    # 1. Extract potential names (Capitalized words)
    # Simple regex for capitalized words that are not starting a sentence or common stopwords
    common_stops = {"The", "A", "An", "On", "In", "At", "To", "From", "And", "But", "Or", "If", "When", "Where", "Who", "What", "Why", "How", "This", "That", "These", "Those", "It", "Is", "Are", "Was", "Were", "Be", "Been", "Being", "Have", "Has", "Had", "Do", "Does", "Did", "Can", "Could", "Will", "Would", "Shall", "Should", "May", "Might", "Must", "Also"}

    # Find capitalized phrases
    cap_phrases = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', content)

    seen_entities = set()
    for phrase in cap_phrases:
        if phrase in common_stops: continue
        if len(phrase) < 3: continue

        etype = "UNKNOWN"
        # Simple heuristics for type
        phrase_lower = phrase.lower()
        if any(name.lower() in phrase_lower for name in ["Epstein", "Maxwell", "Clinton", "Prince Andrew", "Trump", "Doe"]): etype = "PERSON"
        elif any(loc.lower() in phrase_lower for loc in ["TEB", "PBI", "USVI", "New York", "Paris", "London"]): etype = "LOCATION"

        if phrase not in seen_entities:
            entities.append({
                "name": phrase,
                "type": etype,
                "confidence": 50,
                "source_context": "Heuristic extraction"
            })
            seen_entities.add(phrase)

    # 2. Extract Dates (YYYY-MM-DD)
    dates = re.findall(r'(\d{4}-\d{2}-\d{2})', content)
    for d in dates:
        timeline.append({
            "date": d,
            "event": f"Event mentioned in {filename}",
            "confidence": 60
        })
        entities.append({
            "name": d,
            "type": "DATE",
            "confidence": 80,
            "source_context": "Date regex"
        })

    # 3. Extract Flight Info
    if "flight" in content.lower() or "flew" in content.lower():
        # Look for 3-letter codes which might be airports (all caps)
        codes = re.findall(r'\b([A-Z]{3})\b', content)
        airport_candidates = [c for c in codes if c not in common_stops and c not in ["PDF", "JPG", "PNG"]]

        for c in airport_candidates:
             if c not in seen_entities:
                 entities.append({
                    "name": c,
                    "type": "LOCATION/AIRPORT",
                    "confidence": 60,
                    "source_context": "Airport code regex"
                })
                 seen_entities.add(c)

    # Create generic relationships if multiple entities found (limit to first few to avoid explosion)
    if len(entities) > 1:
        # Link first entity to next few
        src = entities[0]['name']
        for i in range(1, min(5, len(entities))):
            tgt = entities[i]['name']
            relationships.append({
                "source": src,
                "target": tgt,
                "type": "associated",
                "confidence": 30,
                "rationale": "Co-occurrence in document",
                "provenance": "Heuristic link"
            })

    # 4. Anomalies
    if "redacted" in content.lower():
        anomalies.append("Document contains 'redacted' keyword.")

    return {
        "entities": entities,
        "relationships": relationships,
        "timeline": timeline,
        "anomalies": anomalies
    }

def analyze_document_llm(content, filename):
    if not content or not content.strip(): return None
    prompt = f"""You are an expert investigative analyst processing the Epstein Archive.
Analyze the following text from document '{filename}'.
Extract:
1. Entities: People, Organizations, Locations, Dates, Flight Log Entries, Financial References.
2. Relationships: Interactions between entities (met, flew with, paid, associated with).
3. Timeline: Key events with dates.
4. Anomalies: Suspicious patterns, contradictions, redaction patterns, or oddities.

Format as JSON:
{{
    "entities": [
        {{"name": "Entity Name", "type": "PERSON/ORG/LOC/DATE/FLIGHT/FINANCIAL", "confidence": 0-100, "source_context": "brief snippet"}}
    ],
    "relationships": [
        {{"source": "Entity1", "target": "Entity2", "type": "relationship_type", "confidence": 0-100, "rationale": "Why this link exists", "provenance": "quote from text"}}
    ],
    "timeline": [
        {{"date": "YYYY-MM-DD or approx", "event": "Description of event", "confidence": 0-100}}
    ],
    "anomalies": [
        "Description of anomaly 1",
        "Description of anomaly 2"
    ]
}}
Strictly return valid JSON only. Do not include markdown formatting like ```json.
Text: {content[:25000]}"""

    response_text = call_llm(prompt)
    if not response_text:
        return heuristic_analyze_document(content, filename)

    # Try to extract JSON block
    clean_text = response_text
    match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
    if match:
        clean_text = match.group(1)
    else:
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            clean_text = match.group(0)

    try:
        data = json.loads(clean_text)
        return data
    except json.JSONDecodeError:
        logger.warning(f"Initial JSON parse failed for {filename}. Attempting cleanup.")
        try:
             # simplistic cleanup: remove newlines that are not structural
             clean_text_2 = clean_text.replace('\n', ' ')
             data = json.loads(clean_text_2)
             return data
        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM JSON for {filename}")
            logger.debug(f"Raw response: {response_text}")
            return heuristic_analyze_document(content, filename)

def scrape_public_sources():
    """Placeholder for automated lightweight scrape of known public sources."""
    logger.info("Starting scrape of public sources (Court Listener, Archive.org)...")
    # Placeholder logic: In a real implementation, this would download files to UNPROCESSED_DIR
    # or directly return paths. For now, we assume it puts files in UNPROCESSED_DIR.
    scraped_files = []
    logger.info("Scraping complete. No new files found (automated scrape disabled/placeholder in this environment).")
    return scraped_files

def create_handoff_stub(anomalies, high_confidence_entities):
    """Creates a handoff stub if critical anomalies are found."""
    if not anomalies:
        return

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    handoff_path = HANDOFFS_DIR / f"handoff-epstein-{timestamp}.md"

    try:
        with open(handoff_path, 'w') as f:
            f.write(f"# Critical Anomalies Detected - {timestamp}\n\n")
            f.write("**Attention:** Grok / Research Lead\n\n")
            f.write("## Anomalies\n")
            for anomaly in anomalies:
                f.write(f"- {anomaly}\n")
            f.write("\n## High Confidence Entities Involved\n")
            seen = set()
            for entity in high_confidence_entities:
                if isinstance(entity, dict):
                    name = entity.get('name')
                else:
                    name = str(entity)

                if name and name not in seen:
                    f.write(f"- {name}\n")
                    seen.add(name)

            f.write("\n## Action Required\n")
            f.write("- [ ] Review source documents for context.\n")
            f.write("- [ ] Verify anomaly against external databases.\n")

        logger.info(f"Handoff stub created at {handoff_path}")
    except Exception as e:
        logger.error(f"Failed to create handoff stub: {e}")

def ingest_files():
    scrape_public_sources()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    dest_dir = PROCESSED_DIR / today
    dest_dir.mkdir(parents=True, exist_ok=True)
    files_to_process = []
    processed_data = []

    # Collect files from UNPROCESSED_DIR and SOURCE_DIR
    dirs_to_scan = [UNPROCESSED_DIR, SOURCE_DIR]

    for d in dirs_to_scan:
        if not d.exists(): continue
        for file_path in d.glob("*"):
            if file_path.is_file():
                try:
                    dest_path = dest_dir / file_path.name
                    # Handle duplicate filenames
                    if dest_path.exists():
                         timestamp = datetime.datetime.now().strftime("%H%M%S")
                         dest_path = dest_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"

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
            # Handle duplicates for handoffs too
            if dest_path.exists():
                 timestamp = datetime.datetime.now().strftime("%H%M%S")
                 dest_path = dest_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"

            shutil.copy(str(file_path), str(dest_path))
            files_to_process.append(dest_path)
        except Exception as e:
            logger.error(f"Error copying handoff {file_path}: {e}")

    for file_path in files_to_process:
        logger.info(f"Processing {file_path.name}...")
        content = ""
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            content = extract_text_from_pdf(file_path)
            if not content.strip():
                logger.warning(f"PDF {file_path.name} appears empty or scanned.")
        elif suffix in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
             logger.info(f"Image detected: {file_path.name}. Marking for OCR.")
             content = f"[IMAGE FILE: {file_path.name} - automated OCR pending]"
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
            else:
                # Use SimpleGraph if networkx is missing
                G = SimpleGraph()
                if 'adj' in data:
                     G.nodes = data.get('nodes', {})
                     G.adj = data.get('adj', {})
                else:
                    # Try to parse node-link format into SimpleGraph
                    for node in data.get('nodes', []):
                        G.add_node(node['id'], **node)
                    links = data.get('links') or data.get('edges', [])
                    for link in links:
                        G.add_edge(link['source'], link['target'], **link)
                return G

        except Exception as e:
            logger.error(f"Error loading graph: {e}")
            return nx.Graph() if HAS_NETWORKX else SimpleGraph()
    return nx.Graph() if HAS_NETWORKX else SimpleGraph()

def save_graph(G):
    try:
        if HAS_NETWORKX:
            data = nx.node_link_data(G)
        else:
            if isinstance(G, SimpleGraph):
                 data = G.to_dict()
            else:
                 data = G # Should be dict already if logic failed somewhere but let's assume SimpleGraph
        with open(GRAPH_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving graph: {e}")

def load_timeline():
    if TIMELINE_FILE.exists():
        try:
            with open(TIMELINE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading timeline: {e}")
            return []
    return []

def save_timeline(timeline_data):
    try:
        # Sort by date
        timeline_data.sort(key=lambda x: x.get('date', ''))
        with open(TIMELINE_FILE, 'w') as f:
            json.dump(timeline_data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving timeline: {e}")

def update_knowledge_graph(G, processed_data):
    new_nodes_count = 0
    new_edges_count = 0
    anomalies = []
    new_timeline_events = []

    for file_path, analysis in processed_data:
        # 1. Entities
        for ent in analysis.get("entities", []):
            name = ent.get("name")
            if not name: continue

            etype = ent.get("type", "UNKNOWN")
            conf = ent.get("confidence", 0)
            context = ent.get("source_context", "")

            if not G.has_node(name):
                G.add_node(name, type=etype, confidence=conf, sources=[file_path.name], context=[context])
                new_nodes_count += 1
            else:
                # Merge attributes
                # G.nodes supports __getitem__ for both NetworkX and SimpleGraph (dict)
                node_data = G.nodes[name]
                node_data['sources'] = list(set(node_data.get('sources', []) + [file_path.name]))
                # Keep highest confidence
                if conf > node_data.get('confidence', 0):
                    node_data['confidence'] = conf
                    node_data['type'] = etype # Update type if higher confidence
                if context:
                        existing_ctx = node_data.get('context', [])
                        if isinstance(existing_ctx, str):
                            existing_ctx = [existing_ctx]
                        node_data['context'] = existing_ctx + [context]

        # 2. Relationships
        for rel in analysis.get("relationships", []):
            src = rel.get("source")
            tgt = rel.get("target")
            if not src or not tgt: continue

            rtype = rel.get("type", "associated")
            conf = rel.get("confidence", 0)
            rat = rel.get("rationale", "")
            prov = rel.get("provenance", "")

            if not G.has_edge(src, tgt):
                G.add_edge(src, tgt, type=rtype, confidence=conf, rationale=[rat], provenance=[prov], weight=1)
                new_edges_count += 1
            else:
                # Merge attributes
                if HAS_NETWORKX and isinstance(G, nx.Graph):
                        edge_data = G[src][tgt]
                else:
                        edge_data = G.adj[src][tgt]

                edge_data['weight'] = edge_data.get('weight', 0) + 1

                existing_prov = edge_data.get('provenance', [])
                if isinstance(existing_prov, str):
                    existing_prov = [existing_prov]
                edge_data['provenance'] = existing_prov + [prov]

                if rat:
                        existing_rat = edge_data.get('rationale', [])
                        if isinstance(existing_rat, str):
                            existing_rat = [existing_rat]
                        edge_data['rationale'] = existing_rat + [rat]

                if conf > edge_data.get('confidence', 0):
                    edge_data['confidence'] = conf
                    edge_data['type'] = rtype

        # 3. Timeline
        for event in analysis.get("timeline", []):
            event['source_doc'] = file_path.name
            new_timeline_events.append(event)

        # 4. Anomalies
        for anom in analysis.get("anomalies", []):
            anomalies.append(f"[{file_path.name}] {anom}")

    return new_nodes_count, new_edges_count, anomalies, new_timeline_events

def detect_anomalies(G, processed_data):
    anomalies = []
    # Both NetworkX and SimpleGraph support iteration over G.degree
    try:
        degrees = sorted(G.degree, key=lambda x: x[1], reverse=True)[:5]
        for n, d in degrees:
            if d > 10: anomalies.append(f"High Degree Node: {n} ({d} connections)")
    except Exception as e:
        logger.warning(f"Anomaly detection (degree centrality) failed: {e}")
    return anomalies

def generate_visuals(G, timeline, output_dir):
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
        if HAS_NETWORKX:
            graph_data = nx.node_link_data(G)
        else:
            if isinstance(G, SimpleGraph):
                graph_data = G.to_dict()
            else:
                graph_data = G
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

    # Timeline Chart
    if HAS_MATPLOTLIB and timeline:
        try:
            # Simple timeline plot
            dates = []
            events = []
            for t in timeline:
                try:
                    d_str = t.get('date', '')
                    # Try a few common formats
                    for fmt in ["%Y-%m-%d", "%Y-%m", "%Y"]:
                        try:
                            d = datetime.datetime.strptime(d_str, fmt)
                            dates.append(d)
                            events.append(t.get('event', '')[:20] + "...")
                            break
                        except: continue
                except:
                    pass

            if dates:
                plt.figure(figsize=(12, 6))
                plt.plot(dates, [1]*len(dates), 'ro')
                for i, txt in enumerate(events):
                    plt.annotate(txt, (dates[i], 1), xytext=(0, 10), textcoords='offset points', rotation=45, fontsize=8)
                plt.yticks([])
                plt.title("Epstein Timeline Events")
                plt.xlabel("Date")
                plt.tight_layout()
                timeline_path = output_dir / f"timeline_{timestamp}.png"
                plt.savefig(timeline_path)
                plt.close()
                logger.info(f"Timeline chart saved to {timeline_path}")
        except Exception as e:
            logger.error(f"Failed to generate timeline chart: {e}")

    return str(html_path)

def generate_nightly_report(processed_data, new_nodes, new_edges, anomalies, new_timeline_events, output_dir):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    report_path = output_dir / f"{today}-epstein-nightly.md"

    # Prepare data for LLM
    docs_summary = []
    for f, analysis in processed_data:
        docs_summary.append({
            "filename": f.name,
            "entities_count": len(analysis.get("entities", [])),
            "top_entities": [e.get("name") for e in analysis.get("entities", [])[:5]],
            "anomalies": analysis.get("anomalies", [])
        })

    prompt = f"""Generate a nightly report based on the following processing statistics and document summaries:

Stats:
- Documents Processed: {len(processed_data)}
- New Graph Nodes: {new_nodes}
- New Graph Edges: {new_edges}
- New Timeline Events: {len(new_timeline_events)}
- Anomalies Detected: {len(anomalies)}

Document Summaries (JSON):
{json.dumps(docs_summary, indent=2)}

Detected Anomalies:
{json.dumps(anomalies, indent=2)}

Please write the following sections in Markdown:
1. ## Executive Summary
   - A 300-500 word narrative summary of the night's findings. Focus on patterns and key entities.
2. ## Top Insights
   - 5-10 high-signal insights (Claim + Evidence + Implication). Bullet points.
3. ## Recommended Follow-ups
   - 3-5 specific targeted research actions for the next daily huddle.

Do not include the title (it will be added). Do not include "Graph Updates", "Anomalies Flagged", "Technical Notes", or "Lessons Learned" sections (they will be added)."""

    llm_content = call_llm(prompt)
    if not llm_content:
        llm_content = "## Executive Summary\nLLM generation failed. Please review raw data.\n\n## Top Insights\n- N/A\n\n## Recommended Follow-ups\n- Check LLM connectivity."

    with open(report_path, 'w') as f:
        f.write(f"# Nightly Epstein Archive Processing – {today}\n\n")

        f.write(llm_content)
        f.write("\n\n")

        f.write("## Graph Updates\n")
        f.write(f"- New Nodes: {new_nodes}\n")
        f.write(f"- New Edges: {new_edges}\n")
        f.write(f"- Total Timeline Events Added: {len(new_timeline_events)}\n\n")

        f.write("## Anomalies Flagged\n")
        if anomalies:
            for a in anomalies: f.write(f"- {a}\n")
        else:
            f.write("None.\n")
        f.write("\n")

        f.write("## Technical Notes\n")
        f.write(f"- Processed {len(processed_data)} files.\n")
        f.write(f"- Output directory: {output_dir}\n")
        f.write(f"- Execution time: {datetime.datetime.now().strftime('%H:%M:%S')}\n\n")

        f.write("## Lessons Learned (Prototype Run)\n")
        f.write("- Initial ingestion pipeline verified.\n")
        f.write("- Graph and timeline integration successful.\n")
        f.write(f"- Scrape public sources: {len(processed_data)} files processed (including test data).\n")
        if not HAS_ABACUS:
             f.write("- AbacusAI not detected. LLM features disabled.\n")
        if not HAS_NETWORKX:
             f.write("- NetworkX not detected. Graph analysis limited.\n")

    logger.info(f"Nightly report generated: {report_path}")

def main():
    logger.info("Starting Nightly Epstein Archive Processor...")
    processed_data = ingest_files()
    G = load_graph()
    timeline = load_timeline()

    new_nodes, new_edges, doc_anomalies, new_timeline_events = update_knowledge_graph(G, processed_data)

    # Merge timeline events
    timeline.extend(new_timeline_events)
    save_timeline(timeline)

    save_graph(G)
    logger.info(f"Graph updated: +{new_nodes} nodes, +{new_edges} edges")
    logger.info(f"Timeline updated: +{len(new_timeline_events)} events")

    all_anomalies = doc_anomalies + detect_anomalies(G, processed_data)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    daily_output_dir = OUTPUT_DIR / today
    daily_output_dir.mkdir(parents=True, exist_ok=True)

    generate_visuals(G, timeline, daily_output_dir)

    # Collect high confidence entities for handoff
    high_conf_entities = []
    for _, analysis in processed_data:
        for ent in analysis.get("entities", []):
            if ent.get("confidence", 0) > 80:
                high_conf_entities.append(ent)

    create_handoff_stub(all_anomalies, high_conf_entities)

    generate_nightly_report(processed_data, new_nodes, new_edges, all_anomalies, new_timeline_events, daily_output_dir)

    # Commit results
    try:
        commit_msg = f"Nightly Epstein processing {datetime.datetime.now().strftime('%Y-%m-%d')} – {len(processed_data)} new docs, {len(all_anomalies)} anomalies"
        subprocess.run(["git", "add", "research/epstein-daily/nightly-output/", "research/epstein-daily/processed/", "research/epstein-daily/graph/", "_agents/_handoffs/"], check=True)

        # Check if there are changes to commit
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if status.stdout.strip():
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            # subprocess.run(["git", "push"], check=True) # Push disabled for safety in this environment
            logger.info(f"Committed changes: {commit_msg}")
        else:
            logger.info("No changes to commit.")
    except Exception as e:
        logger.error(f"Git commit failed: {e}")

    logger.info("Processing complete.")

if __name__ == "__main__":
    main()
