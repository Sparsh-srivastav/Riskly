import asyncio
import json
import logging
import socket
from aiokafka import AIOKafkaProducer
from app.core.config import settings

logger = logging.getLogger("riskly.kafka")

KAFKA_BOOTSTRAP_SERVERS = settings.kafka_bootstrap_servers
producer: AIOKafkaProducer | None = None
_checked: bool = False
_is_online: bool = False

def is_broker_online() -> bool:
    global _checked, _is_online
    if _checked:
        return _is_online
    _checked = True
    try:
        host, port = KAFKA_BOOTSTRAP_SERVERS.split(":")
        with socket.create_connection((host, int(port)), timeout=0.1):
            _is_online = True
            logger.info("Kafka broker detected at %s", KAFKA_BOOTSTRAP_SERVERS)
    except Exception:
        _is_online = False
        logger.info("Kafka offline (%s). Running in standalone mode.", KAFKA_BOOTSTRAP_SERVERS)
    return _is_online

async def get_kafka_producer() -> AIOKafkaProducer | None:
    global producer
    if not is_broker_online():
        return None
    if producer is None:
        try:
            prod = AIOKafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            await prod.start()
            producer = prod
        except Exception as e:
            logger.warning("Kafka start failed: %s", e)
            return None
    return producer

async def stop_kafka_producer():
    global producer
    if producer is not None:
        try:
            await producer.stop()
        except Exception:
            pass
        producer = None

async def publish_event(topic: str, payload: dict):
    if not is_broker_online():
        return
    try:
        prod = await get_kafka_producer()
        if prod:
            await prod.send_and_wait(topic, payload)
    except Exception as exc:
        logger.error("Kafka publish failed: %s", exc)
