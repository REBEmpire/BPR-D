# BPR&D Directory Structure v3.0

Updated: 2026-02-20 (post-cleanup)

```
BPR&D/
├── README.md                           # Project overview + quick links
├── BPR&D_To_Do_List.md                 # SINGLE living To-Do document
├── LICENSE
├── .gitignore
├── render.yaml                         # Render deployment (web)
├── render-crewai.yaml                  # Render deployment (meeting service)
├── requirements.txt                    # Root Python dependencies
│
├── docs/                               # All documentation
│   ├── protocols/
│   │   ├── Team_Meeting_Protocol_v2.md
│   │   └── Agent_Context_Guide.md
│   ├── archive/                        # Superseded docs
│   ├── START_HERE.md                   # 5-minute orientation
│   ├── QUICKSTART.md                   # 15-minute setup
│   ├── DDAS_Strategic_Plan.md          # Full roadmap
│   ├── README_GAMES.md                 # Game dev guide
│   ├── VIDEO_AUDIO_PRODUCTION.md       # Media workflows
│   ├── JULIUS_INSTRUCTIONS_V2.md       # Research coordinator
│   ├── file_structure.md               # This file
│   └── ...
│
├── _agents/                            # AI agent system
│   ├── grok/                           # Agent: profile, memory, handoff, context/
│   ├── claude/
│   ├── gemini/
│   ├── abacus/
│   ├── russell/                        # Human-in-Charge notes
│   ├── _archive/                       # Retired agents (chatllm, deep-agent, jules)
│   ├── _handoffs/                      # Team handoff tickets
│   ├── _sessions/                      # Meeting & work session logs
│   ├── _shared/                        # Shared agent resources
│   ├── _templates/                     # Agent file templates
│   ├── _tools/                         # Agent tooling (quality_gate.py)
│   ├── _logs/                          # Agent operational logs
│   ├── team_state.md                   # Live team status
│   ├── _protocols.md                   # Agent protocols
│   ├── _cost_governance.md             # Budget rules
│   ├── _voting.md                      # Voting procedures
│   ├── roadmap-2026.json               # Milestone tracking
│   └── PRE-LAUNCH-CHECKLIST.md
│
├── _shared/                            # Shared resources
│   ├── knowledge/                      # Organizational knowledge
│   ├── memories/                       # Episodic & strategic memories
│   ├── skill-graphs/                   # Skill web definitions
│   ├── skills/                         # Reusable skill modules
│   ├── templates/                      # Document templates
│   └── backlog.json                    # Team backlog
│
├── research/                           # 9 research topics + special
│   ├── ancient-religions-lost-civilizations/
│   ├── corruption-investigation/
│   ├── epstein-daily/
│   ├── extraterrestrial/
│   ├── great-works-and-writing/
│   ├── high-tech/
│   ├── history-and-archaeology/
│   ├── norse-mythology/
│   ├── open-lanes/
│   ├── permaculture/
│   ├── daily_briefs/
│   ├── special-reports/
│   ├── hive_blogging_mastery/
│   ├── media_content_mastery/
│   ├── social_media_marketing/
│   └── _templates/
│
├── content/                            # Content pipeline
│   ├── automation/                     # Python content generator
│   ├── templates/                      # 5 Hive content templates
│   ├── hive_posts/                     # Drafts & published
│   ├── automation_pipelines/
│   └── quality_standards.md
│
├── games/                              # Godot 4.x game projects
│   ├── splinterlands-civ/              # 4X strategy
│   ├── slingerlands-rpg/               # Turn-based dungeon crawler
│   └── shared-assets/                  # Shared GDScript utilities
│
├── web/                                # Next.js 15 web application
│   ├── src/
│   ├── public/
│   ├── scripts/
│   └── package.json
│
├── crewai-service/                     # Custom meeting service
│   ├── main.py                         # FastAPI entry point
│   ├── orchestrator/                   # Meeting engine
│   ├── llm/                            # LLM providers (xAI, Anthropic, Google)
│   ├── output/                         # GitHub writer, renderer
│   ├── tools/                          # GitHub, memory tools
│   ├── backlog/                        # Backlog discovery
│   └── meetings/                       # Meeting type definitions
│
├── pipelines/                          # Automation pipelines
│   ├── content/                        # Hive content pipeline
│   └── github-bot/                     # PR agent, meeting parser
│
├── assets/                             # Media assets
│   ├── images/
│   ├── generated/
│   └── financials/
│
├── publishing/                         # Hive publishing
│   └── hive/
│       ├── drafts/
│       └── published/
│
├── tasks/                              # Task tracking
│   ├── projects/                       # One folder or .md per project
│   └── archived/
│
├── meetings/                           # Meeting logs
│   └── logs/
│
├── scripts/                            # Utility scripts
├── tests/                              # Test suites
├── verification/                       # Research verification tools
│
├── _archive/                           # Archived legacy code
│   ├── knowledge_system/
│   ├── skill_webs/
│   └── tests/
│
├── .github/                            # GitHub Actions workflows
├── .bprd/                              # BPR&D configuration
├── .devcontainer/                      # Dev container setup
└── .claude/                            # Claude Code settings
```

## Maintenance Rules (all agents follow)

* Never create duplicate To-Do files.
* Every new large item = new file/folder in `tasks/projects/`.
* Keep root clean; no loose files (docs go in `docs/`).
* After every meeting, commit structure changes with clear message.
* Do NOT move files referenced by crewai-service or web at runtime.
* HiC can request further refinements anytime.
