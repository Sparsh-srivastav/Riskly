import json
import logging
from aiokafka import AIOKafkaProducer

from app.core.config import settings

logger = logging.getLogger("riskly.kafka")

KAFKA_BOOTSTRAP_SERVERS = settings.kafka_bootstrap_servers
producer: AIOKafkaProducer | None = None


async def get_kafka_producer() -> AIOKafkaProducer:
    global producer
    if producer is None:
        producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await producer.start()
        logger.info("AIOKafkaProducer initialized and connected to %s", KAFKA_BOOTSTRAP_SERVERS)
    return producer


async def stop_kafka_producer():
    global producer
    if producer is not None:
        await producer.stop()
        producer = None
        logger.info("AIOKafkaProducer stopped.")


async def publish_event(topic: str, payload: dict):
    """
    Publishes a JSON-serialized event to a given Kafka topic.
    """
    try:
        prod = await get_kafka_producer()
        await prod.send_and_wait(topic, payload)
        logger.info("Event successfully published to topic %s: %s", topic, payload)
    except Exception as exc:
        logger.error("Failed to publish event to topic %s: %s", topic, exc)