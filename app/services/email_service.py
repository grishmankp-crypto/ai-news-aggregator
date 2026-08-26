import os
import smtplib
import html
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import markdown

load_dotenv()

logger = logging.getLogger(__name__)

MY_EMAIL = os.getenv("MY_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")


def send_email(subject: str, body_text: str, body_html: str = None, recipients: list = None):
    """Send email via Resend (primary) or Gmail SMTP (fallback)."""
    resend_key = os.getenv("RESEND_API_KEY")
    
    if resend_key and recipients:
        # Use Resend for multi-user delivery
        _send_via_resend(subject, body_text, body_html, recipients, resend_key)
    else:
        # Fallback to Gmail SMTP for single-user / local dev
        _send_via_gmail(subject, body_text, body_html, recipients)
    
    # Always save a local backup
    _save_local_backup(body_html or body_text)


def _send_via_resend(subject: str, body_text: str, body_html: str, recipients: list, api_key: str):
    """Send email using Resend API (supports multi-user bulk delivery)."""
    import requests
    
    from_email = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")
    
    for recipient in recipients:
        try:
            response = requests.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "from": f"AI Radar <{from_email}>",
                    "to": [recipient],
                    "subject": subject,
                    "html": body_html or body_text,
                    "text": body_text
                }
            )
            if response.status_code in (200, 201):
                logger.info(f"Email sent via Resend to {recipient}")
            else:
                logger.error(f"Resend error for {recipient}: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Failed to send via Resend to {recipient}: {e}")


def _send_via_gmail(subject: str, body_text: str, body_html: str, recipients: list = None):
    """Send email using Gmail SMTP (single-user fallback)."""
    my_email = (os.getenv("MY_EMAIL") or "").strip().strip('"').strip("'")
    app_password = (os.getenv("APP_PASSWORD") or "").replace(" ", "").strip().strip('"').strip("'")

    # If SMTP credentials are missing, save locally as HTML / MD file
    if not my_email or not app_password:
        os.makedirs("output", exist_ok=True)
        html_path = os.path.join("output", "latest_digest.html")
        md_path = os.path.join("output", "latest_digest.md")
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(body_html or body_text)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(body_text)
            
        logger.info(f"MY_EMAIL or APP_PASSWORD not set. Digest saved locally to: {os.path.abspath(html_path)}")
        return
    
    if recipients is None:
        recipients = [my_email]
    
    recipients = [r for r in recipients if r is not None]
    if not recipients:
        recipients = [my_email]
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = my_email
    msg["To"] = ", ".join(recipients)
    
    part1 = MIMEText(body_text, "plain")
    msg.attach(part1)
    
    if body_html:
        part2 = MIMEText(body_html, "html")
        msg.attach(part2)

    masked_pass = f"{app_password[:2]}***{app_password[-2:]} (len: {len(app_password)})" if len(app_password) >= 4 else f"(len: {len(app_password)})"
    logger.info(f"Authenticating Gmail SMTP with user='{my_email}', password={masked_pass}")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(my_email, app_password)
            smtp.sendmail(my_email, recipients, msg.as_string())
        logger.info(f"Email sent via Gmail SMTP to {recipients}")
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"Gmail SMTP Authentication Failed! user='{my_email}', password_info={masked_pass}. Check your GitHub Secret 'MY_EMAIL' and 'APP_PASSWORD'. Error: {e}")
        raise e


def _save_local_backup(content: str):
    """Save a local HTML backup of the latest digest."""
    try:
        os.makedirs("output", exist_ok=True)
        html_path = os.path.join("output", "latest_digest.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception:
        pass  # Don't crash the pipeline over a backup file


def markdown_to_html(markdown_text: str) -> str:
    html_content = markdown.markdown(markdown_text, extensions=['extra', 'nl2br'])
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
        }}
        h2 {{
            font-size: 18px;
            font-weight: 600;
            color: #1a1a1a;
            margin-top: 24px;
            margin-bottom: 8px;
            line-height: 1.4;
        }}
        h3 {{
            font-size: 16px;
            font-weight: 600;
            color: #1a1a1a;
            margin-top: 20px;
            margin-bottom: 8px;
            line-height: 1.4;
        }}
        p {{
            margin: 8px 0;
            color: #4a4a4a;
        }}
        strong {{
            font-weight: 600;
            color: #1a1a1a;
        }}
        em {{
            font-style: italic;
            color: #666;
        }}
        a {{
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        hr {{
            border: none;
            border-top: 1px solid #e5e5e5;
            margin: 20px 0;
        }}
        .greeting {{
            font-size: 16px;
            font-weight: 500;
            color: #1a1a1a;
            margin-bottom: 12px;
        }}
        .introduction {{
            color: #4a4a4a;
            margin-bottom: 20px;
        }}
        .article-link {{
            display: inline-block;
            margin-top: 8px;
            color: #0066cc;
            font-size: 14px;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""


def digest_to_html(digest_response, user_name: str = "Grishmank Parate", user_email: str = None) -> str:
    """Generate branded HTML email from a digest response.
    
    Args:
        digest_response: EmailDigestResponse object
        user_name: Full name of the recipient (for dynamic branding)
        user_email: Email for unsubscribe link (optional)
    """
    from app.agent.email_agent import EmailDigestResponse
    
    if not isinstance(digest_response, EmailDigestResponse):
        return markdown_to_html(digest_response.to_markdown() if hasattr(digest_response, 'to_markdown') else str(digest_response))
    
    first_name = user_name.split()[0] if user_name else "there"
    
    html_parts = []
    greeting_html = markdown.markdown(digest_response.introduction.greeting, extensions=['extra', 'nl2br'])
    introduction_html = markdown.markdown(digest_response.introduction.introduction, extensions=['extra', 'nl2br'])
    
    # Header Branding (dynamic per user)
    html_parts.append(f"""
    <div style="border-bottom: 2px solid #2563eb; padding-bottom: 12px; margin-bottom: 20px;">
        <div style="font-size: 11px; font-weight: 700; letter-spacing: 1.5px; color: #2563eb; text-transform: uppercase;">
            AI Radar • Personalized AI Newsletter
        </div>
        <h1 style="font-size: 22px; font-weight: 700; color: #0f172a; margin: 6px 0 0 0; letter-spacing: -0.5px;">
            {first_name}'s Daily AI Digest
        </h1>
    </div>
    """)
    
    html_parts.append(f'<div class="greeting">{greeting_html}</div>')
    html_parts.append(f'<div class="introduction">{introduction_html}</div>')
    html_parts.append('<hr>')
    
    for article in digest_response.articles:
        html_parts.append(f'<h3>{html.escape(article.title)}</h3>')
        summary_html = markdown.markdown(article.summary, extensions=['extra', 'nl2br'])
        html_parts.append(f'<div>{summary_html}</div>')
        html_parts.append(f'<p><a href="{html.escape(article.url)}" class="article-link">Read full story →</a></p>')
        html_parts.append('<hr>')
    
    # Footer with unsubscribe link
    unsubscribe_html = ""
    if user_email:
        unsubscribe_html = f' • <a href="mailto:grishmankp@gmail.com?subject=Unsubscribe&body=Please unsubscribe {user_email}" style="color: #94a3b8; text-decoration: underline;">Unsubscribe</a>'
    
    html_parts.append(f"""
    <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid #e2e8f0; font-size: 12px; color: #64748b; text-align: center;">
        <p style="margin: 0;">AI Radar • Multi-Agent AI Newsletter • Curated for <strong>{html.escape(user_name)}</strong></p>
        <p style="margin: 4px 0 0 0;">Powered by Groq Open-Source LLMs{unsubscribe_html}</p>
    </div>
    """)
    
    html_content = '\n'.join(html_parts)
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #334155;
            max-width: 620px;
            margin: 0 auto;
            padding: 24px;
            background-color: #ffffff;
        }}
        h3 {{
            font-size: 17px;
            font-weight: 700;
            color: #0f172a;
            margin-top: 22px;
            margin-bottom: 8px;
            line-height: 1.4;
        }}
        p {{
            margin: 8px 0;
            color: #334155;
        }}
        strong {{
            font-weight: 600;
            color: #0f172a;
        }}
        em {{
            font-style: italic;
            color: #64748b;
        }}
        a {{
            color: #2563eb;
            text-decoration: none;
            font-weight: 600;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        hr {{
            border: none;
            border-top: 1px solid #e2e8f0;
            margin: 20px 0;
        }}
        .greeting {{
            font-size: 16px;
            font-weight: 600;
            color: #0f172a;
            margin-bottom: 12px;
        }}
        .introduction {{
            color: #475569;
            margin-bottom: 20px;
            font-size: 15px;
        }}
        .article-link {{
            display: inline-block;
            margin-top: 6px;
            color: #2563eb;
            font-size: 14px;
        }}
        .greeting p {{
            margin: 0;
        }}
        .introduction p {{
            margin: 0;
        }}
        div {{
            margin: 8px 0;
            color: #334155;
        }}
        div p {{
            margin: 4px 0;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""


def send_email_to_self(subject: str, body: str):
    if not MY_EMAIL:
        raise ValueError("MY_EMAIL environment variable is not set. Please set it in your .env file.")
    send_email(subject, body, recipients=[MY_EMAIL])


if __name__ == "__main__":
    send_email_to_self("Test from Python", "Hello from my script.")
