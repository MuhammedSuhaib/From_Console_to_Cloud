from dapr.ext.fastapi import DaprApp
from dapr.clients import DaprClient
import json
import logging

logger = logging.getLogger(__name__)

def publish_task_event(event_type: str, task_data: dict) -> bool:
    """
    Publish a task event to the Dapr pub/sub component.

    Args:
        event_type: Type of event (e.g., 'task_created', 'task_completed', 'task_updated')
        task_data: Dictionary containing task information

    Returns:
        bool: True if event published successfully, False otherwise
    """
    try:
        with DaprClient() as client:
            # Create the event payload
            event_payload = {
                "event_type": event_type,
                "task_data": task_data,
                "timestamp": json.dumps(task_data.get('updated_at', task_data.get('created_at')))
            }

            # Publish to the pubsub component
            client.publish_event(
                pubsub_name='task-pubsub',
                topic_name='task-events',
                data=json.dumps(event_payload),
                data_content_type='application/json'
            )

            logger.info(f"Published {event_type} event for task: {task_data.get('id', 'unknown')}")
            return True

    except Exception as e:
        logger.error(f"Error publishing {event_type} event: {str(e)}")
        return False