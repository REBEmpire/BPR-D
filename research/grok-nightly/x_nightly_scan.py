#!/usr/bin/env python3
"""
Nightly X (Twitter) Scan for Grok
---------------------------------
Scans X for high-relevance content related to BPR&D projects and research topics.
Generates a nightly report and a handoff for the morning briefing.

Owner: Grok (Chief) / Implemented by Gemini
"""

import os
import sys
import json
import datetime
import re
import logging
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
TEAM_STATE_FILE = BASE_DIR / "_agents" / "team_state.md"
MOCK_DATA_FILE = GROK_NIGHTLY_DIR / "mock_x_data.json"

# Tweepy Import Fallback
try:
    import tweepy
    HAS_TWEEPY = True
except ImportError:
    HAS_TWEEPY = False
    logger.warning("Tweepy not found. Will use mock mode if API token is missing.")

class ConfigLoader:
    """Loads keywords and topics from project files."""

    def __init__(self):
        self.keywords = set()
        self.topics = {} # Category -> [Keywords]

    def load_all(self):
        self._load_from_charter()
        self._load_from_team_state()
        self._load_from_research_dirs()

        # Add core BPR&D terms
        self.keywords.update(["BPR&D", "AI Agents", "Web3 Gaming", "Splinterlands", "Hive Blockchain"])

        logger.info(f"Loaded {len(self.keywords)} keywords across {len(self.topics)} categories.")
        return list(self.keywords)

    def _load_from_charter(self):
        if not CHARTER_FILE.exists():
            logger.warning(f"Charter file not found: {CHARTER_FILE}")
            return

        with open(CHARTER_FILE, 'r') as f:
            content = f.read()

        # Extract Active Projects
        projects_section = re.search(r"## Active Projects\n(.*?)##", content, re.DOTALL)
        if projects_section:
            projects = re.findall(r"### \d+\. (.*?)\n", projects_section.group(1))
            for p in projects:
                self.keywords.add(p.strip())
                if "Active Projects" not in self.topics:
                    self.topics["Active Projects"] = []
                self.topics["Active Projects"].append(p.strip())

    def _load_from_team_state(self):
        if not TEAM_STATE_FILE.exists():
            logger.warning(f"Team state file not found: {TEAM_STATE_FILE}")
            return

        with open(TEAM_STATE_FILE, 'r') as f:
            content = f.read()

        # Extract Active Projects from Team State
        # Pattern: ### 1. Project Name (Priority: ...)
        projects = re.findall(r"### \d+\. (.*?)\(", content)
        for p in projects:
            self.keywords.add(p.strip())
            if "Team Focus" not in self.topics:
                self.topics["Team Focus"] = []
            self.topics["Team Focus"].append(p.strip())

    def _load_from_research_dirs(self):
        if not RESEARCH_DIR.exists():
            return

        # Scan immediate subdirectories of research/
        for item in RESEARCH_DIR.iterdir():
            if item.is_dir() and not item.name.startswith(('_', '.')) and item.name != "grok-nightly":
                topic_name = item.name.replace('-', ' ').title()
                self.keywords.add(topic_name)
                if "Research Programs" not in self.topics:
                    self.topics["Research Programs"] = []
                self.topics["Research Programs"].append(topic_name)

                # Add subdirectory name as keyword too (e.g. "high-tech")
                self.keywords.add(item.name)


class XClient:
    """Abstracts X (Twitter) access, handling Auth and Mock mode."""

    def __init__(self):
        self.bearer_token = os.environ.get("X_BEARER_TOKEN")
        self.client = None
        self.use_mock = False

        if self.bearer_token and HAS_TWEEPY:
            try:
                self.client = tweepy.Client(bearer_token=self.bearer_token)
                logger.info("Authenticated with X API.")
            except Exception as e:
                logger.error(f"Failed to auth with X API: {e}. Falling back to mock.")
                self.use_mock = True
        else:
            logger.info("No X_BEARER_TOKEN or Tweepy missing. Using mock mode.")
            self.use_mock = True

    def fetch_posts(self, query_keywords: List[str], max_results=10):
        if self.use_mock:
            return self._fetch_mock()

        try:
            # Construct a simple OR query (limit 512 chars for basic tier usually, but v2 allows 512-1024)
            # We'll just take top 5 keywords for the query to be safe for now,
            # in a real app we'd paginate queries.
            # actually, let's just use a broad query "AI OR Crypto OR History" for demo
            query = " OR ".join(query_keywords[:3]) # Very limited for now

            response = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100), # Cap at 100
                tweet_fields=['created_at', 'public_metrics', 'author_id', 'text']
            )

            if not response.data:
                return []

            # Normalize to dict
            tweets = []
            for t in response.data:
                tweets.append({
                    "id": str(t.id),
                    "text": t.text,
                    "created_at": t.created_at.isoformat() if t.created_at else datetime.datetime.now().isoformat(),
                    "author_id": str(t.author_id),
                    "public_metrics": t.public_metrics or {}
                })
            return tweets

        except Exception as e:
            logger.error(f"API Fetch failed: {e}")
            return self._fetch_mock()

    def _fetch_mock(self):
        if not MOCK_DATA_FILE.exists():
            logger.warning("Mock data file missing. Returning empty.")
            return []

        with open(MOCK_DATA_FILE, 'r') as f:
            data = json.load(f)
            return data.get("data", [])


class ContentAnalyzer:
    """Analyzes and scores content."""

    def __init__(self, keywords: List[str], topics: Dict[str, List[str]]):
        self.keywords = [k.lower() for k in keywords]
        self.topics = topics

        # Agent specialty mapping
        self.agent_map = {
            "gemini": ["code", "python", "data", "compliance", "automation", "ai agent"],
            "claude": ["architecture", "strategy", "vision", "philosophy", "ethics"],
            "abacus": ["innovation", "quantum", "physics", "math", "weird"],
            "grok": ["crypto", "web3", "governance", "splinterlands", "hive", "media", "youtube"]
        }

    def analyze(self, tweets: List[Dict]):
        results = []
        for t in tweets:
            text = t.get("text", "").lower()
            score = 0
            matches = []
            suggested_agent = "Team"

            # Keyword matching
            for k in self.keywords:
                if k in text:
                    score += 1
                    matches.append(k)

            # Metric boosting (virality)
            metrics = t.get("public_metrics", {})
            likes = metrics.get("like_count", 0)
            retweets = metrics.get("retweet_count", 0)

            if likes > 1000 or retweets > 200:
                score += 2
                matches.append("high_engagement")
            elif likes > 100:
                score += 1

            # Determine relevance tier
            relevance = "Low"
            if score >= 3:
                relevance = "High"
            elif score >= 1:
                relevance = "Medium"

            # Determine agent
            for agent, terms in self.agent_map.items():
                if any(term in text for term in terms):
                    suggested_agent = agent.capitalize()
                    break

            t_enriched = t.copy()
            t_enriched.update({
                "score": score,
                "relevance": relevance,
                "matches": matches,
                "suggested_agent": suggested_agent
            })
            results.append(t_enriched)

        return sorted(results, key=lambda x: x["score"], reverse=True)


class ReportGenerator:
    """Generates artifacts."""

    def __init__(self, output_dir: Path, handoff_dir: Path):
        self.output_dir = output_dir
        self.handoff_dir = handoff_dir
        self.today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d")

    def save_json(self, data: List[Dict]):
        outfile = self.output_dir / f"x_scan_{self.today}.json"
        with open(outfile, 'w') as f:
            json.dump({"date": self.today, "items": data}, f, indent=2)
        logger.info(f"Saved JSON: {outfile}")

    def save_markdown_report(self, data: List[Dict]):
        outfile = self.output_dir / f"x_scan_{self.today}.md"
        high_rel = [d for d in data if d['relevance'] == 'High']
        med_rel = [d for d in data if d['relevance'] == 'Medium']

        with open(outfile, 'w') as f:
            f.write(f"# Grok Nightly X Scan – {self.today}\n\n")

            f.write("## Executive Summary\n")
            f.write(f"Scanned {len(data)} posts. Found {len(high_rel)} High relevance and {len(med_rel)} Medium relevance items.\n\n")

            f.write("## High-Relevance Hits\n")
            if high_rel:
                for item in high_rel:
                    self._write_item(f, item)
            else:
                f.write("No high relevance items found.\n")
            f.write("\n")

            f.write("## Potential Opportunities (Medium)\n")
            if med_rel:
                for item in med_rel:
                    self._write_item(f, item)
            else:
                f.write("No medium relevance items found.\n")
            f.write("\n")

            f.write("## Raw Data Log\n")
            f.write(f"See JSON artifact: `x_scan_{self.today}.json`\n")

        logger.info(f"Saved Report: {outfile}")

    def save_handoff(self, data: List[Dict]):
        outfile = self.handoff_dir / f"handoff-x-nightly-insights-{self.timestamp}.md"

        # Filter for Handover (Medium+)
        relevant_items = [d for d in data if d['relevance'] in ['High', 'Medium']]

        with open(outfile, 'w') as f:
            f.write(f"# Handoff: Grok Nightly X Insights - {self.today}\n\n")

            if not relevant_items:
                f.write("No critical insights flagged from X scan tonight.\n")
                return

            f.write("## Critical Insights & Opportunities\n")
            for item in relevant_items:
                # Format: - **[Agent]**: [Summary] (Link)
                agent = item.get('suggested_agent', 'Team')
                text_snippet = item['text'][:100].replace('\n', ' ') + "..."
                link = f"https://x.com/user/status/{item['id']}"
                f.write(f"- **{agent}**: {text_snippet} ([View Post]({link}))\n")
                f.write(f"  - *Matches:* {', '.join(item['matches'])}\n")

            f.write("\n## Suggested Actions\n")
            f.write("- Verify sources on High relevance items.\n")
            f.write("- Discuss income opportunities in Morning Sync.\n")

        logger.info(f"Saved Handoff: {outfile}")

    def _write_item(self, f, item):
        f.write(f"### [{item['suggested_agent']}] Tweet {item['id']}\n")
        f.write(f"**Text:** {item['text']}\n\n")
        f.write(f"**Metrics:** Likes: {item['public_metrics'].get('like_count', 0)}, RTs: {item['public_metrics'].get('retweet_count', 0)}\n")
        f.write(f"**Matches:** {', '.join(item['matches'])}\n")
        f.write(f"[Link](https://x.com/user/status/{item['id']})\n\n")


def main():
    logger.info("Starting Grok Nightly X Scan...")

    # Ensure dirs exist
    if not GROK_NIGHTLY_DIR.exists():
        GROK_NIGHTLY_DIR.mkdir(parents=True)
    if not HANDOFFS_DIR.exists():
        HANDOFFS_DIR.mkdir(parents=True)

    # 1. Config
    loader = ConfigLoader()
    keywords = loader.load_all()

    # 2. Fetch
    client = XClient()
    tweets = client.fetch_posts(keywords)
    logger.info(f"Fetched {len(tweets)} posts.")

    # 3. Analyze
    analyzer = ContentAnalyzer(keywords, loader.topics)
    analyzed_data = analyzer.analyze(tweets)

    # 4. Report
    reporter = ReportGenerator(GROK_NIGHTLY_DIR, HANDOFFS_DIR)
    reporter.save_json(analyzed_data)
    reporter.save_markdown_report(analyzed_data)
    reporter.save_handoff(analyzed_data)

    logger.info("Scan Complete.")

if __name__ == "__main__":
    main()
