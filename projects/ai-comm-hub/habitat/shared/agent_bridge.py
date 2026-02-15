import os
import logging
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import libtmux
from typing import Optional

# Configuration
TMUX_SESSION_NAME = "agent"
API_PORT = 8000

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent-bridge")

app = FastAPI(title="Agent Bridge")

def get_server():
    server = libtmux.Server()
    return server

def get_session(server):
    try:
        session = server.find_where({"session_name": TMUX_SESSION_NAME})
        if not session:
            session = server.new_session(session_name=TMUX_SESSION_NAME)
            logger.info(f"Created new tmux session: {TMUX_SESSION_NAME}")
        return session
    except Exception as e:
        logger.error(f"Error getting/creating session: {e}")
        # Fallback: try to create if finding failed (sometimes happens on fresh server)
        return server.new_session(session_name=TMUX_SESSION_NAME)

def get_pane():
    server = get_server()
    session = get_session(server)
    window = session.windows[0]
    pane = window.panes[0]
    return pane

class TaskRequest(BaseModel):
    command: str
    workspace: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Ensure tmux session exists on startup"""
    try:
        pane = get_pane()
        logger.info(f"Connected to tmux session: {TMUX_SESSION_NAME}")
    except Exception as e:
        logger.error(f"Failed to initialize tmux session: {e}")

@app.get("/health")
def health_check():
    return {"status": "ok", "agent": os.environ.get("AGENT_NAME", "unknown")}

@app.post("/task")
def execute_task(task: TaskRequest):
    try:
        pane = get_pane()

        if task.workspace:
            # Check if directory exists first? No, just try to cd.
            logger.info(f"Changing workspace to: {task.workspace}")
            pane.send_keys(f"cd {task.workspace}")

        logger.info(f"Sending command: {task.command}")
        pane.send_keys(task.command)

        return {"status": "success", "message": "Command sent to terminal"}
    except Exception as e:
        logger.error(f"Task execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs")
def get_logs(lines: int = 100):
    try:
        pane = get_pane()
        # capture_pane returns a list of lines
        output = pane.capture_pane(start=-lines)
        return {"logs": output}
    except Exception as e:
        logger.error(f"Failed to fetch logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Start tmux server if not running (libtmux attaches, but we need the process)
    # Actually, libtmux connects to the socket. We usually need 'tmux start-server' or just 'new-session'.
    # We will rely on the startup_event or the container's entrypoint to ensure tmux is ready.
    # But get_session handles creation.

    uvicorn.run(app, host="0.0.0.0", port=API_PORT)
