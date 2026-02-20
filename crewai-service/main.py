"""
BPR&D Meeting Service
Custom multi-agent meeting orchestration — no CrewAI, no n8n.
Direct LLM API calls with full conversation transcript for natural dialogue.

Endpoints:
  POST /api/v1/meetings/execute         - Run a meeting (structured)
  POST /api/v1/meetings/manual-trigger  - HiC one-command team meeting trigger (X-API-KEY auth)
  POST /api/v1/ignite-the-forge         - Ignite the Alchemical Forge (HiC-only)
  GET  /api/v1/health                   - Health check
  GET  /api/v1/agents                   - List agents and status
  GET  /api/v1/cost/monthly             - Current month's spend
  GET  /api/v1/schedule                 - View scheduled jobs
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agents.registry import resolve_participants, load_agents, is_abacus_available
from config import settings
from meetings import MEETING_TYPES
from prompts.nervous_system_injector import NervousSystemInjector
from models.meeting import MeetingRequest, MeetingResponse, MeetingType, CostEstimate
from output.github_writer import commit_meeting_results
from output.notifier import send_meeting_notification
from scheduling.scheduler import create_scheduler, _set_execute_fn
from utils.cost_tracker import CostTracker, load_monthly_spend, save_cost_log, get_monthly_cost_breakdown

# --- Logging ---
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("bprd-meeting")

# --- Scheduler ---
scheduler = create_scheduler()

# --- Background meeting tracking ---
_running_meetings: dict[str, asyncio.Task] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    # Startup: Check API Keys
    critical_missing = []
    if not settings.XAI_API_KEY:
        critical_missing.append("XAI_API_KEY (Grok)")
    if not settings.GITHUB_TOKEN:
        critical_missing.append("GITHUB_TOKEN")

    optional_missing = []
    if not settings.ANTHROPIC_API_KEY:
        optional_missing.append("ANTHROPIC_API_KEY (Claude)")
    if not settings.GEMINI_API_KEY:
        optional_missing.append("GEMINI_API_KEY (Gemini)")
    if not is_abacus_available():
        optional_missing.append("ABACUS_API_KEY (Abacus)")

    if critical_missing:
        logger.critical(f"CRITICAL: Missing required keys: {', '.join(critical_missing)}. Service may fail.")

    if optional_missing:
        logger.warning(f"Optional keys missing: {', '.join(optional_missing)}. Corresponding agents will be unavailable.")

    if not critical_missing and not optional_missing:
        logger.info("All API keys configured and agents ready.")

    monthly = load_monthly_spend()
    logger.info(f"Monthly spend: ${monthly:.2f} / ${settings.MONTHLY_BUDGET_CAP:.2f}")

    if monthly >= settings.MONTHLY_BUDGET_ALERT:
        logger.warning(f"Monthly spend ${monthly:.2f} exceeds alert threshold ${settings.MONTHLY_BUDGET_ALERT:.2f}")

    # Wire scheduler to meeting execution
    _set_execute_fn(execute_meeting)
    scheduler.start()
    logger.info("BPR&D Meeting Service started. Scheduler active.")

    # Probe the skill graph at startup and log node count
    try:
        _ns = NervousSystemInjector()
        await _ns.load()
        logger.info(
            "Nervous system nodes loaded: %d | Graph: _shared/skill-graphs/bprd-core/",
            _ns.node_count,
        )
    except Exception as _ns_err:
        logger.warning("Nervous system startup probe failed: %s", _ns_err)

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

    # Filter out agents with missing keys dynamically
    available_participants = []
    for name in participant_names:
        if name == "grok" and not settings.XAI_API_KEY:
            logger.error("Grok requested but XAI_API_KEY missing.")
            continue
        if name == "claude" and not settings.ANTHROPIC_API_KEY:
            logger.warning("Claude requested but ANTHROPIC_API_KEY missing. Skipping.")
            continue
        if name == "gemini" and not settings.GEMINI_API_KEY:
            logger.warning("Gemini requested but GEMINI_API_KEY missing. Skipping.")
            continue
        if name == "abacus" and not is_abacus_available():
            logger.warning("Abacus requested but API key missing. Skipping.")
            continue
        available_participants.append(name)

    if not available_participants:
        return MeetingResponse(
            success=False,
            meeting_id=meeting_id,
            meeting_type=meeting_type_str,
            notes="",
            error="No available agents (check API keys).",
        )

    agents = await load_agents(available_participants)

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
            commit_ok, notes_path = await commit_meeting_results(response)
            if commit_ok and notes_path:
                response.session_path = notes_path
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


@app.post("/api/v1/meetings/manual-trigger")
async def manual_team_meeting_trigger(
    payload: dict,
    x_api_key: str = Header(default="", alias="X-API-KEY"),
) -> dict:
    """
    HiC one-command trigger for team meetings.

    Requires X-API-KEY header matching BPRD_API_KEY env var.

    Body fields:
        meeting_type   (str)  — default "team_meeting"
        participants   (list) — default all four agents
        goal           (str)  — short goal description (used as agenda)
        custom_prompt  (str)  — optional override for the full agenda prompt

    Returns:
        status, meeting_id, report_url (GitHub path where notes are committed)

    Example:
        curl -X POST https://bprd-meetings.onrender.com/api/v1/meetings/manual-trigger \\
          -H "Content-Type: application/json" \\
          -H "X-API-KEY: $BPRD_API_KEY" \\
          -d '{"goal": "Implement hybrid semantic search in discovery.py",
               "participants": ["grok", "claude", "gemini"]}'
    """
    # --- Auth ---
    if not settings.BPRD_API_KEY:
        logger.warning("BPRD_API_KEY not set — manual-trigger endpoint is OPEN. Set it in Render env vars.")
    elif x_api_key != settings.BPRD_API_KEY:
        logger.warning("manual-trigger: rejected request with invalid X-API-KEY")
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-KEY header.")

    # --- Parse payload ---
    meeting_type = payload.get("meeting_type", "daily_briefing")
    participants = payload.get("participants", ["grok", "claude", "gemini", "abacus"])
    goal = payload.get("goal", "")
    custom_prompt = payload.get("custom_prompt", "")

    # Build a rich agenda: custom_prompt wins; fall back to structured goal block
    if custom_prompt:
        agenda = custom_prompt
    elif goal:
        agenda = (
            f"**⚡ HiC Goal:** {goal}\n\n"
            "Complete this as a full collaborative team session with real dialogue. "
            "Produce concrete deliverables, commit all file changes to GitHub, "
            "and update handoffs before closing."
        )
    else:
        agenda = "Full team sync — review backlog and drive top priorities to completion."

    logger.info(
        "manual-trigger: meeting_type=%s participants=%s goal=%r",
        meeting_type, participants, goal[:80] if goal else "",
    )

    # --- Build MeetingRequest and reuse execute_meeting ---
    try:
        meeting_type_enum = MeetingType(meeting_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown meeting_type '{meeting_type}'. Valid: {[mt.value for mt in MeetingType]}",
        )

    request = MeetingRequest(
        meeting_type=meeting_type_enum,
        participants=participants,
        agenda=agenda,
    )

    # Fire-and-forget: launch meeting in background so the HTTP response
    # returns immediately. Render Starter plan kills requests after 30s,
    # but Daily Briefings take 2-5 minutes. The background task runs to
    # completion on the same asyncio event loop that APScheduler uses.
    meeting_id = f"{meeting_type}-manual-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

    task = asyncio.create_task(execute_meeting(request))
    _running_meetings[meeting_id] = task

    def _cleanup(t: asyncio.Task) -> None:
        _running_meetings.pop(meeting_id, None)
        if t.exception():
            logger.error(f"Background meeting {meeting_id} failed: {t.exception()}")
        else:
            logger.info(f"Background meeting {meeting_id} completed successfully")

    task.add_done_callback(_cleanup)

    sessions_url = f"https://github.com/{settings.GITHUB_REPO}/tree/main/meetings/logs"

    return {
        "status": "triggered",
        "meeting_id": meeting_id,
        "meeting_type": meeting_type,
        "participants": participants,
        "goal": goal,
        "report_url": sessions_url,
        "message": "Meeting launched in background. Session notes will appear in GitHub within 2-5 minutes.",
    }


# --- Health & Status ---

@app.get("/api/v1/health")
async def health_check():
    """Health check for Render deployment monitoring."""
    # Custom health check logic based on key availability
    status = "healthy"
    missing = []

    if not settings.XAI_API_KEY or not settings.GITHUB_TOKEN:
        status = "degraded"
        missing.append("critical_keys")

    return {
        "status": status,
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
                "model": "gemini-3-pro-preview",
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
    breakdown = get_monthly_cost_breakdown()
    monthly = breakdown["total"]

    return {
        "month": datetime.utcnow().strftime("%Y-%m"),
        "spent_usd": round(monthly, 2),
        "budget_cap_usd": settings.MONTHLY_BUDGET_CAP,
        "budget_alert_usd": settings.MONTHLY_BUDGET_ALERT,
        "budget_remaining_usd": round(settings.MONTHLY_BUDGET_CAP - monthly, 2),
        "breakdown": breakdown["by_agent"],
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



@app.post("/api/v1/trigger-special-session")
async def trigger_special_session(
    payload: dict,
    x_api_key: str = Header(default="", alias="X-API-KEY"),
) -> dict:
    """
    Trigger a Special Session (4-5 turn workflow) from the dashboard button.
    """
    # 1. Auth
    if not settings.BPRD_API_KEY:
        logger.warning("BPRD_API_KEY not set!")
    elif x_api_key != settings.BPRD_API_KEY:
        logger.warning("trigger-special-session: rejected request with invalid X-API-KEY")
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-KEY header.")

    # 2. Validate payload
    topic = payload.get("topic")
    hic_id = payload.get("hic_id", "russell")
    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")

    logger.info(f"Triggering Special Session for topic: {topic}")

    # 3. Create GitHub Issue
    issue_title = f"Special Session Request: {topic}"
    issue_body = f"""Triggered by {hic_id} via Dashboard.
Topic: {topic}
Status: In Progress"""
    try:
        issue_num = await create_issue(issue_title, issue_body, labels=["special-session"])
        if issue_num:
            logger.info(f"Created issue #{issue_num} for special session")
        else:
            logger.warning("Failed to create GitHub issue for special session")
            issue_num = "N/A"
    except Exception as e:
        logger.error(f"Error creating issue: {e}")
        issue_num = "Error"

    # 4. Launch Workflow (Background Task)
    request = MeetingRequest(
        meeting_type=MeetingType.SPECIAL_SESSION,
        participants=["grok", "claude", "gemini", "abacus"],
        agenda=f"""**⚡ HiC Goal:** {topic}

GitHub Issue: #{issue_num}"""
    )

    meeting_id = f"special-session-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

    # We define the task logic here or reuse execute_meeting
    # execute_meeting is async, so create_task is correct.
    task = asyncio.create_task(execute_meeting(request))
    _running_meetings[meeting_id] = task

    def _cleanup(t):
        _running_meetings.pop(meeting_id, None)
        if t.exception():
            logger.error(f"Special session {meeting_id} failed: {t.exception()}")
        else:
            logger.info(f"Special session {meeting_id} completed successfully")

    task.add_done_callback(_cleanup)

    return {
        "status": "triggered",
        "meeting_id": meeting_id,
        "issue_number": issue_num,
        "message": f"Special Session '{topic}' initiated. Check GitHub/Telegram."
    }
# --- Alchemical Forge ---

@app.post("/api/v1/ignite-the-forge")
async def ignite_the_forge(
    payload: dict = None,
    x_api_key: str = Header(default="", alias="X-API-KEY"),
) -> dict:
    """
    Ignite the Alchemical Forge — HiC-only endpoint.

    Flips AETHERIAL_FORGE_ENABLED and runs one transmutation cycle.
    Requires X-API-KEY header matching BPRD_API_KEY env var.

    Body fields:
        dry_run (bool) — If true, run in dry-run mode (default: false)
        turns (int) — Number of expansion turns (default: 4, max: 6)

    Returns:
        status, forge_run_id, elixir_path, grade

    Example:
        curl -X POST https://bprd-meetings.onrender.com/api/v1/ignite-the-forge \\
          -H "Content-Type: application/json" \\
          -H "X-API-KEY: $BPRD_API_KEY" \\
          -d '{"dry_run": false}'
    """
    # --- Auth ---
    if not settings.BPRD_API_KEY:
        logger.warning("BPRD_API_KEY not set — ignite-the-forge endpoint is OPEN.")
    elif x_api_key != settings.BPRD_API_KEY:
        logger.warning("ignite-the-forge: rejected request with invalid X-API-KEY")
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-KEY header.")

    payload = payload or {}
    dry_run = payload.get("dry_run", False)
    turns = min(max(payload.get("turns", 4), 1), 6)

    forge_run_id = f"forge-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    logger.info(f"Igniting the Alchemical Forge: {forge_run_id} (dry_run={dry_run}, turns={turns})")

    # Enable the forge
    os.environ["AETHERIAL_FORGE_ENABLED"] = "true"

    try:
        # Import and run the forge
        from pipelines.alchemical_forge.elixir_expansion_chamber import run_forge
        result = await run_forge(
            dry_run=dry_run,
            use_latest_brief=True,
            turns=turns,
        )

        return {
            "status": "completed" if result["success"] else "failed",
            "forge_run_id": forge_run_id,
            "dry_run": dry_run,
            "elixir_path": result.get("elixir_path"),
            "grade": result.get("grade"),
            "image_paths": result.get("image_paths", []),
            "errors": result.get("errors", []),
            "message": "The Great Work continues." if result["success"] else "Transmutation failed.",
        }

    except Exception as e:
        logger.error(f"Forge ignition failed: {e}", exc_info=True)
        return {
            "status": "error",
            "forge_run_id": forge_run_id,
            "error": str(e),
            "message": "The Forge could not be ignited.",
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
