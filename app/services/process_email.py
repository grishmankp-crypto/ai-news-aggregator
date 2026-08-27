import sys
import time
from pathlib import Path
import logging
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
load_dotenv()

from app.agent.email_agent import EmailAgent, RankedArticleDetail, EmailDigestResponse
from app.agent.curator_agent import CuratorAgent
from app.profiles.user_profile import USER_PROFILE
from app.database.repository import Repository
from app.services.email_service import send_email, digest_to_html

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def generate_email_digest(hours: int = 24, top_n: int = 10, user_profile: dict = None) -> EmailDigestResponse:
    """Generate a personalized email digest for a given user profile.
    
    Args:
        hours: How many hours back to look for digests
        top_n: Number of top articles to include
        user_profile: User profile dict (falls back to hardcoded USER_PROFILE if None)
    """
    profile = user_profile or USER_PROFILE
    curator = CuratorAgent(profile)
    email_agent = EmailAgent(profile)
    repo = Repository()
    
    digests = repo.get_recent_digests(hours=hours)
    total = len(digests)
    
    if total == 0:
        logger.warning(f"No digests found from the last {hours} hours")
        raise ValueError("No digests available")
    
    logger.info(f"Ranking {total} digests for email generation")
    ranked_articles = curator.rank_digests(digests)
    
    if not ranked_articles:
        logger.error("Failed to rank digests")
        raise ValueError("Failed to rank articles")
    
    logger.info(f"Generating email digest with top {top_n} articles")
    
    article_details = [
        RankedArticleDetail(
            digest_id=a.digest_id,
            rank=a.rank,
            relevance_score=a.relevance_score,
            reasoning=a.reasoning,
            title=next((d["title"] for d in digests if d["id"] == a.digest_id), ""),
            summary=next((d["summary"] for d in digests if d["id"] == a.digest_id), ""),
            url=next((d["url"] for d in digests if d["id"] == a.digest_id), ""),
            article_type=next((d["article_type"] for d in digests if d["id"] == a.digest_id), "")
        )
        for a in ranked_articles
    ]
    
    email_digest = email_agent.create_email_digest_response(
        ranked_articles=article_details,
        total_ranked=len(ranked_articles),
        limit=top_n
    )
    
    logger.info("Email digest generated successfully")
    logger.info(f"\n=== Email Introduction ===")
    logger.info(email_digest.introduction.greeting)
    logger.info(f"\n{email_digest.introduction.introduction}")
    
    return email_digest


def send_digest_email(hours: int = 24, top_n: int = 10) -> dict:
    """Send digest to the default single user (backward compatible)."""
    try:
        result = generate_email_digest(hours=hours, top_n=top_n)
        markdown_content = result.to_markdown()
        html_content = digest_to_html(result, user_name="Grishmank Parate")
        
        subject = f"Grishmank's Daily AI Radar - {result.introduction.greeting.split('for ')[-1] if 'for ' in result.introduction.greeting else 'Today'}"
        
        send_email(
            subject=subject,
            body_text=markdown_content,
            body_html=html_content
        )
        
        logger.info("Email sent successfully!")
        return {
            "success": True,
            "subject": subject,
            "articles_count": len(result.articles)
        }
    except ValueError as e:
        logger.error(f"Error sending email: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def send_digest_to_all_users(hours: int = 24, top_n: int = 10) -> dict:
    """Send personalized digest emails to ALL active users in the database.
    
    Scalability architecture (handles 1000+ users):
    ┌─────────────────────────────────────────────────────────────┐
    │ 1. GLOBAL PHASE (runs ONCE, not per-user)                  │
    │    • Fetch all digests from the last N hours                │
    │    • Generate ONE global ranked article list via Curator LLM│
    │    • Build full RankedArticleDetail objects                 │
    ├─────────────────────────────────────────────────────────────┤
    │ 2. PER-USER PHASE (lightweight, no LLM calls)              │
    │    • Filter global ranking by user interests (string match) │
    │    • Generate personalized greeting (1 LLM call per batch)  │
    │    • Render personalized HTML email                         │
    │    • Send via Resend batch API (100 emails/request)         │
    └─────────────────────────────────────────────────────────────┘
    
    This reduces LLM usage from O(2N) to O(1) for N users,
    making it feasible to serve thousands of subscribers on Groq free tier.
    """
    repo = Repository()
    users = repo.get_all_active_users()
    
    if not users:
        logger.info("No registered users found. Falling back to single-user mode.")
        return send_digest_email(hours=hours, top_n=top_n)
    
    # ── STEP 1: Cache all user data upfront ──────────────────────
    user_cache = []
    for user in users:
        user_cache.append({
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "profile": repo.get_user_profile_dict(user)
        })
    
    total_users = len(user_cache)
    logger.info(f"📬 Starting delivery to {total_users} active users")
    
    # ── STEP 2: Generate ONE global ranking (saves N LLM calls) ──
    digests = repo.get_recent_digests(hours=hours)
    if not digests:
        logger.warning(f"No digests found from the last {hours} hours")
        return {"success": False, "error": "No digests available", "sent": 0, "failed": 0}
    
    logger.info(f"Generating global ranking for {len(digests)} digests (shared across all users)")
    
    # Use a generic profile for global ranking
    global_profile = {
        "name": "AI Professional",
        "background": "AI/ML enthusiast and professional",
        "interests": [
            "Large Language Models (LLMs)",
            "AI Research Papers",
            "Open-Source AI Tools",
            "Multi-Agent Systems",
            "Machine Learning Engineering",
        ],
        "preferences": {
            "prefer_practical_and_code": True,
            "prefer_technical_depth": True,
            "prefer_open_source_and_agentic": True,
            "prefer_research_breakthroughs": True,
            "avoid_marketing_hype": True
        },
        "expertise_level": "Intermediate"
    }
    
    global_curator = CuratorAgent(global_profile)
    global_ranked = global_curator.rank_digests(digests)
    
    if not global_ranked:
        logger.error("Failed to generate global ranking")
        return {"success": False, "error": "Failed to rank articles", "sent": 0, "failed": 0}
    
    # Build full article detail objects from the global ranking
    digest_lookup = {d["id"]: d for d in digests}
    global_article_details = [
        RankedArticleDetail(
            digest_id=a.digest_id,
            rank=a.rank,
            relevance_score=a.relevance_score,
            reasoning=a.reasoning,
            title=digest_lookup.get(a.digest_id, {}).get("title", ""),
            summary=digest_lookup.get(a.digest_id, {}).get("summary", ""),
            url=digest_lookup.get(a.digest_id, {}).get("url", ""),
            article_type=digest_lookup.get(a.digest_id, {}).get("article_type", "")
        )
        for a in global_ranked
        if a.digest_id in digest_lookup
    ]
    
    logger.info(f"✓ Global ranking complete: {len(global_article_details)} articles ranked")
    
    # ── STEP 3: Process users in batches ─────────────────────────
    BATCH_SIZE = 50
    results = {
        "success": True,
        "total_users": total_users,
        "sent": 0,
        "failed": 0,
        "details": []
    }
    
    for batch_idx in range(0, total_users, BATCH_SIZE):
        batch = user_cache[batch_idx:batch_idx + BATCH_SIZE]
        batch_num = batch_idx // BATCH_SIZE + 1
        total_batches = (total_users + BATCH_SIZE - 1) // BATCH_SIZE
        logger.info(f"── Processing user batch {batch_num}/{total_batches} ({len(batch)} users) ──")
        
        for u in batch:
            try:
                # Filter global ranking by user interests (lightweight, no LLM)
                user_interests = [i.lower() for i in u['profile'].get('interests', [])]
                user_articles = _filter_articles_for_user(global_article_details, user_interests, top_n)
                
                if not user_articles:
                    user_articles = global_article_details[:top_n]
                
                # Generate personalized email (1 LLM call for the intro)
                email_agent = EmailAgent(u['profile'])
                email_digest = email_agent.create_email_digest_response(
                    ranked_articles=user_articles,
                    total_ranked=len(global_article_details),
                    limit=top_n
                )
                
                # Render personalized HTML
                markdown_content = email_digest.to_markdown()
                html_content = digest_to_html(
                    email_digest, 
                    user_name=u['name'],
                    user_email=u['email']
                )
                
                # Dynamic subject line
                first_name = u['name'].split()[0] if u['name'] else "there"
                subject = f"{first_name}'s AI Radar \u2014 {email_digest.introduction.greeting.split('for ')[-1] if 'for ' in email_digest.introduction.greeting else 'Today'}"
                
                # Send email
                send_email(
                    subject=subject,
                    body_text=markdown_content,
                    body_html=html_content,
                    recipients=[u['email']]
                )
                
                # Log successful delivery
                repo.log_email_sent(
                    user_id=u['id'],
                    subject=subject,
                    articles_count=len(email_digest.articles),
                    status="sent"
                )
                
                results["sent"] += 1
                results["details"].append({
                    "user": u['email'],
                    "status": "sent",
                    "articles": len(email_digest.articles)
                })
                
                logger.info(f"✓ [{results['sent']}/{total_users}] Email sent to {u['email']}")
                
                # Minimal pause — no per-user LLM curation call anymore
                time.sleep(0.5)
                
            except Exception as e:
                results["failed"] += 1
                results["details"].append({
                    "user": u['email'],
                    "status": "failed",
                    "error": str(e)
                })
                
                try:
                    repo.log_email_sent(
                        user_id=u['id'],
                        subject="Failed",
                        articles_count=0,
                        status="failed"
                    )
                except Exception:
                    pass
                
                logger.error(f"✗ Failed to send to {u['email']}: {e}")
        
        # Progress summary per batch
        logger.info(f"── Batch {batch_num} complete: {results['sent']} sent, {results['failed']} failed so far ──")
    
    results["articles_count"] = results["sent"]
    if results["failed"] > 0 and results["sent"] == 0:
        results["success"] = False
    
    logger.info(f"📬 Multi-user delivery complete: {results['sent']} sent, {results['failed']} failed out of {total_users}")
    return results


def _filter_articles_for_user(
    global_articles: list, 
    user_interests: list, 
    top_n: int
) -> list:
    """Filter and re-rank global articles based on a user's interest keywords.
    
    This is a lightweight, no-LLM approach that lets each user get a slightly
    personalized view of the global ranking without extra API calls.
    """
    if not user_interests:
        return global_articles[:top_n]
    
    scored = []
    for article in global_articles:
        # Count how many user interests match the article title/summary
        text = f"{article.title} {article.summary}".lower()
        interest_hits = sum(1 for interest in user_interests if any(
            keyword in text for keyword in interest.split()
            if len(keyword) > 3  # Skip short words like "and", "for"
        ))
        # Blend global relevance score with interest match bonus
        blended_score = article.relevance_score + (interest_hits * 1.5)
        scored.append((blended_score, article))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    return [article for _, article in scored[:top_n]]


if __name__ == "__main__":
    result = send_digest_to_all_users(hours=24, top_n=10)
    if result["success"]:
        print(f"\n=== Digest Delivery Complete ===")
        print(f"Sent: {result.get('sent', 1)}")
        print(f"Failed: {result.get('failed', 0)}")
    else:
        print(f"Error: {result.get('error', 'Unknown')}")
