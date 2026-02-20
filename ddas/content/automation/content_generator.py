#!/usr/bin/env python3
"""
DDAS Content Generator
Orchestrates AI content generation and formatting for multiple Hive accounts

Supports:
- Multiple AI backends (Claude, OpenAI, Local Ollama)
- Batch content generation
- Image generation integration
- Content review workflow
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """Supported AI providers"""
    CLAUDE = "claude"
    OPENAI = "openai"
    OLLAMA = "ollama"  # Local open-source
    CUSTOM = "custom"


@dataclass
class ContentPrompt:
    """A prompt for AI content generation"""
    account: str  # Target Hive account
    content_type: str  # 'article', 'story', 'guide', 'news'
    title: str
    topic: str
    tags: List[str]
    tone: str  # 'technical', 'narrative', 'educational', 'casual'
    length: str  # 'short' (300-500), 'medium' (500-1000), 'long' (1000-2000)
    include_image: bool = True
    image_prompt: Optional[str] = None
    additional_instructions: Optional[str] = None


class ContentGenerator:
    """Main content generation orchestrator"""

    def __init__(self, provider: AIProvider = AIProvider.CLAUDE):
        self.provider = provider
        self.generated_content = []
        self.client = self._initialize_client()

    def _initialize_client(self):
        """Initialize AI client based on provider"""
        try:
            if self.provider == AIProvider.CLAUDE:
                # Use Claude SDK
                logger.info("Initializing Claude provider")
                from anthropic import Anthropic
                api_key = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("CLAUDE_API_KEY or ANTHROPIC_API_KEY environment variable required")
                return Anthropic(api_key=api_key)

            elif self.provider == AIProvider.OPENAI:
                logger.info("Initializing OpenAI provider")
                import openai
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY environment variable required")
                client = openai.OpenAI(api_key=api_key)
                return client

            elif self.provider == AIProvider.OLLAMA:
                logger.info("Initializing Ollama provider")
                # Ollama runs locally, requires local setup
                import requests
                # Assume Ollama is running on localhost:11434
                return {"base_url": "http://localhost:11434", "session": requests.Session()}

            else:
                logger.warning("No AI provider initialized")
                return None

        except Exception as e:
            logger.error(f"Error initializing AI provider: {str(e)}")
            return None

    def generate_content(self, prompt: ContentPrompt) -> Dict:
        """
        Generate content based on prompt

        Args:
            prompt: ContentPrompt with generation parameters

        Returns:
            Dict with generated content and metadata
        """
        result = {
            "success": False,
            "prompt": prompt.__dict__,
            "generated_at": datetime.now().isoformat(),
            "content": "",
            "image_prompt": "",
            "tags": prompt.tags
        }

        try:
            # Build system message based on content type
            system_prompt = self._build_system_prompt(prompt.content_type, prompt.tone)

            # Build user message
            user_message = self._build_user_message(prompt)

            logger.info(f"Generating {prompt.content_type} for {prompt.account}: {prompt.title}")

            # Generate content using the appropriate AI provider
            if self.client is None:
                raise ValueError(f"No client available for provider {self.provider}")

            generated_content = self._call_ai_api(system_prompt, user_message)

            # Load and apply template if available
            template_path = self._get_template_path(prompt.content_type)
            if os.path.exists(template_path):
                result["content"] = self._apply_template(generated_content, prompt, template_path)
            else:
                result["content"] = generated_content

            if prompt.include_image:
                result["image_prompt"] = prompt.image_prompt or f"Illustration for: {prompt.title}"

            result["success"] = True
            self.generated_content.append(result)
            logger.info(f"Content generated successfully")

            return result

        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            result["error"] = str(e)
            return result

    def _build_system_prompt(self, content_type: str, tone: str) -> str:
        """Build system prompt based on content type and tone"""
        tone_guides = {
            "technical": "Use precise technical language, explain concepts clearly, include code examples where relevant.",
            "narrative": "Tell an engaging story, use descriptive language, create emotional connection with reader.",
            "educational": "Teach the reader step-by-step, use examples, explain why things matter, be patient and clear.",
            "casual": "Write conversationally, use friendly language, relate to audience, be concise and engaging."
        }

        type_guides = {
            "article": "Write a well-structured article with introduction, main points, and conclusion.",
            "story": "Write an engaging narrative or story excerpt.",
            "guide": "Write a how-to guide with clear steps and tips.",
            "news": "Write a news-style update or announcement.",
            "devlog": "Write a development log entry discussing progress, challenges, and next steps."
        }

        system_msg = f"""You are a content writer for the Decentralized Digital Arts Studio (DDAS).
Your writing is intended for the Hive blockchain community.
Maintain a professional yet approachable tone.

Content Type: {content_type}
Tone: {tone}

{type_guides.get(content_type, '')}
{tone_guides.get(tone, '')}

Keep content well-formatted with markdown, use headers appropriately, and include relevant details."""

        return system_msg

    def _build_user_message(self, prompt: ContentPrompt) -> str:
        """Build user message from prompt"""
        msg = f"""Write a {prompt.content_type} titled: "{prompt.title}"

Topic: {prompt.topic}
Content Type: {prompt.content_type}
Length: {prompt.length}
Target Audience: Hive community members interested in gaming and digital arts

Tags to include: {', '.join(prompt.tags)}

"""
        if prompt.additional_instructions:
            msg += f"\nSpecial instructions: {prompt.additional_instructions}\n"

        msg += "\nWrite the content now:"

        return msg

    def generate_batch(self, prompts: List[ContentPrompt]) -> List[Dict]:
        """Generate content for multiple prompts"""
        logger.info(f"Starting batch generation of {len(prompts)} items")
        results = []

        for i, prompt in enumerate(prompts):
            logger.info(f"Generating {i+1}/{len(prompts)}")
            result = self.generate_content(prompt)
            results.append(result)

        logger.info(f"Batch generation complete. Success: {sum(1 for r in results if r['success'])}/{len(results)}")
        return results

    def _call_ai_api(self, system_prompt: str, user_message: str) -> str:
        """Call the appropriate AI API based on provider"""
        try:
            if self.provider == AIProvider.CLAUDE:
                response = self.client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=4000,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_message}]
                )
                return response.content[0].text

            elif self.provider == AIProvider.OPENAI:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=4000,
                    temperature=0.7
                )
                return response.choices[0].message.content

            elif self.provider == AIProvider.OLLAMA:
                # Ollama API call
                payload = {
                    "model": "mistral",  # or whatever model is available
                    "prompt": f"{system_prompt}\n\n{user_message}",
                    "stream": False
                }
                response = self.client["session"].post(
                    f"{self.client['base_url']}/api/generate",
                    json=payload
                )
                response.raise_for_status()
                return response.json()["response"]

            else:
                raise ValueError(f"Unsupported provider: {self.provider}")

        except Exception as e:
            logger.error(f"AI API call failed: {str(e)}")
            raise

    def _get_template_path(self, content_type: str) -> str:
        """Get template path based on content type"""
        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        template_map = {
            "devlog": "devblog_template.md",
            "article": f"{content_type}_template.md",  # generic article template
            "story": "lore_template.md",
            "guide": "strategy_template.md",
            "news": "news_template.md"
        }
        template_name = template_map.get(content_type, "devblog_template.md")
        return os.path.join(template_dir, template_name)

    def _apply_template(self, generated_content: str, prompt: ContentPrompt, template_path: str) -> str:
        """Apply template to generated content"""
        try:
            with open(template_path, "r") as f:
                template = f.read()

            # Replace placeholders in template
            replacements = {
                "[DATE]": datetime.now().strftime("%Y-%m-%d"),
                "[TITLE]": prompt.title,
                "[CONTENT]": generated_content,
                "[ACCOUNT]": prompt.account,
                "[TYPE]": prompt.content_type,
                "[TOPIC]": prompt.topic,
                "[TAGS]": ", ".join(prompt.tags),
                "[Game Status]": "Splinterlands Civ | Slingerlands RPG",
                "[Version]": "0.1.0-alpha",
                "[Repository]": "https://github.com/REBEmpire/BPR-D",
                "[Discord]": "https://discord.gg/ddas"
            }

            result = template
            for placeholder, value in replacements.items():
                result = result.replace(placeholder, value)

            return result

        except Exception as e:
            logger.warning(f"Error applying template: {str(e)}, using raw content")
            return generated_content

    def save_generated_content(self, output_dir: str = "generated_content"):
        """Save all generated content to JSON files"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for content in self.generated_content:
            timestamp = content["generated_at"].replace(":", "-").replace(".", "-")
            filename = f"{content['prompt']['account']}_{timestamp}.json"
            filepath = os.path.join(output_dir, filename)

            try:
                with open(filepath, "w") as f:
                    json.dump(content, f, indent=2)
                logger.info(f"Saved: {filepath}")
            except Exception as e:
                logger.error(f"Error saving content: {str(e)}")


class PromptLibrary:
    """Pre-built prompts for each account type"""

    @staticmethod
    def get_dev_blog_prompts() -> List[ContentPrompt]:
        """Prompts for Dev Blog account"""
        return [
            ContentPrompt(
                account="ddas-devblog",
                content_type="devlog",
                title="Weekly Development Update",
                topic="Recent progress on game development",
                tags=["development", "gamedev", "update"],
                tone="technical",
                length="medium"
            ),
            ContentPrompt(
                account="ddas-devblog",
                content_type="article",
                title="Architecture Decision: Choosing Our Game Engine",
                topic="Technical decision-making process",
                tags=["development", "architecture", "godot"],
                tone="technical",
                length="long"
            )
        ]

    @staticmethod
    def get_lore_prompts() -> List[ContentPrompt]:
        """Prompts for Lore account"""
        return [
            ContentPrompt(
                account="ddas-lore",
                content_type="story",
                title="The Tale of [Character Name]",
                topic="Character backstory from Splinterlands/Slingerlands",
                tags=["lore", "storytelling", "splinterlands"],
                tone="narrative",
                length="long"
            ),
            ContentPrompt(
                account="ddas-lore",
                content_type="article",
                title="Exploring the Splinterlands Universe",
                topic="World-building and setting explanation",
                tags=["lore", "worldbuilding", "splinterlands"],
                tone="educational",
                length="medium"
            )
        ]

    @staticmethod
    def get_strategy_prompts() -> List[ContentPrompt]:
        """Prompts for Strategy account"""
        return [
            ContentPrompt(
                account="ddas-strategy",
                content_type="guide",
                title="Beginner's Guide to Deck Building",
                topic="How to build effective decks for Splinterlands",
                tags=["strategy", "guide", "tips"],
                tone="educational",
                length="long"
            ),
            ContentPrompt(
                account="ddas-strategy",
                content_type="article",
                title="Meta Analysis: Current Top Strategies",
                topic="Analysis of winning strategies in competitive play",
                tags=["strategy", "analysis", "competitive"],
                tone="technical",
                length="medium"
            )
        ]

    @staticmethod
    def get_community_prompts() -> List[ContentPrompt]:
        """Prompts for Community account"""
        return [
            ContentPrompt(
                account="ddas-community",
                content_type="article",
                title="Community Spotlight: [Player Name]",
                topic="Feature a community member and their achievements",
                tags=["community", "spotlight", "players"],
                tone="casual",
                length="medium"
            ),
            ContentPrompt(
                account="ddas-community",
                content_type="article",
                title="Weekly Community Roundup",
                topic="Highlight community discussions and achievements",
                tags=["community", "roundup", "news"],
                tone="casual",
                length="medium"
            )
        ]

    @staticmethod
    def get_news_prompts() -> List[ContentPrompt]:
        """Prompts for News account"""
        return [
            ContentPrompt(
                account="ddas-news",
                content_type="news",
                title="DDAS Project Milestone Reached",
                topic="Major project announcement",
                tags=["news", "announcement", "milestone"],
                tone="professional",
                length="medium"
            ),
            ContentPrompt(
                account="ddas-news",
                content_type="news",
                title="Weekly Gaming News Summary",
                topic="Digest of relevant gaming news",
                tags=["news", "gaming", "roundup"],
                tone="professional",
                length="medium"
            )
        ]


if __name__ == "__main__":
    logger.info("Content Generator module loaded.")
