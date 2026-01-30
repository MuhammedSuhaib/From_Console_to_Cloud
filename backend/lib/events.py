from confluent_kafka import Producer
import json
import logging
import os

logger = logging.getLogger(__name__)

def delivery_report(err, msg):
    """Callback for reporting message delivery results."""
    if err is not None:
        logger.error(f'Message delivery failed: {err}')
    else:
        logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def publish_task_event(event_type: str, task_data: dict) -> bool:
    """
    Publish a task event to Kafka.

    Args:
        event_type: Type of event (e.g., 'task_created', 'task_completed', 'task_updated')
        task_data: Dictionary containing task information

    Returns:
        bool: True if event published successfully, False otherwise
    """
    try:
        # Get Kafka configuration from environment variables
        bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        kafka_username = os.getenv('KAFKA_USERNAME', '')
        kafka_password = os.getenv('KAFKA_PASSWORD', '')

        # Configure Kafka producer with SASL_SSL and SCRAM-SHA-256
        conf = {
            'bootstrap.servers': bootstrap_servers,
            'security.protocol': 'SASL_SSL',
            'sasl.mechanism': 'SCRAM-SHA-256',
            'sasl.username': kafka_username,
            'sasl.password': kafka_password,
            'acks': 'all'
        }

        # Create producer
        producer = Producer(conf)

        # Create the event payload
        event_payload = {
            "event_type": event_type,
            "task_data": task_data,
            "timestamp": task_data.get('updated_at', task_data.get('created_at'))
        }

        # Convert to JSON string
        message_value = json.dumps(event_payload)

        # Asynchronously produce a message, the delivery report callback
        # will be triggered from poll() above, or flush() below
        producer.produce('task-events', message_value.encode('utf-8'), callback=delivery_report)

        # Wait for any outstanding messages to be delivered and delivery report
        # callbacks to be triggered
        producer.flush()

        logger.info(f"Published {event_type} event for task: {task_data.get('id', 'unknown')}")
        return True

    except Exception as e:
        logger.error(f"Error publishing {event_type} event: {str(e)}")
        return False