#!/usr/bin/env python3
"""
DDAS Content Orchestrator
Main script that coordinates daily content generation and publishing workflow

This script:
1. Generates content via AI for each account
2. Manages the content queue
3. Publishes to Hive and cross-platforms
4. Logs metrics and performance
"""

import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict
import logging

# Add automation module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from content_generator import (
    ContentGenerator,
    PromptLibrary,
    ContentPrompt,
    AIProvider
)
from hive_publisher import HivePublisher, ContentQueue

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler('ddas_orchestrator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DDASOrchestrator:
    """Main orchestrator for DDAS content pipeline"""

    # 5 Hive accounts
    ACCOUNTS = {
        "ddas-devblog": {
            "name": "Development Blog",
            "posting_key": None,  # TODO: Load from secure config
            "daily_posts": 1,
            "posting_hour": 9,  # 9 AM UTC
            "posting_minute": 0,
            "prompt_source": PromptLibrary.get_dev_blog_prompts
        },
        "ddas-lore": {
            "name": "Lore & Stories",
            "posting_key": None,
            "daily_posts": 1,
            "posting_hour": 12,
            "posting_minute": 0,
            "prompt_source": PromptLibrary.get_lore_prompts
        },
        "ddas-strategy": {
            "name": "Strategy & Guides",
            "posting_key": None,
            "daily_posts": 1,
            "posting_hour": 15,
            "posting_minute": 0,
            "prompt_source": PromptLibrary.get_strategy_prompts
        },
        "ddas-community": {
            "name": "Community Hub",
            "posting_key": None,
            "daily_posts": 1,
            "posting_hour": 18,
            "posting_minute": 0,
            "prompt_source": PromptLibrary.get_community_prompts
        },
        "ddas-news": {
            "name": "News & Updates",
            "posting_key": None,
            "daily_posts": 1,
            "posting_hour": 21,
            "posting_minute": 0,
            "prompt_source": PromptLibrary.get_news_prompts
        }
    }

    def __init__(self, ai_provider: AIProvider = AIProvider.CLAUDE):
        """Initialize orchestrator"""
        self.ai_provider = ai_provider
        self.generator = ContentGenerator(provider=ai_provider)
        self.publishers = {}
        self.content_queue = ContentQueue()
        self.session_stats = {
            "start_time": datetime.now(),
            "content_generated": 0,
            "content_published": 0,
            "errors": 0
        }

        logger.info("=== DDAS Orchestrator Initialized ===")
        logger.info(f"AI Provider: {ai_provider.value}")
        logger.info(f"Accounts configured: {len(self.ACCOUNTS)}")

    def load_publisher_keys(self, config_file: str = "publisher_config.json"):
        """Load Hive publisher keys from secure config"""
        if not os.path.exists(config_file):
            logger.warning(f"Config file not found: {config_file}")
            logger.warning("Publishers will be in dry-run mode")
            return

        try:
            with open(config_file, "r") as f:
                config = json.load(f)

            for account, account_config in self.ACCOUNTS.items():
                if account in config:
                    self.publishers[account] = HivePublisher(
                        account_name=account,
                        posting_key=config[account]["posting_key"],
                        private_key=config[account].get("private_key")
                    )
                    logger.info(f"Loaded publisher for {account}")
                else:
                    logger.warning(f"No config for account: {account}")

        except Exception as e:
            logger.error(f"Error loading publisher config: {str(e)}")

    def generate_daily_content(self) -> Dict:
        """Generate content for all accounts for today"""
        logger.info("=== Starting Daily Content Generation ===")

        results = {
            "timestamp": datetime.now().isoformat(),
            "accounts": {},
            "total_generated": 0,
            "total_errors": 0
        }

        for account_name, account_config in self.ACCOUNTS.items():
            logger.info(f"\nGenerating content for: {account_config['name']}")

            account_results = {
                "account": account_name,
                "generated": [],
                "errors": []
            }

            try:
                # Get prompt library for this account
                prompts = account_config["prompt_source"]()

                # Generate content for each prompt
                for prompt in prompts[:account_config["daily_posts"]]:
                    try:
                        content = self.generator.generate_content(prompt)

                        if content["success"]:
                            account_results["generated"].append(content)
                            self.session_stats["content_generated"] += 1
                            logger.info(f"✓ Generated: {prompt.title}")
                        else:
                            account_results["errors"].append(content)
                            self.session_stats["errors"] += 1
                            logger.error(f"✗ Failed: {prompt.title}")

                    except Exception as e:
                        logger.error(f"Error generating content: {str(e)}")
                        self.session_stats["errors"] += 1
                        account_results["errors"].append({
                            "title": prompt.title,
                            "error": str(e)
                        })

            except Exception as e:
                logger.error(f"Error processing account {account_name}: {str(e)}")
                self.session_stats["errors"] += 1

            results["accounts"][account_name] = account_results
            results["total_generated"] += len(account_results["generated"])
            results["total_errors"] += len(account_results["errors"])

        logger.info(f"\n=== Daily Generation Complete ===")
        logger.info(f"Total Generated: {results['total_generated']}")
        logger.info(f"Total Errors: {results['total_errors']}")

        return results

    def publish_daily_content(self, dry_run: bool = True) -> Dict:
        """Publish generated content to Hive"""
        logger.info(f"\n=== Publishing Content (DRY RUN: {dry_run}) ===")

        results = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "published": [],
            "scheduled": [],
            "errors": []
        }

        for content_item in self.generator.generated_content:
            account = content_item["prompt"]["account"]

            try:
                if account not in self.publishers and not dry_run:
                    logger.warning(f"No publisher for {account}, skipping")
                    continue

                # Create post data
                post_data = {
                    "title": content_item["prompt"]["title"],
                    "content": content_item["content"],
                    "tags": content_item["tags"]
                }

                if dry_run:
                    logger.info(f"[DRY RUN] Would publish to {account}: {post_data['title']}")
                    results["published"].append({
                        "account": account,
                        "title": post_data["title"],
                        "status": "dry_run"
                    })
                else:
                    publisher = self.publishers[account]
                    result = publisher.publish_post(
                        title=post_data["title"],
                        content=post_data["content"],
                        tags=post_data["tags"],
                        dry_run=False
                    )

                    if result["success"]:
                        logger.info(f"✓ Published to {account}")
                        self.session_stats["content_published"] += 1
                        results["published"].append({
                            "account": account,
                            "title": post_data["title"],
                            "status": "published",
                            "url": result.get("url")
                        })
                    else:
                        logger.error(f"✗ Failed to publish to {account}")
                        self.session_stats["errors"] += 1
                        results["errors"].append({
                            "account": account,
                            "title": post_data["title"],
                            "error": result.get("error", "Unknown error")
                        })

            except Exception as e:
                logger.error(f"Error publishing to {account}: {str(e)}")
                self.session_stats["errors"] += 1
                results["errors"].append({
                    "account": account,
                    "error": str(e)
                })

        logger.info(f"\n=== Publishing Complete ===")
        logger.info(f"Published: {len(results['published'])}")
        logger.info(f"Errors: {len(results['errors'])}")

        return results

    def save_session_report(self, gen_results: Dict, pub_results: Dict):
        """Save session report to file"""
        report = {
            "session": self.session_stats,
            "generation": gen_results,
            "publishing": pub_results
        }

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"session_reports/ddas_session_{timestamp}.json"

        # Create directory if needed
        os.makedirs("session_reports", exist_ok=True)

        try:
            with open(filename, "w") as f:
                json.dump(report, f, indent=2)
            logger.info(f"Session report saved: {filename}")
        except Exception as e:
            logger.error(f"Error saving session report: {str(e)}")

    def run_daily_cycle(self, publish: bool = False, dry_run: bool = True):
        """Run complete daily content cycle"""
        logger.info("\n" + "="*60)
        logger.info("DDAS DAILY CONTENT CYCLE")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info("="*60)

        try:
            # Generate content
            gen_results = self.generate_daily_content()

            # Publish content if requested
            if publish:
                pub_results = self.publish_daily_content(dry_run=dry_run)
            else:
                pub_results = {"status": "skipped"}
                logger.info("Publishing skipped (use --publish flag)")

            # Save report
            self.save_session_report(gen_results, pub_results)

            # Print summary
            logger.info("\n" + "="*60)
            logger.info("SESSION SUMMARY")
            logger.info("="*60)
            logger.info(f"Content Generated: {self.session_stats['content_generated']}")
            logger.info(f"Content Published: {self.session_stats['content_published']}")
            logger.info(f"Errors: {self.session_stats['errors']}")
            logger.info(f"Duration: {datetime.now() - self.session_stats['start_time']}")
            logger.info("="*60 + "\n")

        except Exception as e:
            logger.error(f"Critical error in daily cycle: {str(e)}")
            self.session_stats["errors"] += 1


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="DDAS Content Orchestrator - Generate and publish daily content"
    )
    parser.add_argument(
        "--provider",
        choices=["claude", "openai", "ollama"],
        default="claude",
        help="AI provider to use"
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Actually publish to Hive (default: dry-run only)"
    )
    parser.add_argument(
        "--no-dry-run",
        action="store_true",
        help="Don't run in dry-run mode for publishing"
    )
    parser.add_argument(
        "--config",
        default="publisher_config.json",
        help="Path to publisher config file"
    )

    args = parser.parse_args()

    # Initialize orchestrator
    provider = AIProvider(args.provider)
    orchestrator = DDASOrchestrator(ai_provider=provider)

    # Load keys if publishing
    if args.publish:
        orchestrator.load_publisher_keys(args.config)

    # Run daily cycle
    orchestrator.run_daily_cycle(
        publish=args.publish,
        dry_run=not args.no_dry_run
    )


if __name__ == "__main__":
    main()
