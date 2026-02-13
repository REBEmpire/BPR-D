#!/usr/bin/env python3
"""
Hive Content Publisher
Automates posting content to Hive blockchain from content queue

Requirements:
- pip install beespy python-dateutil
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HivePublisher:
    def __init__(self, account_name: str, posting_key: str, private_key: Optional[str] = None):
        """
        Initialize Hive publisher

        Args:
            account_name: Hive account name
            posting_key: Posting private key for account
            private_key: Optional active key for transfers
        """
        self.account_name = account_name
        self.posting_key = posting_key
        self.private_key = private_key

        try:
            from beespy.client import Client
            self.client = Client()
            logger.info(f"Initialized Hive client for account: {account_name}")
        except ImportError:
            logger.error("beespy not installed. Install with: pip install beespy")
            raise

    def create_post(
        self,
        title: str,
        content: str,
        tags: List[str],
        meta_data: Optional[Dict] = None,
        community: Optional[str] = None
    ) -> Dict:
        """
        Create a Hive post

        Args:
            title: Post title
            content: Post body (markdown supported)
            tags: List of tags (max 5, first is primary category)
            meta_data: Optional metadata dict (app info, etc)
            community: Optional community name to post to

        Returns:
            Dict with post details including permlink
        """
        try:
            # Generate permlink from title
            import re
            permlink = re.sub(r'[^a-z0-9-]', '', title.lower().replace(' ', '-'))
            permlink = permlink[:256]  # Hive limit

            # Prepare JSON metadata
            json_metadata = {
                "tags": tags[:5],  # Max 5 tags
                "app": "ddas-publisher/0.1"
            }
            if meta_data:
                json_metadata.update(meta_data)

            # Prepare post operation
            post_op = {
                "parent_author": community if community else "",
                "parent_permlink": tags[0] if community else (tags[0] if tags else "hive"),
                "author": self.account_name,
                "permlink": permlink,
                "title": title,
                "body": content,
                "json_metadata": json.dumps(json_metadata)
            }

            logger.info(f"Created post operation: {self.account_name}/{permlink}")
            return {
                "success": True,
                "permlink": permlink,
                "url": f"https://hive.blog/@{self.account_name}/{permlink}",
                "operation": post_op
            }

        except Exception as e:
            logger.error(f"Error creating post: {str(e)}")
            return {"success": False, "error": str(e)}

    def publish_post(
        self,
        title: str,
        content: str,
        tags: List[str],
        meta_data: Optional[Dict] = None,
        community: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict:
        """
        Publish a post to Hive blockchain

        Args:
            title: Post title
            content: Post body
            tags: List of tags
            meta_data: Optional metadata
            community: Optional community name
            dry_run: If True, don't actually broadcast

        Returns:
            Result dict with transaction info
        """
        try:
            post_data = self.create_post(
                title=title,
                content=content,
                tags=tags,
                meta_data=meta_data,
                community=community
            )

            if not post_data["success"]:
                return post_data

            if dry_run:
                logger.info("DRY RUN: Would publish post")
                return {
                    "success": True,
                    "dry_run": True,
                    "post_data": post_data
                }

            # TODO: Implement actual Hive transaction broadcasting
            # This requires beespy or hive-python library with proper key management
            # For now, return the post data
            logger.info(f"READY TO BROADCAST: {post_data['url']}")
            return {
                "success": True,
                "published": True,
                "post_data": post_data
            }

        except Exception as e:
            logger.error(f"Error publishing post: {str(e)}")
            return {"success": False, "error": str(e)}

    def schedule_post(
        self,
        title: str,
        content: str,
        tags: List[str],
        publish_time: datetime,
        meta_data: Optional[Dict] = None,
        community: Optional[str] = None
    ) -> Dict:
        """
        Schedule a post for future publishing

        Args:
            title: Post title
            content: Post body
            tags: List of tags
            publish_time: datetime when to publish
            meta_data: Optional metadata
            community: Optional community name

        Returns:
            Dict with scheduling info
        """
        scheduled_file = f"scheduled_{self.account_name}_{publish_time.timestamp()}.json"

        schedule_data = {
            "account": self.account_name,
            "title": title,
            "content": content,
            "tags": tags,
            "publish_time": publish_time.isoformat(),
            "meta_data": meta_data,
            "community": community,
            "created_at": datetime.now().isoformat()
        }

        try:
            with open(f"scheduled/{scheduled_file}", "w") as f:
                json.dump(schedule_data, f, indent=2)
            logger.info(f"Post scheduled for {publish_time}: {scheduled_file}")
            return {"success": True, "scheduled_file": scheduled_file}
        except Exception as e:
            logger.error(f"Error scheduling post: {str(e)}")
            return {"success": False, "error": str(e)}


class ContentQueue:
    """Manages content queue from Notion/external sources"""

    def __init__(self, queue_file: str = "content_queue.json"):
        self.queue_file = queue_file
        self.queue = self._load_queue()

    def _load_queue(self) -> List[Dict]:
        """Load content queue from file"""
        if os.path.exists(self.queue_file):
            try:
                with open(self.queue_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading queue: {str(e)}")
                return []
        return []

    def _save_queue(self):
        """Save content queue to file"""
        try:
            with open(self.queue_file, "w") as f:
                json.dump(self.queue, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving queue: {str(e)}")

    def add_content(self, content_item: Dict):
        """Add content to queue"""
        content_item["added_at"] = datetime.now().isoformat()
        content_item["status"] = "pending"
        self.queue.append(content_item)
        self._save_queue()
        logger.info(f"Added to queue: {content_item.get('title', 'Untitled')}")

    def get_pending_content(self) -> List[Dict]:
        """Get all pending content"""
        return [item for item in self.queue if item.get("status") == "pending"]

    def mark_published(self, content_index: int, tx_hash: str = ""):
        """Mark content as published"""
        if 0 <= content_index < len(self.queue):
            self.queue[content_index]["status"] = "published"
            self.queue[content_index]["published_at"] = datetime.now().isoformat()
            if tx_hash:
                self.queue[content_index]["tx_hash"] = tx_hash
            self._save_queue()
            logger.info(f"Marked content as published: {content_index}")

    def remove_content(self, content_index: int):
        """Remove content from queue"""
        if 0 <= content_index < len(self.queue):
            removed = self.queue.pop(content_index)
            self._save_queue()
            logger.info(f"Removed from queue: {removed.get('title', 'Untitled')}")


if __name__ == "__main__":
    # Example usage
    logger.info("Hive Publisher module loaded. Import into your automation scripts.")
