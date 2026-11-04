import asyncio
import json
import logging
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("stream-processor")

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
INCOMING_TOPIC = "contact-reports"
ALERTS_TOPIC = "risk-alerts"

WINDOW_DURATION = timedelta(minutes=10)
VELOCITY_THRESHOLD = 3
event_window_store = defaultdict(list)


def evaluate_velocity_threshold(contact_key: str, now: datetime) -> int:
    timestamps = event_window_store[contact_key]
    cutoff = now - WINDOW_DURATION
    active_timestamps = [ts for ts in timestamps if ts > cutoff]
    active_timestamps.append(now)
    event_window_store[contact_key] = active_timestamps
    return len(active_timestamps)


async def run_processor():
    logger.info("Initializing Riskly Kafka Stream Processor...")

    consumer = AIOKafkaConsumer(
        INCOMING_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="riskly-stream-processor-group",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="latest",
    )

    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda m: json.dumps(m).encode("utf-8"),
    )

    while True:
        try:
            await consumer.start()
            await producer.start()
            logger.info("Connected to Kafka brokers successfully.")
            break
        except Exception as e:
            logger.warning("Kafka broker unavailable, retrying in 3 seconds: %s", e)
            await asyncio.sleep(3)

    try:
        async for msg in consumer:
            payload = msg.value
            contact_val = payload.get("normalized_value", "unknown")
            contact_type = payload.get("contact_type", "unknown")
            ml_score = payload.get("ml_risk_score", 0.0)
            report_cat = payload.get("report_type", "unknown")

            now = datetime.now(timezone.utc)
            contact_key = f"{contact_type}:{contact_val}"
            report_count_in_window = evaluate_velocity_threshold(contact_key, now)

            logger.info(
                "Ingested [%s] | Category: %s | ML Score: %s | Window Velocity: %d",
                contact_key,
                report_cat,
                ml_score,
                report_count_in_window,
            )

            is_velocity_burst = report_count_in_window >= VELOCITY_THRESHOLD
            is_critical_ml = ml_score >= 80.0

            if is_velocity_burst or is_critical_ml:
                alert_payload = {
                    "event": "risk_alert",
                    "contact_type": contact_type,
                    "contact_value": contact_val,
                    "velocity_count": report_count_in_window,
                    "window_minutes": 10,
                    "ml_risk_score": ml_score,
                    "alert_reason": (
                        "HIGH_VELOCITY_ATTACK" if is_velocity_burst else "CRITICAL_ML_CONFIDENCE"
                    ),
                    "timestamp": now.isoformat(),
                }

                logger.warning("🚨 DISPATCHING RISK ALERT: %s", alert_payload)
                await producer.send_and_wait(ALERTS_TOPIC, alert_payload)

    except asyncio.CancelledError:
        pass
    finally:
        await consumer.stop()
        await producer.stop()
        logger.info("Stream Processor stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(run_processor())
    except KeyboardInterrupt:
        logger.info("Shutting down stream processor...")