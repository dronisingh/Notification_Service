from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel
from workers.rabbitmq_client import publish_notification  # corrected import

# Database Configuration
DATABASE_URL = "postgresql://postgres:pass@localhost:5433/notifications"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy Model
class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    message = Column(String)
    type = Column(String)

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI()

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic model for incoming notification data
class NotificationIn(BaseModel):
    user_id: int
    message: str
    type: str  # "email", "sms", or "in_app"

# POST /notifications — enqueue notification to RabbitMQ
@app.post("/notifications")
def send_notification(notification: NotificationIn, db: Session = Depends(get_db)):
    if notification.type not in ("email", "sms", "in_app"):
        raise HTTPException(status_code=400, detail="Invalid notification type")

    # Save notification to DB (for audit purposes)
    notif_db = Notification(
        user_id=notification.user_id,
        message=notification.message,
        type=notification.type,
    )
    db.add(notif_db)
    db.commit()
    db.refresh(notif_db)

    # Enqueue notification data to RabbitMQ for processing
    try:
        publish_notification(notification.dict())  # Make sure function name matches your workers.rabbitmq_client.py
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enqueue notification: {e}")

    return {"status": "Notification queued", "notification_id": notif_db.id}

# GET /users/{user_id}/notifications
@app.get("/users/{user_id}/notifications")
def get_notifications(user_id: int, db: Session = Depends(get_db)):
    notifications = db.query(Notification).filter(Notification.user_id == user_id).all()
    return notifications
