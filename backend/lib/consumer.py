from confluent_kafka import Consumer, KafkaException
import json
import logging
import os
import threading
import asyncio

logger = logging.getLogger(__name__)

def start_kafka_consumer():
    """
    Start a Kafka consumer to listen to the task-events topic.
    """
    try:
        # Get Kafka configuration from environment variables
        bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        kafka_username = os.getenv('KAFKA_USERNAME', '')
        kafka_password = os.getenv('KAFKA_PASSWORD', '')

        # Configure Kafka consumer with SASL_SSL and SCRAM-SHA-256
        conf = {
            'bootstrap.servers': bootstrap_servers,
            'security.protocol': 'SASL_SSL',
            'sasl.mechanism': 'SCRAM-SHA-256',
            'sasl.username': kafka_username,
            'sasl.password': kafka_password,
            'group.id': 'task-event-consumer-group',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True
        }

        # Create consumer
        consumer = Consumer(conf)

        # Subscribe to the task-events topic
        consumer.subscribe(['task-events'])

        logger.info("Kafka consumer started, listening to task-events topic...")

        # Poll for messages
        while True:
            try:
                msg = consumer.poll(timeout=1.0)  # Wait for 1 second for a message

                if msg is None:
                    continue  # Timeout, no message received

                if msg.error():
                    # Error occurred
                    if msg.error().code() == KafkaException._PARTITION_EOF:
                        # End of partition reached, which is not an error
                        continue
                    else:
                        logger.error(f"Consumer error: {msg.error()}")
                        continue

                # Process the message
                try:
                    # Decode the message value
                    message_value = msg.value().decode('utf-8')
                    event_data = json.loads(message_value)

                    event_type = event_data.get('event_type')
                    task_data = event_data.get('task_data', {})

                    if event_type == 'task_created':
                        user_id = task_data.get('user_id', 'Unknown')
                        due_date = task_data.get('due_date')

                        if due_date:
                            logger.info(f'Consumer: Received task for [User: {user_id}] due on [{due_date}]')
                        else:
                            logger.info(f'Consumer: Received task for [User: {user_id}] without due date')

                    # Add more event type handling as needed
                    elif event_type == 'task_completed':
                        user_id = task_data.get('user_id', 'Unknown')
                        task_title = task_data.get('title', 'Unknown')
                        logger.info(f'Consumer: Task completed for [User: {user_id}] - Task: {task_title}')

                    else:
                        logger.info(f'Consumer: Received {event_type} event for user {task_data.get("user_id", "Unknown")}')

                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode JSON message: {e}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

            except KeyboardInterrupt:
                logger.info("Consumer interrupted by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in consumer: {e}")
                break

    except Exception as e:
        logger.error(f"Error starting Kafka consumer: {e}")

    finally:
        # Close the consumer
        try:
            consumer.close()
            logger.info("Kafka consumer closed")
        except:
            pass

def run_consumer_in_thread():
    """
    Run the Kafka consumer in a separate thread.
    """
    consumer_thread = threading.Thread(target=start_kafka_consumer, daemon=True)
    consumer_thread.start()
    return consumer_thread