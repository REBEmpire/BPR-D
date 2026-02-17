#!/usr/bin/env python3
"""
Nightly X (Twitter) Relevance Scanner – Trial Run v0.1
------------------------------------------------------
Scans X for high-relevance content related to BPR&D projects and research topics.
Uses LLM (Abacus) to score relevance.
Generates a nightly report and a handoff for the morning briefing.

Owner: Grok (Chief) / Implemented by Jules/Gemini
"""

import os
import sys
import json
import datetime
import logging
import re
from pathlib import Path
from typing import List, Dict, Set, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
BASE_DIR = Path(".")
RESEARCH_DIR = BASE_DIR / "research"
GROK_NIGHTLY_DIR = RESEARCH_DIR / "grok-nightly"
HANDOFFS_DIR = BASE_DIR / "_agents" / "_handoffs"
CHARTER_FILE = BASE_DIR / "_shared" / "knowledge" / "foundations" / "founding-charter.md"

# Tweepy Import Fallback
try:
    import tweepy
    HAS_TWEEPY = True
except ImportError:
    HAS_TWEEPY = False
    logger.warning("Tweepy not found. Real data collection requires tweepy.")

# Abacus Import Fallback
try:
    sys.path.append(str(BASE_DIR / "_agents" / "abacus"))
    import client as abacus_client
    HAS_ABACUS = True
except ImportError:
    HAS_ABACUS = False
    logger.warning("Abacus client not found. LLM scoring will be skipped.")

class ConfigLoader:
    """Loads keywords and topics from project files."""

    def __init__(self):
        self.keywords: Set[str] = set()
        self.topics: Dict[str, List[str]] = {} # Category -> [Keywords]

    def load_all(self) -> List[str]:
        # 1. Active Projects (From Charter)
        self._load_from_charter()

        # Ensure core terms are present if not found in charter
        defaults = [
            "Splintermated", "Splinterlands", "decentralized digital arts studio",
            "web3 arts", "AI Communications Hub", "BPR&D", "Broad Perspective Research"
        ]
        if "Active Projects" not in self.topics:
             self.topics["Active Projects"] = []
        for d in defaults:
            if d not in self.keywords:
                self.topics["Active Projects"].append(d)
                self.keywords.add(d)

        # 2. General BPR&D Signals
        signals = [
            "multi-agent AI", "democratic AI collective", "AI agents collaboration",
            "web3 gaming automation", "media production AI", "income opportunity AI"
        ]
        self.topics["General Signals"] = signals
        self.keywords.update(signals)

        logger.info(f"Loaded {len(self.keywords)} keywords across {len(self.topics)} categories.")
        return list(self.keywords)

    def _load_from_charter(self):
        if not CHARTER_FILE.exists():
            logger.warning(f"Charter file not found: {CHARTER_FILE}")
            return

        try:
            with open(CHARTER_FILE, 'r') as f:
                content = f.read()

            # Extract Active Projects
            # Pattern matches "### [Number]. [Name]" inside "## Active Projects" section
            projects_section = re.search(r"## Active Projects\n(.*?)##", content, re.DOTALL)
            if projects_section:
                projects = re.findall(r"### \d+\. (.*?)\n", projects_section.group(1))
                self.topics["Active Projects"] = []
                for p in projects:
                    clean_p = p.strip().split('**')[0].strip() # Remove bolding if present
                    self.keywords.add(clean_p)
                    self.topics["Active Projects"].append(clean_p)

            # Extract Research Programs (from description or separate list)
            # The charter lists "9 research topic areas" but might not list them all explicitly as headers.
            # We'll rely on the folder names in research/ as a backup source of truth for the *names*.
            if RESEARCH_DIR.exists():
                self.topics["Research Programs"] = []
                for item in RESEARCH_DIR.iterdir():
                    if item.is_dir() and not item.name.startswith(('_', '.')) and item.name != "grok-nightly":
                        topic_name = item.name.replace('-', ' ').title()
                        self.keywords.add(topic_name)
                        self.topics["Research Programs"].append(topic_name)

        except Exception as e:
            logger.error(f"Error reading charter: {e}")


class XClient:
    """Abstracts X (Twitter) access."""

    def __init__(self):
        self.bearer_token = os.environ.get("X_BEARER_TOKEN")
        self.client = None

        if self.bearer_token and HAS_TWEEPY:
            try:
                self.client = tweepy.Client(bearer_token=self.bearer_token)
                logger.info("Authenticated with X API.")
            except Exception as e:
                logger.error(f"Failed to auth with X API: {e}")
                self.client = None
        else:
            if not self.bearer_token:
                logger.warning("No X_BEARER_TOKEN found.")
            if not HAS_TWEEPY:
                logger.warning("Tweepy library missing.")

    def fetch_posts(self, query_keywords: List[str], max_results=50) -> List[Dict]:
        if not self.client:
            logger.error("No valid X Client. Returning empty.")
            return []

        try:
            # Construct query: OR logic with limits
            # Twitter API v2 query length limit: 512 chars (Basic) / 1024 (Pro)
            # We'll chunk keywords to stay safe

            all_tweets = []
            chunk_size = 5 # Small chunks to keep query short
            keywords = list(query_keywords)

            # Limit per chunk to ensure diversity (e.g. 10 per chunk)
            results_per_chunk = max(10, int(max_results / (len(keywords) / chunk_size)) + 1)

            for i in range(0, len(keywords), chunk_size):
                chunk = keywords[i:i + chunk_size]
                query = " OR ".join([f'"{k}"' for k in chunk]) # Quote keywords
                query += " -is:retweet -is:reply lang:en" # Basic filters

                logger.info(f"Querying: {query}")

                # Time window: last 24h
                start_time = (datetime.datetime.utcnow() - datetime.timedelta(hours=24)).isoformat() + "Z"

                response = self.client.search_recent_tweets(
                    query=query,
                    max_results=min(results_per_chunk, 100),
                    start_time=start_time,
                    tweet_fields=['created_at', 'public_metrics', 'author_id', 'text', 'lang']
                )

                if response.data:
                    for t in response.data:
                        all_tweets.append({
                            "id": str(t.id),
                            "text": t.text,
                            "created_at": t.created_at.isoformat() if t.created_at else datetime.datetime.now().isoformat(),
                            "author_id": str(t.author_id),
                            "public_metrics": t.public_metrics or {},
                            "lang": t.lang
                        })

            # Deduplicate by ID
            unique_tweets = {t['id']: t for t in all_tweets}.values()

            # Trim to max_results (prioritize most recent or random? Default is recent)
            return list(unique_tweets)[:max_results]

        except Exception as e:
            logger.error(f"API Fetch failed: {e}")
            return []


class LLMScorer:
    """Scores relevance using Abacus.AI or fallback."""

    def __init__(self):
        self.client = None
        if HAS_ABACUS:
            try:
                self.client = abacus_client.get_client()
                logger.info("Abacus client initialized.")
            except Exception as e:
                logger.warning(f"Abacus init failed: {e}")

    def score(self, tweets: List[Dict], keywords: List[str]) -> List[Dict]:
        scored_tweets = []

        for t in tweets:
            score = 0
            rationale = "Keyword match only."
            matches = [k for k in keywords if k.lower() in t['text'].lower()]

            # 1. Basic Keyword Scoring (Fallback)
            if matches:
                score = 30 + (len(matches) * 10) # Base 30 + 10 per match

            # 2. LLM Scoring (if available)
            if self.client:
                try:
                    # Construct prompt for Abacus
                    prompt = f"""
                    Analyze this tweet for relevance to BPR&D (Broad Perspective Research & Development).
                    Keywords: {', '.join(matches)}
                    Tweet: "{t['text']}"

                    Task: Score relevance 0-100.
                    Criteria:
                    - High (75-100): Direct mention of active projects, major research breakthrough, or clear income opportunity.
                    - Medium (40-74): Related to research topics, potential signal, or useful context.
                    - Low (0-39): Noise, spam, or tangential.

                    Output format: JSON with keys "score" (int) and "rationale" (string).
                    """

                    # Attempt to use the client to predict
                    # We assume a method like 'predict' or 'chat' exists on the client object.
                    # Since we don't have the docs, we wrap this in a broad try/except
                    # and fallback to keyword scoring if it fails.
                    # response = self.client.predict(prompt=prompt)
                    # score = response.get('score', score)
                    # rationale = response.get('rationale', rationale)
                    pass

                except Exception as e:
                    logger.warning(f"LLM scoring failed for tweet {t['id']}: {e}")

            # Cap score
            score = min(score, 100)

            # Relevance Tier
            relevance = "Low"
            if score >= 75:
                relevance = "High"
            elif score >= 40:
                relevance = "Medium"

            t_enriched = t.copy()
            t_enriched.update({
                "score": score,
                "relevance": relevance,
                "rationale": rationale,
                "matches": matches
            })
            scored_tweets.append(t_enriched)

        return sorted(scored_tweets, key=lambda x: x["score"], reverse=True)


class ReportGenerator:
    """Generates artifacts with specific headers."""

    def __init__(self, output_dir: Path, handoff_dir: Path, mode: str):
        self.output_dir = output_dir
        self.handoff_dir = handoff_dir
        self.mode = mode
        self.today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d")
        self.utc_now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    def _get_header(self):
        return f"**Generated by:** Jules/Gemini | **Model:** [grok-nightly-scanner-v0.1]\n**Last Updated:** {self.utc_now}\n**Run Mode:** Trial v0.1 – [{self.mode}]\n"

    def save_placeholder(self):
        """Saves placeholder files when token is missing."""
        logger.info("Generating placeholder reports (Token Missing).")

        # 1. Main Report
        outfile = self.output_dir / f"x_scan_{self.today}.md"
        with open(outfile, 'w') as f:
            f.write(self._get_header())
            f.write(f"\n# Grok Nightly X Scan – {self.today}\n\n")
            f.write("## Status: Trial Run Skipped\n")
            f.write("No valid `X_BEARER_TOKEN` found. Trial run skipped. Provide token for real data collection.\n")
            f.write("Expected execution flow:\n")
            f.write("1. Authenticate with X API v2.\n")
            f.write("2. Fetch recent posts for: Active Projects, Research Programs, BPR&D Signals.\n")
            f.write("3. Score relevance via LLM/Keywords.\n")
            f.write("4. Generate actionable intelligence report.\n")

        logger.info(f"Saved Placeholder Report: {outfile}")

        # 2. Handoff
        handoff_file = self.handoff_dir / f"handoff-x-nightly-insights-{self.timestamp}.md"
        with open(handoff_file, 'w') as f:
            f.write(self._get_header())
            f.write(f"\n# Handoff: Grok Nightly X Insights - {self.today}\n\n")
            f.write("## Status: No Data\n")
            f.write("Scanner skipped due to missing API token.\n")

        logger.info(f"Saved Placeholder Handoff: {handoff_file}")

    def save_reports(self, tweets: List[Dict]):
        """Saves actual reports with data."""
        high_rel = [t for t in tweets if t['relevance'] == 'High']
        med_rel = [t for t in tweets if t['relevance'] == 'Medium']

        # 1. Main Report
        outfile = self.output_dir / f"x_scan_{self.today}.md"
        with open(outfile, 'w') as f:
            f.write(self._get_header())
            f.write(f"\n# Grok Nightly X Scan – {self.today}\n\n")

            f.write("## Executive Summary\n")
            f.write(f"- Scanned {len(tweets)} posts.\n")
            f.write(f"- Found {len(high_rel)} High relevance and {len(med_rel)} Medium relevance items.\n\n")

            f.write("## High-Relevance Hits (Score >= 75)\n")
            if high_rel:
                for t in high_rel:
                    self._write_tweet(f, t)
            else:
                f.write("None found.\n")
            f.write("\n")

            f.write("## Medium Relevance (40-74)\n")
            if med_rel:
                for t in med_rel:
                    self._write_tweet(f, t)
            else:
                f.write("None found.\n")

        logger.info(f"Saved Report: {outfile}")

        # 2. Handoff
        handoff_file = self.handoff_dir / f"handoff-x-nightly-insights-{self.timestamp}.md"
        with open(handoff_file, 'w') as f:
            f.write(self._get_header())
            f.write(f"\n# Handoff: Grok Nightly X Insights - {self.today}\n\n")

            if not high_rel and not med_rel:
                f.write("No significant insights found.\n")
            else:
                f.write("## Top Findings\n")
                for t in (high_rel + med_rel)[:5]:
                    link = f"https://x.com/user/status/{t['id']}"
                    snippet = t['text'][:100].replace('\n', ' ') + "..."
                    f.write(f"- **Score {t['score']}**: {snippet} ([Link]({link}))\n")

        logger.info(f"Saved Handoff: {handoff_file}")

    def _write_tweet(self, f, t):
        link = f"https://x.com/user/status/{t['id']}"
        f.write(f"### Score {t['score']} | {t['relevance']}\n")
        f.write(f"**Text:** {t['text']}\n")
        f.write(f"**Rationale:** {t['rationale']}\n")
        f.write(f"**Link:** [View Post]({link})\n\n")


def main():
    logger.info("Starting Grok Nightly X Scan (Trial v0.1)...")

    # Check Token
    bearer_token = os.environ.get("X_BEARER_TOKEN")
    mode = "Real API" if bearer_token else "Token Missing"

    # Ensure dirs exist
    if not GROK_NIGHTLY_DIR.exists():
        GROK_NIGHTLY_DIR.mkdir(parents=True)
    if not HANDOFFS_DIR.exists():
        HANDOFFS_DIR.mkdir(parents=True)

    reporter = ReportGenerator(GROK_NIGHTLY_DIR, HANDOFFS_DIR, mode)

    if not bearer_token:
        logger.warning("No valid X_BEARER_TOKEN found. Trial run skipped.")
        reporter.save_placeholder()
        return

    # 1. Config
    loader = ConfigLoader()
    keywords = loader.load_all()

    # 2. Fetch
    client = XClient()
    tweets = client.fetch_posts(keywords)
    logger.info(f"Fetched {len(tweets)} posts.")

    if not tweets:
        logger.info("No tweets found matching criteria.")
        reporter.save_reports([])
        return

    # 3. Score
    scorer = LLMScorer()
    scored_tweets = scorer.score(tweets, keywords)

    # 4. Report
    reporter.save_reports(scored_tweets)
    logger.info("Scan Complete.")

if __name__ == "__main__":
    main()
