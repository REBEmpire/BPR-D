# BPR&D Post-Reorg File Structure
> Generated: Feb 20, 2026 | Branch: repo-cleanup

```
.
├── .bprd/
│   └── agents.yaml
├── .claude/
│   ├── agents/
│   │   └── Claude Code.agent.md
│   └── settings.json
├── .devcontainer/
│   ├── Dockerfile
│   ├── devcontainer.json
│   └── scripts/
│       └── (setup-*.sh scripts)
├── .github/
│   ├── agents/
│   │   ├── Gemini.agent.md
│   │   └── Grok-Code-Fast_1.agent.md
│   └── workflows/
│       ├── hive-pipeline.yml
│       ├── meeting-automator.yml
│       └── pr-agent.yml
├── _agents/
│   ├── PRE-LAUNCH-CHECKLIST.md
│   ├── _archive/
│   │   ├── README.md
│   │   ├── abacus-client.py
│   │   ├── abacus-integration.md
│   │   ├── automations/grok-daily-work/
│   │   ├── chatllm/
│   │   ├── deep-agent/
│   │   ├── handoffs/
│   │   └── jules/
│   ├── _cost_governance.md
│   ├── _handoffs/
│   │   ├── archive/
│   │   ├── PHANTOM_HANDOFFS_RESOLVED.md
│   │   └── handoff-*.md (30+ active handoffs)
│   ├── _hic_needed_template.md
│   ├── _logs/
│   │   └── api_healer_20260220.json
│   ├── _protocols.md
│   ├── _sessions/
│   │   ├── 2026-01-29-inaugural.md
│   │   ├── 2026-02-1[6-9]-*.md (daily briefings & work sessions)
│   │   ├── HiC_Notes*.md
│   │   └── claude-*-20260219-*.md
│   ├── _shared/
│   │   ├── knowledge/user_preference.txt
│   │   ├── memories/procedural/
│   │   └── skills/hive_content_creation.md
│   ├── _templates/
│   │   ├── decision_record.md
│   │   ├── episodic_memory.md
│   │   ├── handoff-with-skill-links.md
│   │   ├── handoff.md
│   │   ├── learnings.md
│   │   └── meeting_notes.md
│   ├── _tools/
│   │   └── quality_gate.py
│   ├── _voting.md
│   ├── abacus/
│   │   ├── Deep Agent.mp4
│   │   ├── context/active.md
│   │   ├── handoff.md
│   │   ├── memory.md
│   │   └── profile.md
│   ├── claude/
│   │   ├── Professor Claude.mp4
│   │   ├── context/active.md
│   │   ├── handoff.md
│   │   ├── memory.md
│   │   └── profile.md
│   ├── gemini/
│   │   ├── *.mp4 (6 personality clips)
│   │   ├── context/active.md
│   │   ├── handoff.md
│   │   ├── memory.md
│   │   └── profile.md
│   ├── grok/
│   │   ├── Grok Boss Babe.mp4
│   │   ├── context/active.md
│   │   ├── handoff.md
│   │   ├── memory.md
│   │   └── profile.md
│   ├── memory_guide.md
│   ├── roadmap-2026.json
│   ├── russell/
│   │   ├── BPR&D Proposed Structure
│   │   ├── BPR&D_FINAL_STRUCTURE.md
│   │   ├── Chief ES
│   │   ├── POST_REORG_TREE.md          ← you are here
│   │   ├── first_week_retrospective_claude.md
│   │   ├── handoff.md
│   │   ├── week_one_alchemical_analysis.md
│   │   └── 2026-02-25-chief-memesearcher-weekly-review.md
│   └── team_state.md
├── _archive/
│   ├── knowledge_system/
│   │   ├── knowledge_graph_v2.py
│   │   └── upgrade_migration.py
│   ├── skill_webs/
│   │   └── skill_web_v2.py
│   └── tests/
│       └── test_knowledge_system_v2.py
├── _shared/
│   ├── backlog.json
│   ├── knowledge/foundations/
│   │   ├── founding-charter.md
│   │   └── org-structure.md
│   ├── knowledge/strategic/
│   │   └── strategic-review-2026-02.md
│   ├── memories/
│   │   ├── episodic/ (3 files)
│   │   └── strategic/ (1 file)
│   ├── skill-graphs/bprd-core/
│   │   ├── MOC-*.md (4 Maps of Content)
│   │   ├── agent-hooks/ (6 hook files)
│   │   ├── reflections/ (3 reweave files)
│   │   ├── skill-*.md (30+ skill definitions)
│   │   └── skill-graphs/navigation.md
│   ├── skills/
│   │   ├── README.md
│   │   ├── automation/n8n-integration/
│   │   ├── coding/frontend-design/
│   │   ├── coding/mcp-builder/
│   │   ├── coding/webapp-testing/
│   │   ├── communication/brand-guidelines/
│   │   ├── communication/internal-comms/
│   │   ├── communication/writing-skills/
│   │   ├── creative/algorithmic-art/
│   │   ├── data/xlsx/
│   │   ├── document/docx/
│   │   ├── document/pdf/
│   │   ├── document/pptx/
│   │   ├── meta/skill-creator/
│   │   ├── writing/current-events/
│   │   ├── writing/fiction-narrative-craft/
│   │   ├── writing/non-fiction-topics/
│   │   ├── writing/research-brief/
│   │   ├── writing/research-premium/
│   │   └── writing/research-report/
│   └── templates/ (4 template files)
├── assets/
│   ├── financials/assets_tracker.md
│   ├── generated/.gitkeep
│   └── images/.gitkeep
├── content/
│   ├── automation/
│   │   ├── README.md
│   │   ├── content_generator.py
│   │   ├── hive_publisher.py
│   │   ├── orchestrator.py
│   │   └── requirements.txt
│   ├── automation_pipelines/.gitkeep
│   ├── hive_posts/
│   │   ├── drafts/ (1 draft)
│   │   └── published/.gitkeep
│   ├── quality_standards.md
│   └── templates/ (5 content templates)
├── crewai-service/                      ← Meeting Engine
│   ├── .env.example
│   ├── .gitignore
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── persona.py
│   │   └── registry.py
│   ├── api_healer.py
│   ├── backlog/
│   │   ├── __init__.py
│   │   └── discovery.py
│   ├── config.py
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── abacus.py
│   │   ├── anthropic_provider.py
│   │   ├── base.py
│   │   ├── google_provider.py
│   │   └── xai.py
│   ├── main.py
│   ├── meetings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── daily_briefing.py
│   │   └── work_session.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── meeting.py
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   └── transcript.py
│   ├── output/
│   │   ├── __init__.py
│   │   ├── github_writer.py
│   │   ├── notifier.py
│   │   ├── parser.py
│   │   └── renderer.py
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── nervous_system_injector.py
│   ├── requirements.txt
│   ├── scheduling/
│   │   ├── __init__.py
│   │   └── scheduler.py
│   ├── scripts/
│   │   ├── debug_gemini.py
│   │   ├── test_crew.py
│   │   ├── test_server.sh
│   │   └── verify_llms.py
│   ├── tests/ (5 test files)
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── github_tool.py
│   │   ├── github_tools.py
│   │   └── memory_tool.py
│   └── utils/
│       ├── __init__.py
│       └── cost_tracker.py
├── data/                                ← NEW: data directory
│   └── .gitkeep
├── docs/
│   ├── AGENT_MEMORY_*.md (4 files)
│   ├── AVATAR_EXTRACTION_GUIDE.md
│   ├── DDAS_Strategic_Plan.md
│   ├── EXECUTION_SUMMARY.md
│   ├── IMPLEMENTATION_CHECKLIST.md
│   ├── IMPLEMENTATION_STATUS.md
│   ├── JULIUS_INSTRUCTIONS_V2.md
│   ├── MODEL-REFERENCE.md
│   ├── QUICKSTART.md
│   ├── README.md
│   ├── README_GAMES.md
│   ├── SETUP_SUMMARY.txt
│   ├── START_HERE.md
│   ├── VIDEO_AUDIO_PRODUCTION.md
│   ├── WRITING_SKILLS_SUMMARY.md
│   ├── api-configuration.md
│   ├── archive/ (4 legacy docs)
│   ├── file_structure.md
│   ├── onboarding.md
│   ├── post-crisis-recovery-protocol.md
│   └── protocols/
│       ├── Agent_Context_Guide.md
│       └── Team_Meeting_Protocol_v2.md
├── games/
│   ├── shared-assets/scripts/
│   │   ├── game_constants.gd
│   │   └── save_manager.gd
│   ├── slingerlands-rpg/
│   │   ├── project.godot
│   │   └── scenes/main.gd
│   └── splinterlands-civ/
│       ├── project.godot
│       └── scenes/main.gd
├── meetings/
│   └── logs/.gitkeep
├── pipelines/
│   ├── .gitkeep
│   ├── content/hive-pipeline-v0.1.py
│   └── github-bot/
│       ├── .pr_agent.toml
│       ├── README.md
│       ├── meeting-parser/ (7 files)
│       ├── scripts/alchemist_persona.py
│       └── workflow-file-content.yml
├── projects/
│   ├── ai-comm-hub/habitat/
│   │   ├── data/epstein/.gitignore
│   │   ├── deep-agent/
│   │   ├── docker-compose.yml
│   │   ├── jules/
│   │   ├── proxy/
│   │   ├── services/epstein-analysis/
│   │   ├── shared/
│   │   └── spin-epstein.sh
│   ├── content-creation-challenge/
│   │   └── Project Initiation.txt
│   └── media-production/
│       ├── README.md
│       └── pipeline.md
├── publishing/
│   └── hive/drafts/ (2 files)
├── render.yaml                          ← Render deployment config
├── render-crewai.yaml
├── research/
│   ├── README.md
│   ├── _templates/ (2 templates)
│   ├── ancient-religions-lost-civilizations/ (8 briefs)
│   ├── corruption-investigation/
│   │   ├── briefs/ (8 briefs + epstein-doj-analysis/)
│   │   └── epstein-doj-analysis/ (full analysis pipeline)
│   ├── daily_briefs/
│   ├── epstein-daily/
│   │   ├── graph/ (2 JSON files)
│   │   ├── nightly-output/ (3 date folders)
│   │   ├── nightly_processor.py
│   │   └── processed/ (3 date folders)
│   ├── extraterrestrial/ (8 briefs)
│   ├── great-works-and-writing/ (9 briefs)
│   ├── grok-nightly/ (5 files)
│   ├── high-tech/ (9 briefs + prototypes/)
│   ├── history-and-archaeology/ (8 briefs)
│   ├── hive_blogging_mastery/.gitkeep
│   ├── media_content_mastery/.gitkeep
│   ├── norse-mythology/ (8 briefs)
│   ├── open-lanes/ (8 briefs)
│   ├── permaculture/ (8 briefs)
│   ├── social_media_marketing/.gitkeep
│   ├── special-reports/ (7 reports + assets/)
│   └── topics_to_explore.md
├── scripts/
│   ├── generate_hive_images.py
│   ├── trigger_abacus_work_session.py
│   ├── verify_endpoint.py
│   └── verify_endpoint_crewai.py
├── tasks/
│   ├── archived/.gitkeep
│   └── projects/
│       └── GitHub_PR_Automation_Bot.md
├── verification/
│   ├── research_detail.png
│   ├── research_listing.png
│   └── verify_research.py
├── web/                                 ← Next.js 15 Website
│   ├── .env.example
│   ├── .gitignore
│   ├── README.md
│   ├── bun.lock
│   ├── eslint.config.mjs
│   ├── next.config.ts
│   ├── package.json
│   ├── package-lock.json
│   ├── postcss.config.mjs
│   ├── public/
│   │   ├── agents/ (4 mp4s)
│   │   ├── avatars/ (4 pngs)
│   │   └── *.svg (5 icons)
│   ├── scripts/ (10 utility scripts)
│   ├── src/
│   │   ├── app/
│   │   │   ├── actions/ (2 server actions)
│   │   │   ├── api/hic/trigger/route.ts
│   │   │   ├── dashboard/page.tsx
│   │   │   ├── globals.css
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── projects/ (3 project pages)
│   │   │   ├── research/ (dynamic routes)
│   │   │   ├── resources/page.tsx
│   │   │   └── team/
│   │   │       ├── AgentMetrics.tsx
│   │   │       ├── AgentStatus.tsx
│   │   │       ├── [slug]/page.tsx
│   │   │       ├── meeting/page.tsx
│   │   │       └── page.tsx
│   │   ├── components/
│   │   │   ├── ApiUsageMonitor.tsx
│   │   │   ├── AssembleCrewButton.tsx
│   │   │   ├── avatar.tsx
│   │   │   ├── gamification/leaderboard.tsx
│   │   │   ├── icons/custom-icons.tsx
│   │   │   ├── navbar.tsx
│   │   │   ├── particle-background.tsx
│   │   │   ├── production/ (4 components)
│   │   │   ├── quest-board.tsx
│   │   │   └── ui/ (10 UI components)
│   │   ├── content/
│   │   │   ├── agents.json
│   │   │   ├── metrics.json
│   │   │   ├── production.json
│   │   │   └── research/ (9 topic folders, ~72 briefs)
│   │   ├── context/
│   │   │   └── gamification-context.tsx
│   │   └── lib/
│   │       ├── agents.ts
│   │       ├── ai-agents/ (4 agent configs)
│   │       ├── db.ts
│   │       ├── handoffs.ts
│   │       ├── meeting/MeetingManager.ts
│   │       ├── research.ts
│   │       └── utils.ts
│   ├── tsconfig.json
│   ├── vitest.config.ts
│   └── vitest.setup.ts
├── .env.example
├── .gitignore
├── BPR&D_To_Do_List.md
├── LICENSE
├── README.md
└── requirements.txt
```

**Summary**: 1,022 tracked files across 15 top-level directories.
Repo is clean on `repo-cleanup` branch, ready for merge to `main`.
