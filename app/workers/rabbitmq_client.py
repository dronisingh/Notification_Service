import pika
import json
import logging

RABBITMQ_HOST = 'localhost'  # Use 'localhost' if running without Docker, or docker service name

def get_connection():
    """Establish connection to RabbitMQ server."""
    parameters = pika.ConnectionParameters(host=RABBITMQ_HOST)
    return pika.BlockingConnection(parameters)

def publish_notification(message: dict):
    """Publish notification message to 'notifications' queue."""
    connection = None
    try:
        connection = get_connection()
        channel = connection.channel()

        # Declare durable queue to survive RabbitMQ restarts
        channel.queue_declare(queue='notifications', durable=True)

        # Publish message as JSON string with persistent delivery mode
        channel.basic_publish(
            exchange='',
            routing_key='notifications',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )
        logging.info(f"Published message to queue: {message}")
    except Exception as e:
        logging.error(f"Failed to publish message: {e}")
        raise
    finally:
        if connection and connection.is_open:
            connection.close()

def consume_notifications(callback):
    """Consume messages from 'notifications' queue and execute callback(message)."""
    connection = None
    try:
        connection = get_connection()
        channel = connection.channel()

        # Declare queue in case it doesn't exist
        channel.queue_declare(queue='notifications', durable=True)

        # Limit unacknowledged messages to 1 for fair dispatch
        channel.basic_qos(prefetch_count=1)

        def on_message(ch, method, properties, body):
            message = json.loads(body)
            try:
                callback(message)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logging.error(f"Error processing message: {e}")
                # You might choose to nack or reject messages here, or requeue

        channel.basic_consume(queue='notifications', on_message_callback=on_message)
        logging.info("Waiting for messages...")
        channel.start_consuming()

    except Exception as e:
        logging.error(f"Error consuming messages: {e}")
        raise
    finally:
        if connection and connection.is_open:
            connection.close()
