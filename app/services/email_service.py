import os
import smtplib
import html
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import markdown

load_dotenv()

MY_EMAIL = os.getenv("MY_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")


def send_email(subject: str, body_text: str, body_html: str = None, recipients: list = None):
    my_email = os.getenv("MY_EMAIL")
    app_password = os.getenv("APP_PASSWORD")

    # If SMTP credentials are missing, save locally as HTML / MD file
    if not my_email or not app_password:
        os.makedirs("output", exist_ok=True)
        html_path = os.path.join("output", "latest_digest.html")
        md_path = os.path.join("output", "latest_digest.md")
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(body_html or body_text)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(body_text)
            
        print(f"\n[INFO] MY_EMAIL or APP_PASSWORD not set. Digest saved locally to: {os.path.abspath(html_path)}")
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
    
    # Always save a local copy as backup
    os.makedirs("output", exist_ok=True)
    html_path = os.path.join("output", "latest_digest.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(body_html or body_text)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(my_email, app_password)
        smtp.sendmail(my_email, recipients, msg.as_string())


def markdown_to_html(markdown_text: str) -> str:
    html = markdown.markdown(markdown_text, extensions=['extra', 'nl2br'])
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
{html}
</body>
</html>"""


def digest_to_html(digest_response) -> str:
    from app.agent.email_agent import EmailDigestResponse
    
    if not isinstance(digest_response, EmailDigestResponse):
        return markdown_to_html(digest_response.to_markdown() if hasattr(digest_response, 'to_markdown') else str(digest_response))
    
    html_parts = []
    greeting_html = markdown.markdown(digest_response.introduction.greeting, extensions=['extra', 'nl2br'])
    introduction_html = markdown.markdown(digest_response.introduction.introduction, extensions=['extra', 'nl2br'])
    
    # Header Branding
    html_parts.append("""
    <div style="border-bottom: 2px solid #2563eb; padding-bottom: 12px; margin-bottom: 20px;">
        <div style="font-size: 11px; font-weight: 700; letter-spacing: 1.5px; color: #2563eb; text-transform: uppercase;">
            GenAI Intelligence Digest • IIITDM Kancheepuram
        </div>
        <h1 style="font-size: 22px; font-weight: 700; color: #0f172a; margin: 6px 0 0 0; letter-spacing: -0.5px;">
            Grishmank's Daily AI Radar
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
    
    # Footer
    html_parts.append("""
    <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid #e2e8f0; font-size: 12px; color: #64748b; text-align: center;">
        <p style="margin: 0;">Automated Multi-Agent AI System • Curated for <strong>Grishmank Parate</strong></p>
        <p style="margin: 4px 0 0 0;">Powered by Groq Open-Source LLMs & SQLite</p>
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
