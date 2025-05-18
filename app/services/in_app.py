# app/services/in_app.py
from app.database import SessionLocal
from app.models import Notification

def send_inapp_notification(user_id, message):
    if message == "force_fail":
        raise Exception("Simulated in-app failure for testing retries")
    db = SessionLocal()
    notif = Notification(user_id=user_id, message=message, type="in_app")
    db.add(notif)
    db.commit()
    db.refresh(notif)
    db.close()
    print(f"In-app notification stored for user {user_id}: {message}")
