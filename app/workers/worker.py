import pika
import json
import logging

from app.services.email import send_email_notification
from app.services.sms import send_sms_notification
from app.services.in_app import send_inapp_notification

RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'notifications'

logging.basicConfig(level=logging.INFO)

def process_notification(notification):
    notif_type = notification.get('type')
    user_id = notification.get('user_id')
    message = notification.get('message')

    # Simulate failure for testing retry mechanism
    if message == 'force_fail':
        raise Exception("Forced failure for testing retries")

    if notif_type == 'email':
        send_email_notification(user_id, message)
    elif notif_type == 'sms':
        send_sms_notification(user_id, message)
    elif notif_type == 'in_app':
        send_inapp_notification(user_id, message)
    else:
        raise Exception(f"Unknown notification type: {notif_type}")

def callback(ch, method, properties, body):
    notification = json.loads(body)
    retries = properties.headers.get('x-retries', 0) if properties and properties.headers else 0

    try:
        process_notification(notification)
        logging.info(f"Processed notification for user {notification['user_id']}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logging.error(f"Exception in processing: {e}")

        if retries < 3:
            logging.info(f"Retrying immediately (retry {retries + 1})")

            # Republish message with incremented retry count
            ch.basic_publish(
                exchange='',
                routing_key=QUEUE_NAME,
                body=json.dumps(notification),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    headers={'x-retries': retries + 1}
                )
            )
        else:
            logging.error("Max retries reached. Discarding message.")

        # Always acknowledge the current message after handling retry or discard
        ch.basic_ack(delivery_tag=method.delivery_tag)

if __name__ == "__main__":
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    # Declare the queue with durability if needed
    channel.queue_declare(queue=QUEUE_NAME, durable=False)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    logging.info("Worker started. Waiting for messages...")
    channel.start_consuming()
