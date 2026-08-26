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
    
    Flow:
    1. Get all active users from the database
    2. For each user, generate a personalized ranked digest using their profile
    3. Send the email via Resend (or Gmail fallback)
    4. Log the email delivery status
    
    Falls back to single-user mode if no users are registered.
    """
    repo = Repository()
    users = repo.get_all_active_users()
    
    if not users:
        logger.info("No registered users found. Falling back to single-user mode.")
        return send_digest_email(hours=hours, top_n=top_n)
    
    # Cache user data upfront so we don't depend on a live DB connection later.
    # Neon free tier closes idle connections after ~5min, and Groq rate limiting
    # can make the loop take 15+ minutes, causing "server closed connection" errors.
    user_cache = []
    for user in users:
        user_cache.append({
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "profile": repo.get_user_profile_dict(user)
        })
    
    logger.info(f"Sending personalized digests to {len(user_cache)} active users")
    
    results = {
        "success": True,
        "total_users": len(user_cache),
        "sent": 0,
        "failed": 0,
        "details": []
    }
    
    for u in user_cache:
        try:
            logger.info(f"Generating digest for {u['name']} ({u['email']})")
            
            # Generate personalized digest
            email_digest = generate_email_digest(
                hours=hours, 
                top_n=top_n, 
                user_profile=u['profile']
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
            subject = f"{first_name}'s AI Radar - {email_digest.introduction.greeting.split('for ')[-1] if 'for ' in email_digest.introduction.greeting else 'Today'}"
            
            # Send email
            send_email(
                subject=subject,
                body_text=markdown_content,
                body_html=html_content,
                recipients=[u['email']]
            )
            
            # Log successful delivery (resilient to stale connections)
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
            
            logger.info(f"✓ Email sent to {u['email']} with {len(email_digest.articles)} articles")
            
            # Short pause between users to prevent hitting Groq RPM limits
            time.sleep(3)
            
        except Exception as e:
            results["failed"] += 1
            results["details"].append({
                "user": u['email'],
                "status": "failed",
                "error": str(e)
            })
            
            # Log failed delivery
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
    
    results["articles_count"] = results["sent"]  # For backward compatibility
    if results["failed"] > 0 and results["sent"] == 0:
        results["success"] = False
    
    logger.info(f"Multi-user delivery complete: {results['sent']} sent, {results['failed']} failed")
    return results


if __name__ == "__main__":
    result = send_digest_to_all_users(hours=24, top_n=10)
    if result["success"]:
        print(f"\n=== Digest Delivery Complete ===")
        print(f"Sent: {result.get('sent', 1)}")
        print(f"Failed: {result.get('failed', 0)}")
    else:
        print(f"Error: {result.get('error', 'Unknown')}")
