"""Standalone test to verify Gmail SMTP credentials and sending to both emails."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from app.services.email_service import send_email

recipients = ["grishmankp@gmail.com", "pgrishmank@gmail.com"]

print("=" * 60)
print(f"Testing Gmail SMTP connection...")
print(f"MY_EMAIL: {os.getenv('MY_EMAIL')}")
print(f"APP_PASSWORD set: {'Yes (length ' + str(len(os.getenv('APP_PASSWORD', ''))) + ')' if os.getenv('APP_PASSWORD') else 'No'}")
print(f"Target Recipients: {recipients}")
print("=" * 60)

for recipient in recipients:
    try:
        print(f"\nSending test email to: {recipient}...")
        send_email(
            subject="AI Radar - Gmail Test Verification",
            body_text="Hello! This is a test email to verify that Gmail SMTP is functioning properly.",
            body_html="<h3>AI Radar - Test</h3><p>Hello! This is a test email to verify that Gmail SMTP is functioning properly without using any Groq API tokens.</p>",
            recipients=[recipient]
        )
        print(f"SUCCESS: Email sent to {recipient}")
    except Exception as e:
        print(f"FAILED for {recipient}: {e}")

print("\n" + "=" * 60)
print("Gmail test completed.")
print("=" * 60)
