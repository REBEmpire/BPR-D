import asyncio
import logging
from datetime import datetime
import os

from agents.registry import RegisteredAgent
from meetings.base import BaseMeeting
from models.meeting import MeetingResponse, CostEstimate
from orchestrator.transcript import Transcript
from output.github_writer import commit_meeting_results
from output.notifier import send_meeting_notification
from tools.github_tool import read_file
from utils.cost_tracker import CostTracker

logger = logging.getLogger(__name__)

class SpecialSession(BaseMeeting):
    meeting_type = "special_session"

    async def execute(
        self,
        agents: dict[str, RegisteredAgent],
        cost_tracker: CostTracker,
        agenda: str = "",
    ) -> MeetingResponse:
        meeting_id = f"special-session-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        cost_tracker.meeting_id = meeting_id
        transcript = Transcript()

        # Extract topic from agenda (it's passed as agenda by main.py manual-trigger)
        topic = agenda.replace("**⚡ HiC Goal:** ", "").split("\n")[0] if agenda else "General Topic"

        logger.info(f"Executing Special Session: {meeting_id} on '{topic}'")

        # --- Phase 1: Topic Intake + Research Pull ---
        logger.info("Phase 1: Topic Intake + Research Pull")

        # Pull context from knowledge_system (and research as fallback)
        research_summary = "No specific research briefs found."
        try:
            # List files in knowledge_system to find relevant ones (naive approach: just list top level)
            ks_files = []
            if os.path.exists("knowledge_system"):
                 ks_files = os.listdir("knowledge_system")

            research_files = []
            if os.path.exists("research"):
                 research_files = os.listdir("research")

            context_msg = f"Available files in knowledge_system: {ks_files}\nAvailable files in research: {research_files}"

            # Use Grok to analyze topic and context
            grok = agents.get("grok")
            if grok:
                sys_prompt = (
                    "You are Grok, leading a Special Session.\n"
                    f"Topic: {topic}\n"
                    f"Context: {context_msg}\n"
                    "Step 1: Analyze the topic and available research. "
                    "Define the scope, key questions, and which agents should focus on what. "
                    "Be concise and directive."
                )

                resp = await grok.provider.chat(
                    messages=[{"role": "user", "content": "Start the session."}],
                    system=sys_prompt,
                    temperature=0.3
                )
                transcript.add_turn("grok", "intake", resp.content)
                cost_tracker.record_usage("grok", resp.input_tokens, resp.output_tokens, resp.cost_usd)
        except Exception as e:
            logger.error(f"Phase 1 failed: {e}")
            transcript.add_turn("system", "error", f"Phase 1 error: {e}")

        # --- Phase 2: Agent Round Robin ---
        logger.info("Phase 2: Agent Round Robin")
        participant_order = ["claude", "gemini", "abacus"]

        for agent_name in participant_order:
            agent = agents.get(agent_name)
            if not agent:
                continue

            prev_context = transcript.to_string()

            sys_prompt = (
                f"You are {agent_name.title()}.\n"
                f"Topic: {topic}\n"
                "Review the discussion so far.\n"
                "Provide your specific expertise, input, and analysis on this topic.\n"
                "Be constructive, technical, and precise."
            )

            try:
                resp = await agent.provider.chat(
                    messages=[{"role": "user", "content": f"Context:\n{prev_context}\n\nYour turn."}],
                    system=sys_prompt,
                    temperature=0.4
                )
                transcript.add_turn(agent_name, "input", resp.content)
                cost_tracker.record_usage(agent_name, resp.input_tokens, resp.output_tokens, resp.cost_usd)
            except Exception as e:
                logger.error(f"Phase 2 ({agent_name}) failed: {e}")

        # --- Phase 3: Synthesis ---
        logger.info("Phase 3: Synthesis")
        if grok:
            prev_context = transcript.to_string()
            sys_prompt = (
                "You are Grok. Synthesize the team's input.\n"
                "Highlight key insights, agreements, and conflicts.\n"
                "Prepare for the work plan phase."
            )
            try:
                resp = await grok.provider.chat(
                    messages=[{"role": "user", "content": f"Context:\n{prev_context}\n\nSynthesize."}],
                    system=sys_prompt,
                    temperature=0.3
                )
                transcript.add_turn("grok", "synthesis", resp.content)
                cost_tracker.record_usage("grok", resp.input_tokens, resp.output_tokens, resp.cost_usd)
            except Exception as e:
                logger.error(f"Phase 3 failed: {e}")

        # --- Phase 4: Work Plan ---
        logger.info("Phase 4: Work Plan")
        # Claude or Gemini does this usually. Let's ask Claude if available, else Gemini.
        planner = agents.get("claude") or agents.get("gemini")
        if planner:
            prev_context = transcript.to_string()
            sys_prompt = (
                f"You are {planner.persona.name}.\n"
                "Create a detailed Work Plan and Specifications based on the synthesis.\n"
                "Include:\n"
                "- Objectives\n"
                "- Step-by-step Plan\n"
                "- Code/Technical Specs (if applicable)\n"
                "- Action Items"
            )
            try:
                resp = await planner.provider.chat(
                    messages=[{"role": "user", "content": f"Context:\n{prev_context}\n\nGenerate Work Plan."}],
                    system=sys_prompt,
                    temperature=0.3
                )
                transcript.add_turn(planner.persona.name.lower(), "work_plan", resp.content)
                cost_tracker.record_usage(planner.persona.name.lower(), resp.input_tokens, resp.output_tokens, resp.cost_usd)
            except Exception as e:
                logger.error(f"Phase 4 failed: {e}")

        # --- Phase 5: Final Deliverable & Commit Prep ---
        logger.info("Phase 5: Final Deliverable")
        # Grok wraps it up for the commit message/notes
        final_summary = ""
        if grok:
            prev_context = transcript.to_string()
            sys_prompt = (
                "You are Grok. Finalize this session.\n"
                "Summarize the outcome for the final report.\n"
                "Ensure it's ready for immediate execution."
            )
            try:
                resp = await grok.provider.chat(
                    messages=[{"role": "user", "content": f"Context:\n{prev_context}\n\nFinalize."}],
                    system=sys_prompt,
                    temperature=0.3
                )
                transcript.add_turn("grok", "closing", resp.content)
                cost_tracker.record_usage("grok", resp.input_tokens, resp.output_tokens, resp.cost_usd)
                final_summary = resp.content
            except Exception as e:
                logger.error(f"Phase 5 failed: {e}")

        # Construct Notes
        notes = f"# Special Session: {topic}\n"
        notes += f"**Date:** {datetime.utcnow().strftime('%Y-%m-%d')}\n"
        notes += f"**Triggered By:** HiC (Russell)\n\n"
        notes += transcript.to_markdown()

        return MeetingResponse(
            success=True,
            meeting_id=meeting_id,
            meeting_type=self.meeting_type,
            notes=notes,
            summary=final_summary,
            cost_estimate=CostEstimate(**cost_tracker.to_dict()),
            # Parse action items/handoffs if possible, or leave empty for now
            action_items=[],
            handoffs=[]
        )
