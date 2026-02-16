"""
BPR&D CrewAI Service
FastAPI webhook server that n8n calls to execute multi-agent meetings.

Endpoints:
  POST /api/v1/meetings/execute  - Run a meeting crew
  GET  /api/v1/health            - Health check for Render/n8n monitoring
  GET  /api/v1/agents            - List agents and their status
  GET  /api/v1/cost/monthly      - Current month's spend
"""

import logging
import sys
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from models.meeting import MeetingRequest, MeetingResponse, MeetingType, CostEstimate
from crews.daily_briefing import create_daily_briefing_crew, parse_crew_output
from utils.cost_tracker import CostTracker, load_monthly_spend, save_cost_log

# --- Logging ---
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("bprd-crewai")

# --- App ---
app = FastAPI(
    title="BPR&D CrewAI Service",
    description=(
        "Multi-agent meeting orchestration for Broad Perspective Research & Development. "
        "Provides hierarchical CrewAI crews triggered by n8n webhooks."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # n8n needs to reach this from any origin
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_checks():
    """Validate configuration on startup."""
    missing = settings.validate()
    if missing:
        logger.warning(f"Missing API keys: {', '.join(missing)}. Some agents may not function.")
    else:
        logger.info("All API keys configured.")

    monthly = load_monthly_spend()
    logger.info(f"Monthly spend so far: ${monthly:.2f} / ${settings.MONTHLY_BUDGET_CAP:.2f}")

    if monthly >= settings.MONTHLY_BUDGET_ALERT:
        logger.warning(
            f"Monthly spend ${monthly:.2f} exceeds alert threshold "
            f"${settings.MONTHLY_BUDGET_ALERT:.2f}"
        )

    logger.info("BPR&D CrewAI Service started.")


# --- Meeting Execution ---

@app.post("/api/v1/meetings/execute", response_model=MeetingResponse)
async def execute_meeting(request: MeetingRequest) -> MeetingResponse:
    """
    Execute a BPR&D meeting via CrewAI hierarchical process.
    Called by n8n workflow via HTTP POST webhook.

    Returns structured meeting output: notes, handoffs, action items, decisions.
    """
    meeting_id = f"{request.meeting_type.value}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    logger.info(f"Meeting {meeting_id} requested: type={request.meeting_type.value}")

    # Budget check
    monthly = load_monthly_spend()
    if monthly >= settings.MONTHLY_BUDGET_CAP:
        logger.error(f"Monthly budget cap reached: ${monthly:.2f}")
        return MeetingResponse(
            success=False,
            meeting_id=meeting_id,
            meeting_type=request.meeting_type.value,
            notes="",
            error=f"Monthly budget cap ${settings.MONTHLY_BUDGET_CAP:.2f} reached. Current spend: ${monthly:.2f}",
        )

    # Cost tracker
    tracker = CostTracker(meeting_id=meeting_id)

    try:
        # Select and create crew
        if request.meeting_type == MeetingType.DAILY_BRIEFING:
            crew, metadata = create_daily_briefing_crew(
                agenda=request.agenda,
                include_abacus=_should_include_abacus(request.participants),
            )
        elif request.meeting_type in (MeetingType.PROJECT_SYNC, MeetingType.RETROSPECTIVE):
            # Phase 2 - not yet implemented
            return MeetingResponse(
                success=False,
                meeting_id=meeting_id,
                meeting_type=request.meeting_type.value,
                notes="",
                error=f"Meeting type '{request.meeting_type.value}' not yet implemented (Phase 2).",
            )
        elif request.meeting_type == MeetingType.AD_HOC:
            # Phase 3 - not yet implemented
            return MeetingResponse(
                success=False,
                meeting_id=meeting_id,
                meeting_type=request.meeting_type.value,
                notes="",
                error="Ad-hoc meetings not yet implemented (Phase 3).",
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown meeting type: {request.meeting_type}",
            )

        logger.info(f"Crew created: {metadata}")

        # Execute crew
        logger.info(f"Starting crew execution for {meeting_id}...")
        result = crew.kickoff()
        logger.info(f"Crew execution completed for {meeting_id}")

        # Parse output
        raw_output = result.raw if hasattr(result, "raw") else str(result)
        response = parse_crew_output(raw_output, meeting_id)

        # Attach cost estimate
        # Note: Detailed token tracking requires CrewAI callbacks (Phase 2 enhancement).
        # For now, we log execution time and estimate based on output length.
        response.cost_estimate = CostEstimate(
            execution_time_seconds=round(tracker.execution_time, 1),
            cost_usd=round(tracker.total_cost, 4),
            by_agent={k: round(v.cost_usd, 4) for k, v in tracker.agent_usage.items()},
            terminated_early=tracker.terminated_early,
            termination_reason=tracker.termination_reason,
        )

        # Save cost log
        save_cost_log(tracker)
        tracker.log_summary()

        logger.info(f"Meeting {meeting_id} completed successfully")
        return response

    except Exception as e:
        logger.error(f"Meeting {meeting_id} failed: {e}", exc_info=True)
        return MeetingResponse(
            success=False,
            meeting_id=meeting_id,
            meeting_type=request.meeting_type.value,
            notes="",
            error=str(e),
        )


# --- Health & Status ---

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint for Render deployment and n8n monitoring."""
    missing = settings.validate()
    return {
        "status": "healthy" if not missing else "degraded",
        "service": "BPR&D CrewAI",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENV,
        "missing_keys": missing,
    }


@app.get("/api/v1/agents")
async def list_agents():
    """List available agents and their status."""
    # Determine Abacus availability
    abacus_status = "paused_until_2026-02-23"
    try:
        if datetime.utcnow() >= datetime(2026, 2, 23):
            abacus_status = "active" if settings.ABACUS_PRIMARY_KEY else "no_api_key"
    except Exception:
        pass

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
                "model": "claude-sonnet-4-5",
                "role": "Co-Second / Chief Strategist",
                "faction": "visionaries",
            },
            "gemini": {
                "status": "active" if settings.GEMINI_API_KEY else "no_api_key",
                "model": "gemini-3-0-pro-preview",
                "role": "Lead Developer / Compliance Automator",
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
            "daily_briefing": "implemented",
            "project_sync": "phase_2",
            "retrospective": "phase_2",
            "ad_hoc": "phase_3",
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


# --- Helpers ---

def _should_include_abacus(participants: list[str] | None) -> bool:
    """Determine if Abacus should be included in the crew."""
    if participants and "abacus" in participants:
        return True

    # Auto-include after Feb 23, 2026
    try:
        if datetime.utcnow() >= datetime(2026, 2, 23) and settings.ABACUS_PRIMARY_KEY:
            return True
    except Exception:
        pass

    return False


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
