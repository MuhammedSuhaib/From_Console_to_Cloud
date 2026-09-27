from confluent_kafka import Producer
import json
import logging
import os
from utils.dapr_utils import dapr_http_fallback

logger = logging.getLogger(__name__)

def delivery_report(err, msg):
    """Callback for reporting message delivery results."""
    if err is not None:
        logger.error(f'Message delivery failed: {err}')
    else:
        logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def _get_kafka_producer():
    """Lazy initialize and return module-level Kafka Producer instance."""
    global _producer
    if _producer is None:
        try:
            bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
            kafka_username = os.getenv('KAFKA_USERNAME', '')
            kafka_password = os.getenv('KAFKA_PASSWORD', '')

            conf = {
                'bootstrap.servers': bootstrap_servers,
                'security.protocol': 'SASL_SSL',
                'sasl.mechanism': 'SCRAM-SHA-256',
                'sasl.username': kafka_username,
                'sasl.password': kafka_password,
                'acks': 'all',
                'client.software.name': 'confluent-kafka-python',
                'client.software.version': '2.13.0',
                'socket.timeout.ms': 1000,
                'message.timeout.ms': 1000,
            }
            _producer = Producer(conf)
        except Exception as e:
            logger.error(f"Failed to create Kafka Producer: {e}")
            _producer = None
    return _producer

_producer = None

def publish_task_event(event_type: str, task_data: dict) -> bool:
    """
    Publish a task event to Dapr pub/sub, with Kafka fallback if Dapr not available.

    Args:
        event_type: Type of event (e.g., 'task_created', 'task_completed', 'task_updated')
        task_data: Dictionary containing task information

    Returns:
        bool: True if event published successfully, False otherwise
    """
    # First, try to use Dapr sidecar if available
    dapr_response = dapr_http_fallback(
        endpoint="/v1.0/publish/task-pubsub/task-events",
        method="POST",
        data={
            "event_type": event_type,
            "task_data": task_data,
            "timestamp": task_data.get('updated_at', task_data.get('created_at'))
        }
    )

    if dapr_response is not None:
        # Dapr succeeded
        logger.info(f"Published {event_type} event via Dapr for task: {task_data.get('id', 'unknown')}")
        return True
    else:
        # Dapr not available, fall back to Kafka
        logger.info("Dapr sidecar not available, falling back to Kafka")

    # Fallback to Kafka
    try:
        producer = _get_kafka_producer()
        if producer is None:
            logger.error("Kafka Producer is not initialized.")
            return False

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

        # Flush with short timeout so broken Kafka connection doesn't stall request
        producer.flush(timeout=1)

        logger.info(f"Published {event_type} event via Kafka for task: {task_data.get('id', 'unknown')}")
        return True

    except Exception as e:
        logger.error(f"Error publishing {event_type} event: {str(e)}")
        return False