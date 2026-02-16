"""
BPR&D Meeting Service
Custom multi-agent meeting orchestration — no CrewAI, no n8n.
Direct LLM API calls with full conversation transcript for natural dialogue.

Endpoints:
  POST /api/v1/meetings/execute  - Run a meeting
  GET  /api/v1/health            - Health check
  GET  /api/v1/agents            - List agents and status
  GET  /api/v1/cost/monthly      - Current month's spend
  GET  /api/v1/schedule          - View scheduled jobs
"""

import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agents.registry import resolve_participants, load_agents, is_abacus_available
from config import settings
from meetings import MEETING_TYPES
from models.meeting import MeetingRequest, MeetingResponse, MeetingType, CostEstimate
from output.github_writer import commit_meeting_results
from output.notifier import send_meeting_notification
from scheduling.scheduler import create_scheduler, _set_execute_fn
from utils.cost_tracker import CostTracker, load_monthly_spend, save_cost_log

# --- Logging ---
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("bprd-meeting")

# --- Scheduler ---
scheduler = create_scheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    # Startup
    missing = settings.validate()
    if missing:
        logger.warning(f"Missing API keys: {', '.join(missing)}. Some agents may not function.")
    else:
        logger.info("All API keys configured.")

    monthly = load_monthly_spend()
    logger.info(f"Monthly spend: ${monthly:.2f} / ${settings.MONTHLY_BUDGET_CAP:.2f}")

    if monthly >= settings.MONTHLY_BUDGET_ALERT:
        logger.warning(f"Monthly spend ${monthly:.2f} exceeds alert threshold ${settings.MONTHLY_BUDGET_ALERT:.2f}")

    # Wire scheduler to meeting execution
    _set_execute_fn(execute_meeting)
    scheduler.start()
    logger.info("BPR&D Meeting Service started. Scheduler active.")

    yield

    # Shutdown
    scheduler.shutdown(wait=False)
    logger.info("BPR&D Meeting Service stopped.")


# --- App ---
app = FastAPI(
    title="BPR&D Meeting Service",
    description=(
        "Custom multi-agent meeting orchestration for Broad Perspective Research & Development. "
        "Direct LLM API calls with full conversation transcript for natural dialogue."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# --- Meeting Execution ---

async def execute_meeting(request: MeetingRequest) -> MeetingResponse:
    """Execute a meeting. Called by webhook or scheduler."""
    meeting_type_str = request.meeting_type.value
    meeting_id = f"{meeting_type_str}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    logger.info(f"Meeting {meeting_id} requested: type={meeting_type_str}")

    # Budget check
    monthly = load_monthly_spend()
    if monthly >= settings.MONTHLY_BUDGET_CAP:
        logger.error(f"Monthly budget cap reached: ${monthly:.2f}")
        return MeetingResponse(
            success=False,
            meeting_id=meeting_id,
            meeting_type=meeting_type_str,
            notes="",
            error=f"Monthly budget cap ${settings.MONTHLY_BUDGET_CAP:.2f} reached. Current spend: ${monthly:.2f}",
        )

    # Check meeting type is implemented
    meeting_cls = MEETING_TYPES.get(meeting_type_str)
    if not meeting_cls:
        return MeetingResponse(
            success=False,
            meeting_id=meeting_id,
            meeting_type=meeting_type_str,
            notes="",
            error=f"Meeting type '{meeting_type_str}' not yet implemented.",
        )

    # Resolve participants and load agents
    participant_names = resolve_participants(request.participants, meeting_type_str)
    agents = await load_agents(participant_names)

    if not agents:
        return MeetingResponse(
            success=False,
            meeting_id=meeting_id,
            meeting_type=meeting_type_str,
            notes="",
            error="No agents could be loaded.",
        )

    # Create cost tracker
    tracker = CostTracker(meeting_id=meeting_id)

    try:
        # Execute the meeting
        meeting = meeting_cls()
        response = await meeting.execute(
            agents=agents,
            cost_tracker=tracker,
            agenda=request.agenda or "",
        )

        # Save cost log
        save_cost_log(tracker)
        tracker.log_summary()

        # Post-meeting: commit results and notify (fire-and-forget)
        try:
            await commit_meeting_results(response)
        except Exception as e:
            logger.error(f"Failed to commit meeting results: {e}")

        try:
            await send_meeting_notification(response)
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")

        logger.info(f"Meeting {meeting_id} completed successfully")
        return response

    except Exception as e:
        logger.error(f"Meeting {meeting_id} failed: {e}", exc_info=True)
        save_cost_log(tracker)
        return MeetingResponse(
            success=False,
            meeting_id=meeting_id,
            meeting_type=meeting_type_str,
            notes="",
            error=str(e),
            cost_estimate=CostEstimate(**tracker.to_dict()),
        )


@app.post("/api/v1/meetings/execute", response_model=MeetingResponse)
async def execute_meeting_endpoint(request: MeetingRequest) -> MeetingResponse:
    """Execute a BPR&D meeting via HTTP webhook."""
    return await execute_meeting(request)


# --- Health & Status ---

@app.get("/api/v1/health")
async def health_check():
    """Health check for Render deployment monitoring."""
    missing = settings.validate()
    return {
        "status": "healthy" if not missing else "degraded",
        "service": "BPR&D Meeting Service",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENV,
        "missing_keys": missing,
    }


@app.get("/api/v1/agents")
async def list_agents_endpoint():
    """List available agents and their status."""
    abacus_status = "active" if is_abacus_available() else "no_api_key"

    return {
        "agents": {
            "grok": {
                "status": "active" if settings.XAI_API_KEY else "no_api_key",
                "model": "grok-4-1-fast-reasoning",
                "role": "Chief / Manager Agent",
                "faction": "visionaries",
            },
            "claude": {
                "status": "active" if settings.ANTHROPIC_API_KEY else "no_api_key",
                "model": "claude-sonnet-4-5-20250929",
                "role": "Co-Second / Chief Strategist",
                "faction": "visionaries",
            },
            "gemini": {
                "status": "active" if settings.GEMINI_API_KEY else "no_api_key",
                "model": "gemini-3.0-pro-preview",
                "role": "Lead Developer / Research Lead",
                "faction": "truth-seekers",
            },
            "abacus": {
                "status": abacus_status,
                "model": "qwen3-max (via RouteLLM)",
                "role": "Co-Second / Chief Innovator",
                "faction": "truth-seekers",
            },
        },
        "meeting_types": {
            mt.value: "implemented" if mt.value in MEETING_TYPES else "not_implemented"
            for mt in MeetingType
        },
    }


@app.get("/api/v1/cost/monthly")
async def monthly_cost():
    """Get current month's spend and budget status."""
    monthly = load_monthly_spend()
    return {
        "month": datetime.utcnow().strftime("%Y-%m"),
        "spent_usd": round(monthly, 2),
        "budget_cap_usd": settings.MONTHLY_BUDGET_CAP,
        "budget_alert_usd": settings.MONTHLY_BUDGET_ALERT,
        "budget_remaining_usd": round(settings.MONTHLY_BUDGET_CAP - monthly, 2),
        "status": (
            "over_cap" if monthly >= settings.MONTHLY_BUDGET_CAP
            else "alert" if monthly >= settings.MONTHLY_BUDGET_ALERT
            else "ok"
        ),
    }


@app.get("/api/v1/schedule")
async def view_schedule():
    """View scheduled meeting jobs."""
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": str(job.next_run_time) if job.next_run_time else None,
        })
    return {"jobs": jobs}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
