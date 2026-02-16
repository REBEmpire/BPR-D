# DOJ Epstein Document Analysis System
## BPR&D Research Focus Project #1

Privacy-conscious analysis system for processing 3.5M+ pages of DOJ Epstein document releases without local storage.

## Development Status

**Phase 0 (Foundation)**: ✅ COMPLETE
**Phase 1 (Basic Processing)**: ✅ COMPLETE
**Phase 2 (Advanced Analysis)**: ✅ COMPLETE

Ready for deployment and real document processing.

## Primary Investigation Goals

1. **Break Their Code** - Decode correspondence using code words, aliases, and obfuscated language
2. **Map the Players** - Create comprehensive network graph of all individuals, organizations, and their relationships
3. **Timeline Reconstruction** - Build detailed chronological timeline of activities, travel, meetings, and events
4. **Location Analysis** - Deep dive into activities at specific locations:
   - Little St. James Island (USVI)
   - Zorro Ranch (New Mexico)
   - Manhattan townhouse
   - Palm Beach residence
   - Other properties and travel destinations

## Privacy Guarantees

- **NO local file storage** - PDFs stream directly to memory via WebFetch
- **NO cloud storage of source documents** - Only analysis results stored in private Hugging Face dataset
- **Automated privacy verification** - PrivacyGuard monitors and prevents file creation
- **Zero-touch processing** - All operations in-memory, Python garbage collection auto-clears data

## Quick Start

### Installation

```bash
# Install dependencies
cd research/corruption-investigation/briefs/epstein-doj-analysis
pip install -r requirements.txt

# Download spaCy model (required for Phase 2 NER)
python -m spacy download en_core_web_lg
```

### Test Phase 2 Pipeline

```bash
# Test all Phase 2 components
python scripts/test_phase2_pipeline.py

# Test individual components
python -m extractors.entity_extractor
python -m extractors.timeline_builder
python -m extractors.code_breaker
python -m analyzers.network_mapper
```

### Initialize Hugging Face Dataset (One-time)

```bash
python scripts/init_hf_dataset.py
```

### Run Daily Analysis Session (60 minutes)

```bash
# Resume from last checkpoint
python scripts/resume_session.py

# Or start fresh session
python scripts/run_session.py
```

### Generate Investigation Reports

```bash
python scripts/generate_report.py
```

## Architecture

```
DOJ Website (justice.gov/epstein)
    ↓ [WebFetch - streaming only]
In-Memory PDF Processing (io.BytesIO)
    ↓ [Extract text, metadata, images]
Analysis Engine (NER, Timeline, Redactions, Code Breaking, Network Mapping)
    ↓ [Process, analyze, correlate]
Hugging Face Dataset (analysis results ONLY)
    ↓ [Session checkpoints, cross-session resume]
```

## Daily Workflow

### Session Structure (60 minutes)

1. **00:00 - 05:00** - Initialization (resume checkpoint, initialize PrivacyGuard)
2. **05:00 - 50:00** - Document processing loop (stream, extract, analyze, save)
3. **50:00 - 55:00** - Wrap-up (finalize, checkpoint, commit to HF dataset)
4. **55:00 - 60:00** - Quality check (verify no local files, preview next session)

### Processing Estimates

- Court Filing (searchable): ~15 min
- FBI File (scanned/OCR): ~30 min
- Email: ~8 min
- Photo/Image: ~5 min

Target: 2-4 documents per 60-minute session

## Project Structure

```
epstein-doj-analysis/
├── core/                      # Core processing infrastructure
│   ├── document_streamer.py   # PDF streaming (zero local storage)
│   ├── document_processor.py  # Main processing pipeline
│   ├── session_manager.py     # Session state via HF checkpoints
│   └── hf_dataset_client.py   # HF dataset interface
├── extractors/                # Data extraction components
│   ├── entity_extractor.py    # NER with spaCy (95% accuracy) ✅
│   ├── timeline_builder.py    # Timeline reconstruction (Goal #3) ✅
│   ├── code_breaker.py        # Code/alias detection (Goal #1) ✅
│   ├── alias_resolver.py      # Entity disambiguation ✅
│   └── metadata_extractor.py  # Metadata + Bates numbers ✅
├── analyzers/                 # Higher-level analysis
│   ├── network_mapper.py      # Relationship graphs (Goal #2) ✅
│   ├── location_analyzer.py   # Location intelligence (Island/Ranch) ✅
│   └── cross_document_coordinator.py  # Batch correlation ✅
├── utils/                     # Utilities
│   ├── privacy_guard.py       # Privacy verification (CRITICAL)
│   ├── ocr_handler.py         # OCR for scanned docs
│   └── time_tracker.py        # Session time management
├── config/                    # Configuration
│   ├── hf_config.py           # HF dataset config
│   └── url_mappings.py        # DOJ dataset URLs
├── scripts/                   # Operational scripts
│   ├── init_hf_dataset.py     # One-time HF dataset setup
│   ├── run_session.py         # Main entry point
│   ├── resume_session.py      # Resume from checkpoint
│   ├── generate_report.py     # Investigation reports
│   └── validate_analysis_quality.py  # Quality checks
└── tests/                     # Test suite
    ├── test_document_streamer.py
    ├── test_privacy_guard.py
    └── test_full_pipeline.py
```

## Hugging Face Dataset Schema

Private repository: `your-username/epstein-docs-analysis`

### Tables

1. **document_analyses** - Main analysis results (entities, timeline, redactions, metadata)
2. **session_checkpoints** - Session state for resume functionality
3. **entity_index** - Cross-document entity cross-reference
4. **timeline_master** - Master chronological timeline
5. **redaction_patterns** - Pattern analysis
6. **code_dictionary** - Code names & aliases ⭐
7. **network_relationships** - Player network graph ⭐
8. **location_activities** - Location-specific intelligence ⭐
9. **flight_logs** - Travel & movement tracking ⭐

## Success Metrics

### Investigation Goals

- [  ] Comprehensive code name dictionary (100+ terms)
- [  ] Complete network graph (500+ entities)
- [  ] Master timeline (1980s - 2019)
- [  ] Location-specific activity reports (Island, Ranch, etc.)

### Technical Metrics

- [  ] All 12 datasets processed
- [  ] 90%+ entity extraction accuracy
- [  ] 95%+ code name/alias detection
- [  ] 100% privacy verification pass rate

## Contributing

This is a BPR&D research project. For questions or contributions, contact the research team.

## License

Internal BPR&D research project. All rights reserved.
