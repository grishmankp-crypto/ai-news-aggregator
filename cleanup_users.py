"""Quick script to deactivate extra users, keeping only pgrishmank@gmail.com and grishmankp@gmail.com."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from app.database.connection import get_session
from app.database.models import User

session = get_session()

keep_emails = {"pgrishmank@gmail.com", "grishmankp@gmail.com"}

users = session.query(User).all()
print(f"\n{'='*60}")
print(f"Total users in database: {len(users)}")
print(f"{'='*60}\n")

for user in users:
    status = "[KEEP]" if user.email in keep_emails else "[DEACTIVATE]"
    print(f"  {status}: {user.name} ({user.email}) [active={user.is_active}]")
    
    if user.email not in keep_emails and user.is_active:
        user.is_active = False

session.commit()

# Verify
active_users = session.query(User).filter_by(is_active=True).all()
print(f"\n{'='*60}")
print(f"Active users remaining: {len(active_users)}")
for u in active_users:
    print(f"  -> {u.name} ({u.email})")
print(f"{'='*60}")

session.close()
print("\nDone! Extra users deactivated.")
