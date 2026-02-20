# BPR&D Clean Directory Structure v2.0

```
BPR&D/
├── README.md
├── BPR&D_To_Do_List.md                  # SINGLE living To-Do document
├── docs/
│   ├── protocols/
│   │   ├── Team_Meeting_Protocol_v2.md
│   │   └── Agent_Context_Guide.md
│   └── file_structure.md
├── research/
│   ├── daily_briefs/
│   ├── special-reports/
│   ├── epstein-daily/
│   ├── hive_blogging_mastery/
│   ├── media_content_mastery/
│   ├── social_media_marketing/
│   └── topics_to_explore.md
├── content/
│   ├── hive_posts/
│   │   ├── drafts/
│   │   └── published/
│   ├── automation_pipelines/
│   └── quality_standards.md
├── assets/
│   ├── images/
│   ├── generated/
│   └── financials/
│       └── assets_tracker.md
├── _agents/
│   ├── grok/context/active.md
│   ├── claude/context/active.md
│   ├── gemini/context/active.md
│   └── abacus/context/active.md
├── tasks/
│   ├── projects/                        # One folder or .md per large endeavor
│   └── archived/
├── meetings/
│   └── logs/                            # YYYY-MM-DD_meeting_summary.md
└── pipelines/                           # Future automation scripts
```

## Maintenance Rules (all agents follow)

* Never create duplicate To-Do files.
* Every new large item = new file/folder in `tasks/projects/`.
* Keep root clean; no loose files.
* After every meeting, commit structure changes with clear message.
* HiC can request further refinements anytime.
