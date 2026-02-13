# DDAS Quick Start Guide

Get up and running with DDAS game development and content automation in under an hour.

## 📋 What You're Getting

- **2 Game Prototypes**: Splinterlands 4X strategy + Slingerlands RPG (Godot-based)
- **Content Automation**: AI-powered writing for 5 Hive accounts
- **Media Pipeline**: Video (YouTube) and audio (Podcasts) ready to launch
- **Complete Documentation**: Strategic plans, setup guides, development roadmaps

## 🚀 Quick Start (Choose Your Path)

### Path A: Game Developer
Want to jump into game development?

```bash
# 1. Install Godot 4.x from https://godotengine.org/download
# 2. Open either game project
cd games/splinterlands-civ
# (or: cd games/slingerlands-rpg)

# 3. Launch Godot, open project folder
# 4. Open scenes/main.tscn and press F5 to test

# 5. Start modifying scenes and scripts!
```

**Next**: Read `README_GAMES.md` for architecture and development guide

---

### Path B: Content Creator
Want to run the content automation pipeline?

```bash
# 1. Install Python 3.8+
python --version

# 2. Set up content automation
cd content/automation
python -m venv venv

# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Test content generation (no publishing)
python orchestrator.py --provider claude

# 5. Check generated_content/ folder for output
```

**Next**: Read `content/automation/README.md` for full setup

---

### Path C: Video/Audio Producer
Want to set up video and podcast pipeline?

```bash
# 1. Install tools
# - OBS Studio: https://obsproject.com/
# - DaVinci Resolve (free): https://www.blackmagicdesign.com/products/davinciresolve/
# - FFmpeg: https://ffmpeg.org/download.html

# 2. Create YouTube channel
# - Go to YouTube.com
# - Create channel named "DDAS" or similar
# - Enable video uploads

# 3. Create podcast on Spotify Podcasters
# - Go to podcasters.spotify.com
# - Click "Start a podcast"
# - Create RSS feed

# 4. Read the video/audio production guide
```

**Next**: Read `VIDEO_AUDIO_PRODUCTION.md` for complete setup

---

## 📁 Directory Guide

```
DDAS/
├── DDAS_Strategic_Plan.md          ← Big picture strategy
├── README_GAMES.md                 ← Game development guide
├── VIDEO_AUDIO_PRODUCTION.md       ← Media production setup
├── QUICKSTART.md                   ← This file

├── games/
│   ├── splinterlands-civ/          ← 4X Strategy game
│   │   └── Open in Godot 4.x
│   ├── slingerlands-rpg/           ← Turn-based RPG
│   │   └── Open in Godot 4.x
│   └── shared-assets/              ← Common game code

├── content/
│   ├── automation/                 ← Python scripts for content
│   │   ├── orchestrator.py         ← Main script to run daily
│   │   ├── content_generator.py    ← AI content generation
│   │   ├── hive_publisher.py       ← Hive blockchain posting
│   │   └── README.md               ← Detailed setup
│   └── templates/                  ← Content templates (5 accounts)

└── backend/                        ← Game server setup (optional)
```

## 🎯 Essential First Steps

### For Everyone
- [ ] Read `DDAS_Strategic_Plan.md` (comprehensive overview - 30 min)
- [ ] Review this file completely
- [ ] Set up GitHub (if not done): Create repository and add team

### For Game Developers
- [ ] Download Godot 4.x
- [ ] Open `games/splinterlands-civ/project.godot` in Godot
- [ ] Read `README_GAMES.md` → Phase 1 section
- [ ] Start implementing Phase 1 features

### For Content Creators
- [ ] Create 5 Hive accounts (or use existing ones)
- [ ] Set up Python environment (`cd content/automation`)
- [ ] Test content generation: `python orchestrator.py --provider claude`
- [ ] Read `content/automation/README.md` for publishing setup

### For Media Producers
- [ ] Install OBS, DaVinci Resolve, FFmpeg
- [ ] Create YouTube channel
- [ ] Set up Spotify Podcasters account
- [ ] Read `VIDEO_AUDIO_PRODUCTION.md` for automation

---

## 🔧 Configuration Files to Create

These are needed to run the actual automation (not for testing):

```
publisher_config.json
├── Contains Hive posting keys
├── DO NOT commit to git
├── Required for: python orchestrator.py --publish

.env
├── API keys (Claude, OpenAI, etc.)
├── DO NOT commit to git
├── Used for: API authentication
```

**⚠️ WARNING**: Never share your private keys! Keep them secret!

---

## 📊 5 Hive Accounts Overview

Each account has a specific purpose:

| Account | Focus | Posts/Week | Best For |
|---------|-------|-----------|----------|
| @ddas-devblog | Technical updates | 5-7 | Developers, tech audience |
| @ddas-lore | Stories & worldbuilding | 5-7 | Creative audience |
| @ddas-strategy | Game guides & tips | 5-7 | Competitive players |
| @ddas-community | Player spotlights | 3-5 | Community engagement |
| @ddas-news | Announcements & roundups | 3-5 | General announcements |

**Total Target**: 5+ articles daily across all accounts

---

## 💻 Command Reference

### Game Development
```bash
# Launch Godot
godot games/splinterlands-civ/project.godot

# Run game (press F5 in Godot)
# Or export: File → Export Project → HTML5
```

### Content Automation
```bash
# Generate content (dry run, no publishing)
python orchestrator.py --provider claude

# Generate and test publish (dry run still active)
python orchestrator.py --provider claude --publish

# Actually publish to Hive (use with caution!)
python orchestrator.py --provider claude --publish --no-dry-run

# Check available prompts
python content_generator.py
```

### Video/Media
```bash
# Record with OBS: Click "Start Recording"

# Process video with FFmpeg:
ffmpeg -i input.mp4 -c:v libx264 -crf 23 output.mp4

# Generate text-to-speech (if configured):
python media_orchestrator.py --generate-podcast
```

---

## 🎓 Learning Path

### Week 1: Foundations
- [ ] Understand project structure (read all docs)
- [ ] Set up development environment
- [ ] Get first game running in Godot
- [ ] Generate first test article

### Week 2: Initial Features
- [ ] Implement Phase 1 game mechanics
- [ ] Publish first 5 articles to Hive
- [ ] Set up content calendar
- [ ] Record first gameplay footage

### Week 3: Content Pipeline
- [ ] Launch daily content automation
- [ ] Post to 5 accounts consistently
- [ ] Create first YouTube video
- [ ] Record first podcast episode

### Week 4+: Scaling
- [ ] Polish games for beta
- [ ] Establish content rhythm
- [ ] Grow audience on all platforms
- [ ] Implement networking/multiplayer

---

## ❓ Common Questions

**Q: Do I need to know GDScript?**
A: No! But if you're doing game dev, you'll learn it fast. Resources included in docs.

**Q: Do I need coding skills for content automation?**
A: Python experience helps, but the orchestrator script is easy to use. Just run it daily.

**Q: What if I don't have an API key?**
A: Test with dry-run mode first. See `content/automation/README.md` for free alternatives.

**Q: Can I use these games commercially?**
A: Yes! They're designed for Hive rewards and potentially NFT integration.

**Q: How long does this take to set up?**
A: 1-2 hours to get everything running. Full feature development depends on team size.

**Q: What's the monthly cost?**
A: $0 minimum (free tier). Realistic: $20-50/month for premium services (optional).

---

## 📞 Getting Help

1. **Check the relevant README**:
   - Game dev: `README_GAMES.md`
   - Content: `content/automation/README.md`
   - Media: `VIDEO_AUDIO_PRODUCTION.md`
   - Strategy: `DDAS_Strategic_Plan.md`

2. **Review your logs**:
   - `ddas_orchestrator.log` (content automation)
   - Godot console (game development)
   - FFmpeg output (video processing)

3. **Consult documentation**:
   - Godot: https://docs.godotengine.org/
   - Hive API: https://developers.hive.io/
   - FFmpeg: https://ffmpeg.org/
   - YouTube API: https://developers.google.com/youtube/v3

4. **Ask the team**: Discuss in Discord/GitHub Issues

---

## ✅ Setup Checklist

- [ ] Read `DDAS_Strategic_Plan.md`
- [ ] Clone/sync this repository
- [ ] Create 5 Hive accounts (or note existing ones)
- [ ] Set up GitHub with team members
- [ ] Install Godot 4.x (game developers)
- [ ] Install Python 3.8+ (content creators)
- [ ] Install OBS/DaVinci/FFmpeg (media producers)
- [ ] Create `publisher_config.json` (content automation)
- [ ] Test game launch in Godot
- [ ] Test content generation: `python orchestrator.py --provider claude`
- [ ] Create YouTube channel
- [ ] Create Spotify Podcasters account
- [ ] Schedule first team meeting/standup

---

## 🎯 Current Status

**Phase**: Foundation Setup ✅ Complete
**Next Phase**: Phase 1 Development (Week 1-2)

You're ready to start building!

---

## 📚 Documentation Structure

```
DDAS/
├── QUICKSTART.md                   ← You are here
├── DDAS_Strategic_Plan.md          ← Full strategy & timeline
├── README_GAMES.md                 ← Game dev guide
├── VIDEO_AUDIO_PRODUCTION.md       ← Media production guide
│
└── content/automation/
    └── README.md                   ← Content automation setup
```

**Read in this order**:
1. QUICKSTART.md (this file)
2. DDAS_Strategic_Plan.md (overview)
3. Your specialization (Games/Content/Media)
4. Run tests and start building!

---

**Version**: 1.0
**Last Updated**: 2026-02-12
**Status**: Ready for Development

## 🚀 Ready to Build?

Pick your path above and let's go!

Questions? Check the docs or ask the team.

Good luck! 💪
