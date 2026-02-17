import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict

app = FastAPI(title="Agent Habitat Proxy")

# Configuration
JULES_URL = os.getenv("JULES_URL", "http://jules-agent:8000")
DEEP_AGENT_URL = os.getenv("DEEP_AGENT_URL", "http://deep-agent:8000")
EPSTEIN_ANALYSIS_URL = os.getenv("EPSTEIN_ANALYSIS_URL", "http://epstein-analysis:8000")

class TaskRequest(BaseModel):
    command: str
    workspace: Optional[str] = None

class EpsteinQuery(BaseModel):
    query: str
    max_results: Optional[int] = 50
    include_timeline: Optional[bool] = True
    model: Optional[str] = None

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "proxy"}

async def forward_request(url: str, method: str, data: Optional[Dict] = None):
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url)
            elif method == "POST":
                response = await client.post(url, json=data)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")

            # Forward status code if not 200
            if response.status_code >= 400:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Service unreachable: {str(e)}")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/jules/task")
async def jules_task(task: TaskRequest):
    return await forward_request(f"{JULES_URL}/task", "POST", task.dict())

@app.get("/agents/jules/logs")
async def jules_logs(lines: int = 100):
    return await forward_request(f"{JULES_URL}/logs?lines={lines}", "GET")

@app.post("/agents/deepagent/task")
async def deep_agent_task(task: TaskRequest):
    return await forward_request(f"{DEEP_AGENT_URL}/task", "POST", task.dict())

@app.get("/agents/deepagent/logs")
async def deep_agent_logs(lines: int = 100):
    return await forward_request(f"{DEEP_AGENT_URL}/logs?lines={lines}", "GET")

@app.post("/agents/analysis/epstein")
async def epstein_analysis(query: EpsteinQuery):
    return await forward_request(f"{EPSTEIN_ANALYSIS_URL}/query", "POST", query.dict())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
