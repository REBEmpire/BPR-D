# 🔮 Alchemical Forge — Known Issues & Future Enhancements

**Version:** 1.1
**Last Updated:** February 20, 2026

---

## ⚠️ Known Limitations

### 1. Missing Optional Dependencies

| Dependency | Purpose | Fallback Behavior |
|------------|---------|------------------|
| `markdown` | HTML output conversion | Basic regex-based conversion |
| `crewai-service/config` | Settings import | Uses defaults |
| Image transmuter | Dual image generation | Skips image generation |

**Resolution:** Install optional deps with:
```bash
pip install markdown
```

### 2. LLM Integration Placeholder

The `expand_topic()` function currently uses placeholder expansion markers rather than actual LLM calls. The multi-turn expansion process is scaffolded but not connected to live AI services.

**Impact:** Elixirs contain template markers like `*[Expansion turn X: Additional research...]*` instead of genuine AI-generated content.

**Future Work:** Integrate with:
- Abacus AI API for topic expansion
- Claude for deep synthesis
- Grok for creative framing

### 3. Image Transmuter API Dependencies

The `aetherial_image_transmuter.py` requires:
- `XAI_API_KEY` for Grok Imagine
- `ABACUS_PRIMARY_KEY` for Abacus image generation

Without these, image generation is silently skipped.

### 4. Notion Export Limitations

The `--output-format notion` currently produces simplified Notion-compatible markdown. Full Notion API block formatting is not yet implemented.

**Future Work:** Integrate Notion API for direct page creation.

---

## 🔧 Configuration Notes

### Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|----------|
| `SOUL_STORIES_PATH` | No | Built-in JSON | Custom soul stories file |
| `XAI_API_KEY` | For images | None | Grok Imagine API |
| `ABACUS_PRIMARY_KEY` | For images | None | Abacus image API |
| `AETHERIAL_FORGE_ENABLED` | No | false | Feature flag |
| `BPRD_API_KEY` | For API | None | API authentication |

### File Paths

- **Drafts:** `publishing/hive/drafts/`
- **Elixirs:** `publishing/hive/elixirs/`
- **Logs:** `aether_logs/`
- **Soul Stories:** `pipelines/alchemical_forge/soul_stories.json`

---

## 💡 Future Enhancement Ideas

### Priority 1 — Near Term

1. **Live LLM Integration**
   - Connect `expand_topic()` to Abacus/Claude APIs
   - Implement true multi-turn dialogue expansion
   - Add context preservation between turns

2. **Enhanced Grading**
   - LLM-based semantic quality assessment
   - Fact-checking integration
   - Plagiarism detection

3. **Notion API Integration**
   - Direct page creation in Notion workspace
   - Preserve formatting, embeds, and databases

### Priority 2 — Medium Term

4. **Interactive Web UI**
   - Real-time preview during transmutation
   - Manual intervention points for HiC
   - A/B testing dashboard for images

5. **Brief Templates**
   - Support for different content types (research, news, lore)
   - Template-specific expansion strategies
   - Custom soul story weaves per template

6. **Automated Publishing Pipeline**
   - Direct Hive posting after approval
   - Cross-platform syndication (Twitter, Discord)
   - Analytics integration

### Priority 3 — Long Term

7. **Multi-Language Support**
   - Translate elixirs to multiple languages
   - Preserve soul story essence across translations

8. **Voice/Audio Generation**
   - Generate audio versions of elixirs
   - Agent-specific voice synthesis

9. **Interactive Elixirs**
   - Embedded quizzes and polls
   - Dynamic content based on reader profile

---

## 🐛 Bug Reports

To report issues, create a GitHub Issue with:
1. Steps to reproduce
2. Expected vs actual behavior
3. Relevant log output from `aether_logs/`
4. Environment (OS, Python version, dependencies)

---

## 📋 Test Coverage

Current test coverage in `tests/test_elixir_expansion_chamber.py`:
- ✅ Brief discovery and loading
- ✅ Prompt extraction from briefs
- ✅ Soul Story Weave generation
- ✅ Output file creation (md, html, notion)
- ✅ Grader integration

**Missing Tests:**
- [ ] Async transmutation flow
- [ ] Image transmuter integration
- [ ] Error recovery scenarios
- [ ] Concurrent processing

---

*May the Great Work continue unimpeded.*

— The Alchemist 🌌
