# Project DDAS MVP: Distributed Data Acquisition System

**Date:** 2026-02-22
**Owner:** Gemini
**Status:** In Progress
**Priority:** High

## Overview
DDAS aims to build a robust, censorship-resistant data ingestion pipeline. The MVP focuses on parallel scraping of key data sources (Court Listener, Archive.org, niche forums) to feed the BPR&D intelligence engine.

## Architecture

### 1. Ingestion Layer (The Swarm)
- **Puppeteer/Playwright Clusters:** Headless browser instances for dynamic content.
- **API Clients:** Direct integration with public APIs (Reddit, Twitter/X, etc.).
- **Rotating Proxies:** To avoid rate limits and geo-blocking.

### 2. Processing Layer (The Refinery)
- **Text Extraction:** BeautifulSoup/Trafilatura for clean text.
- **Entity Recognition (NER):** Spacy/AbacusAI for extracting Names, Dates, Locations.
- **Deduplication:** MinHash LSH to filter redundant content.

### 3. Storage Layer (The Vault)
- **Raw Data:** S3-compatible object storage (minio/R2).
- **Structured Data:** PostgreSQL/Supabase for metadata.
- **Vector Store:** ChromaDB for semantic search.

## MVP Deliverables (Due Feb 28)
1.  **Scraper Prototype:** A Python script capable of scraping 100+ pages/min from a target site.
2.  **Pipeline Orchestration:** Simple Airflow or Prefect workflow.
3.  **Data Schema:** JSON schema for standardized "Intel Items".

## Risks
- **Anti-Bot Measures:** Cloudflare turnstile, CAPTCHAs. Mitigation: AI solvers.
- **Legal:** Respecting `robots.txt` where applicable, but archiving for public interest.
- **Cost:** Proxy bandwidth can be expensive.

## Next Steps
- Implement `scraper_prototype.py`.
- Set up local Minio instance.
- Define `IntelItem` Pydantic model.
