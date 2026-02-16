import os
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
from datetime import datetime

# --- Configuration ---
DATA_PATH = os.getenv("DATA_PATH", "/app/data")
PERSISTENCE_MODE = os.getenv("PERSISTENCE_MODE", "ephemeral")
MODEL = os.getenv("MODEL", "proxy")
USE_HABITAT_PROXY = os.getenv("USE_HABITAT_PROXY", "true").lower() == "true"

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("epstein-analysis")

app = FastAPI(
    title="Epstein Document Analysis Service",
    description="Privacy-first, in-memory analysis service for the Epstein dataset.",
    version="0.1.0-alpha",
)

# --- Models ---

class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query for the dataset")
    max_results: int = Field(50, description="Maximum number of entities/results to return")
    include_timeline: bool = Field(True, description="Whether to include a timeline of events")
    model: Optional[str] = Field(None, description="Specific model to use (overrides env var)")

class Entity(BaseModel):
    name: str
    type: str
    confidence: float
    context: str

class TimelineEvent(BaseModel):
    date: str
    description: str
    source_doc: str

class AnalysisResponse(BaseModel):
    status: str
    model_used: str
    query_echo: str
    entities: List[Entity]
    timeline: List[TimelineEvent]
    network_snippet: dict
    confidence_score: float
    timestamp: str

# --- Endpoints ---

@app.get("/health")
async def health_check():
    """
    Returns the operational status of the service and dataset availability.
    """
    dataset_status = "mounted" if os.path.exists(DATA_PATH) and os.listdir(DATA_PATH) else "empty_or_missing"

    return {
        "status": "online",
        "service": "epstein-analysis",
        "dataset_path": DATA_PATH,
        "dataset_status": dataset_status,
        "active_model": MODEL,
        "persistence_mode": PERSISTENCE_MODE,
        "meme": "The files are in the computer? *zoolander_face*"
    }

@app.post("/query", response_model=AnalysisResponse)
async def query_dataset(request: QueryRequest = Body(...)):
    """
    Accepts a natural language query and performs analysis on the Epstein dataset.
    Currently returns a rich mock response while the core engine is being integrated.
    """
    active_model = request.model or MODEL
    logger.info(f"Received query: '{request.query}' using model: {active_model}")

    # TODO: PLUG IN REAL ANALYSIS LOGIC HERE
    # from core.analysis import run_query
    # result = run_query(request.query, ...)

    # Mock Response Logic
    mock_entities = []
    mock_timeline = []

    if "ghislaine" in request.query.lower():
        mock_entities.append(Entity(name="Ghislaine Maxwell", type="Person", confidence=0.99, context="Flight Log 2016-03-12"))
        mock_entities.append(Entity(name="TerraMar Project", type="Organization", confidence=0.95, context="Funding Document A"))
        mock_timeline.append(TimelineEvent(date="2016-03-12", description="Flight executed from NY to Palm Beach", source_doc="flight_log_2016.pdf"))

    mock_entities.append(Entity(name="Mock Entity A", type="Person", confidence=0.85, context="Redacted Document #4"))

    return AnalysisResponse(
        status="analysis_complete (mock)",
        model_used=active_model,
        query_echo=request.query,
        entities=mock_entities,
        timeline=mock_timeline,
        network_snippet={"nodes": [{"id": "Ghislaine"}, {"id": "Epstein"}], "edges": [{"source": "Ghislaine", "target": "Epstein", "label": "Associate"}]},
        confidence_score=0.92,
        timestamp=datetime.utcnow().isoformat()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
