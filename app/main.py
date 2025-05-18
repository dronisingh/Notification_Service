from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import Notification
from pydantic import BaseModel
import pika
import json

app = FastAPI(title="Notification Service")

Base.metadata.create_all(bind=engine)

RABBITMQ_HOST = 'localhost'  # Use 'localhost' if not using Docker network
QUEUE_NAME = 'notifications'

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class NotificationCreate(BaseModel):
    user_id: int
    message: str
    type: str

def publish_to_rabbitmq(message: dict):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=False)
    channel.basic_publish(
        exchange='',
        routing_key=QUEUE_NAME,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2  # Make message persistent
        )
    )
    connection.close()

@app.post("/notifications")
def send_notification(notification: NotificationCreate, db: Session = Depends(get_db)):
    if notification.type not in ("email", "sms", "in_app"):
        raise HTTPException(status_code=400, detail="Invalid notification type")

    # Save notification to DB
    db_notification = Notification(
        user_id=notification.user_id,
        message=notification.message,
        type=notification.type
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)

    # Publish to RabbitMQ
    try:
        publish_to_rabbitmq({
            "id": db_notification.id,
            "user_id": notification.user_id,
            "message": notification.message,
            "type": notification.type
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enqueue notification: {str(e)}")

    return {"status": "Notification saved and queued", "id": db_notification.id}

@app.get("/users/{user_id}/notifications")
def get_notifications(user_id: int, db: Session = Depends(get_db)):
    notifications = db.query(Notification).filter(Notification.user_id == user_id).all()
    return notifications
