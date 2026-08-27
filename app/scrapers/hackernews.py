import logging
import requests
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Hacker News Algolia API for searching AI-related stories
HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search"
HN_ITEM_URL = "https://news.ycombinator.com/item?id={}"

# AI-related search queries to rotate through
AI_SEARCH_QUERIES = [
    "artificial intelligence",
    "large language model",
    "GPT",
    "LLM",
    "machine learning",
    "deep learning",
    "neural network",
    "OpenAI",
    "Anthropic",
    "Google DeepMind",
    "AI agent",
    "transformer model",
]


class HackerNewsStory(BaseModel):
    story_id: str
    title: str
    url: str
    points: int
    num_comments: int
    author: str
    published_at: datetime
    description: str = ""


class HackerNewsScraper:
    """Scrapes AI-related stories from Hacker News using the Algolia search API."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "AI-News-Aggregator/2.1"})

    def get_articles(self, hours: int = 72, max_stories: int = 20) -> List[HackerNewsStory]:
        """Fetch recent AI-related stories from Hacker News.

        Args:
            hours: How many hours back to search.
            max_stories: Maximum number of stories to return.

        Returns:
            List of HackerNewsStory objects, deduplicated and sorted by points.
        """
        cutoff_ts = int((datetime.now(timezone.utc) - timedelta(hours=hours)).timestamp())
        seen_ids: set = set()
        all_stories: List[HackerNewsStory] = []

        for query in AI_SEARCH_QUERIES:
            try:
                stories = self._search_stories(query, cutoff_ts, seen_ids)
                all_stories.extend(stories)
            except Exception as e:
                logger.warning(f"HN search failed for query '{query}': {e}")
                continue

        # Sort by points (popularity) and deduplicate
        all_stories.sort(key=lambda s: s.points, reverse=True)
        return all_stories[:max_stories]

    def _search_stories(
        self, query: str, cutoff_ts: int, seen_ids: set
    ) -> List[HackerNewsStory]:
        """Search HN Algolia API for stories matching a query."""
        params = {
            "query": query,
            "tags": "story",
            "numericFilters": f"created_at_i>{cutoff_ts},points>5",
            "hitsPerPage": 10,
        }

        response = self.session.get(HN_SEARCH_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        stories = []
        for hit in data.get("hits", []):
            story_id = str(hit.get("objectID", ""))
            if not story_id or story_id in seen_ids:
                continue
            seen_ids.add(story_id)

            # Use the external URL if available, otherwise link to HN discussion
            url = hit.get("url") or HN_ITEM_URL.format(story_id)
            title = hit.get("title", "Untitled")

            # Build a description from available text
            story_text = hit.get("story_text") or ""
            comment_text = hit.get("comment_text") or ""
            description = story_text or comment_text or f"{title} — Hacker News discussion with {hit.get('num_comments', 0)} comments."

            try:
                published_at = datetime.fromtimestamp(
                    hit.get("created_at_i", 0), tz=timezone.utc
                )
            except (ValueError, OSError):
                published_at = datetime.now(timezone.utc)

            stories.append(
                HackerNewsStory(
                    story_id=story_id,
                    title=title,
                    url=url,
                    points=hit.get("points", 0),
                    num_comments=hit.get("num_comments", 0),
                    author=hit.get("author", "unknown"),
                    published_at=published_at,
                    description=description[:2000],  # Cap description length
                )
            )

        return stories


if __name__ == "__main__":
    scraper = HackerNewsScraper()
    stories = scraper.get_articles(hours=72)
    print(f"Found {len(stories)} AI stories from Hacker News")
    for s in stories[:5]:
        print(f"  [{s.points}pts] {s.title}")
