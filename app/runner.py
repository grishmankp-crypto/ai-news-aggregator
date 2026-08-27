import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import YOUTUBE_CHANNELS
from app.scrapers.youtube import YouTubeScraper, ChannelVideo
from app.scrapers.openai import OpenAIScraper, OpenAIArticle
from app.scrapers.anthropic import AnthropicScraper, AnthropicArticle
from app.scrapers.hackernews import HackerNewsScraper, HackerNewsStory
from app.database.repository import Repository



def run_scrapers(hours: int = 24) -> dict:
    youtube_scraper = YouTubeScraper()
    openai_scraper = OpenAIScraper()
    anthropic_scraper = AnthropicScraper()
    hn_scraper = HackerNewsScraper()
    repo = Repository()
    
    youtube_videos = []
    video_dicts = []
    for channel_id in YOUTUBE_CHANNELS:
        videos = youtube_scraper.get_latest_videos(channel_id, hours=hours)
        youtube_videos.extend(videos)
        video_dicts.extend([
            {
                "video_id": v.video_id,
                "title": v.title,
                "url": v.url,
                "channel_id": channel_id,
                "published_at": v.published_at,
                "description": v.description,
                "transcript": v.transcript
            }
            for v in videos
        ])
    
    openai_articles = openai_scraper.get_articles(hours=hours)
    anthropic_articles = anthropic_scraper.get_articles(hours=hours)
    
    if video_dicts:
        repo.bulk_create_youtube_videos(video_dicts)
    
    if openai_articles:
        article_dicts = [
            {
                "guid": a.guid,
                "title": a.title,
                "url": a.url,
                "published_at": a.published_at,
                "description": a.description,
                "category": a.category
            }
            for a in openai_articles
        ]
        repo.bulk_create_openai_articles(article_dicts)
    
    if anthropic_articles:
        article_dicts = [
            {
                "guid": a.guid,
                "title": a.title,
                "url": a.url,
                "published_at": a.published_at,
                "description": a.description,
                "category": a.category
            }
            for a in anthropic_articles
        ]
        repo.bulk_create_anthropic_articles(article_dicts)
    
    # Scrape Hacker News AI stories
    hn_stories = hn_scraper.get_articles(hours=hours)
    if hn_stories:
        story_dicts = [
            {
                "story_id": s.story_id,
                "title": s.title,
                "url": s.url,
                "points": s.points,
                "num_comments": s.num_comments,
                "author": s.author,
                "published_at": s.published_at,
                "description": s.description
            }
            for s in hn_stories
        ]
        repo.bulk_create_hackernews_stories(story_dicts)
    
    return {
        "youtube": youtube_videos,
        "openai": openai_articles,
        "anthropic": anthropic_articles,
        "hackernews": hn_stories,
    }


if __name__ == "__main__":
    results = run_scrapers(hours=24)
    print(f"YouTube videos: {len(results['youtube'])}")
    print(f"OpenAI articles: {len(results['openai'])}")
    print(f"Anthropic articles: {len(results['anthropic'])}")

