from app.database.repository import Repository
from app.database.models import User, EmailLog
from datetime import datetime, timezone, timedelta

repo = Repository()
users = repo.session.query(User).all()
print("=== All Users in DB ===")
for u in users:
    print(f"User ID: {u.id} | Email: {u.email} | Name: {u.name} | is_active: {u.is_active}")

print("\n=== Recent Email Logs (Last 24 Hours) ===")
cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
logs = repo.session.query(EmailLog).filter(EmailLog.sent_at >= cutoff).order_by(EmailLog.sent_at.desc()).all()
for l in logs:
    user = repo.session.query(User).filter_by(id=l.user_id).first()
    email = user.email if user else "Unknown"
    print(f"Log: sent_at: {l.sent_at} | User: {email} | Status: {l.status} | Subject: {l.subject}")
