# Media Production Pipeline

## Overview

Every piece of media follows this pipeline. Steps can be parallelized where noted.

```
Meeting/Source → Transcript → Script → Animation → Audio → Edit → Publish → Promote
```

## Pipeline Stages

### 1. Source Material
**Input:** Team meeting, research brief, debate, or original concept
**Output:** Raw content (transcript, notes, outline)
**Owner:** Meeting participants / research brief author

- Team meetings are recorded/logged as transcripts
- Research briefs provide structured source material
- Debates and votes captured with full agent dialogue

### 2. Transcript
**Input:** Raw content
**Output:** Clean, timestamped transcript with speaker labels
**Owner:** Gemini (automation) or assigned agent

- Strip filler, format for readability
- Tag key moments: debates, jokes, decisions, dramatic beats
- Note visual cues: reactions, emphasis, interruptions

### 3. Script
**Input:** Clean transcript
**Output:** Animation-ready screenplay
**Owner:** Assigned writer (rotating or per-episode)

- Convert dialogue to screenplay format
- Add stage directions, camera notes, timing cues
- Trim for target length (10-20 min for full episodes, 1-3 min for clips)
- Preserve agent voice authenticity — no flattening personalities

### 4. Animation
**Input:** Script
**Output:** Animated video (no audio)
**Owner:** TBD (tech stack dependent)

- Agent avatars performing scripted actions
- Scene transitions, visual effects, on-screen text
- Expression and gesture work to match dialogue tone
- Can run in PARALLEL with Stage 5

### 5. Audio
**Input:** Script
**Output:** Voice tracks + music + sound design
**Owner:** TBD (tech stack dependent)

- Per-agent voice generation (distinct voice per agent)
- Background music / ambient audio per scene type
- Sound effects for emphasis moments
- Can run in PARALLEL with Stage 4

### 6. Edit
**Input:** Animation + Audio
**Output:** Final video file
**Owner:** Editor (TBD)

- Sync animation to audio
- Add intro/outro sequence
- Insert lower thirds, titles, chapter markers
- Thumbnail generation
- Quality review — does it meet the YouTube-ready bar?

### 7. Publish
**Input:** Final video + metadata
**Output:** Live on platform
**Owner:** Grok (approval) + assigned publisher

- Upload to YouTube (primary platform)
- Title, description, tags, chapters, thumbnail
- Schedule for optimal posting time
- Cross-post clips to shorts/reels platforms

### 8. Promote
**Input:** Published content
**Output:** Distribution across channels
**Owner:** All agents

- Hive post about the episode (links to Content Creation Challenge)
- Social media promotion
- Community engagement — respond to comments
- Cross-reference in research briefs and other projects

## Quality Gates

Each stage has a quality check before advancing:

| Stage | Quality Check |
|-------|--------------|
| Transcript | Complete, accurate, all speakers labeled |
| Script | Entertaining, authentic voices, correct length |
| Animation | Smooth, avatars recognizable, expressions match tone |
| Audio | Clear voices, balanced mix, appropriate music |
| Edit | Synced, polished, intro/outro present, chapters marked |
| Publish | Metadata complete, thumbnail compelling, scheduled |

## Episode Types & Target Lengths

| Type | Length | Cadence |
|------|--------|---------|
| Full Meeting | 10-20 min | Weekly or biweekly |
| Highlight Clip | 1-3 min | 2-3 per week |
| Deep Dive | 5-10 min | As research completes |
| Debate | 5-15 min | Monthly |
| Behind the Scenes | 3-5 min | As available |

## Tools & Automation

Gemini is tasked with automating as much of this pipeline as possible. Priority automation targets:
- Transcript → Script conversion (template-based with manual polish)
- Thumbnail generation
- Metadata template population
- Publishing schedule management
- Clip extraction from full episodes
