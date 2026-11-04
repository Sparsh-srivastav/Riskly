import json
import logging
import random
import sys
import time
import urllib.request
import urllib.error

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("attack-simulator")

API_BASE = "http://127.0.0.1:8000"

ATTACK_VECTORS = [
    {
        "category": "fraud",
        "description": "CBI officer demanding urgent wire transfer for arrest warrant and asking for debit card pin.",
        "evidence": "Fake summons document sent via WhatsApp PDF",
    },
    {
        "category": "phishing",
        "description": "Urgent bank alert: your debit card is blocked. Click login link and verify OTP immediately.",
        "evidence": "http://secure-update-hdfc-kyc.com/login",
    },
    {
        "category": "fraud",
        "description": "Won 50000 lottery cash prize! Demanding advance customs fee via crypto transfer.",
        "evidence": "Telegram handle @fast_reward_support",
    },
    {
        "category": "phishing",
        "description": "Caller claimed to be tech support asking for remote screen share and CVV to unblock laptop.",
        "evidence": "Toll-free customer support spoof",
    },
    {
        "category": "spam",
        "description": "Unsolicited pre-approved personal loan promotion message with suspicious shortlink.",
        "evidence": "SMS short code link bit.ly/loan-fast",
    },
]

TARGET_ENTITIES = [
    {"type": "phone", "value": "+919876543210"},
    {"type": "phone", "value": "+919123456789"},
    {"type": "email", "value": "security-alert@update-bank-kyc.com"},
    {"type": "phone", "value": "+918800112233"},
    {"type": "email", "value": "support@crypto-instant-double.org"},
]


def post_json(url: str, data: dict, headers: dict = None) -> dict:
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers=req_headers,
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_analyst_token() -> str:
    login_payload = {"email": "analyst@riskly.dev", "password": "analyst123"}
    try:
        data = post_json(f"{API_BASE}/auth/login", login_payload)
        return data["access_token"]
    except urllib.error.HTTPError as e:
        if e.code == 401:
            logger.info("Registering analyst user...")
            post_json(
                f"{API_BASE}/auth/register",
                {**login_payload, "role": "analyst"},
            )
            data = post_json(f"{API_BASE}/auth/login", login_payload)
            return data["access_token"]
        raise


def simulate_burst(rate_delay_seconds: float = 2.0, count: int = 8):
    logger.info("Starting Riskly Attack Simulator. Emitting %d incidents...", count)
    try:
        token = get_analyst_token()
        headers = {"Authorization": f"Bearer {token}"}
    except Exception as e:
        logger.error("Failed to authenticate simulator: %r", e)
        return

    for i in range(1, count + 1):
        entity = random.choice(TARGET_ENTITIES)
        scenario = random.choice(ATTACK_VECTORS)

        payload = {
            "contact_type": entity["type"],
            "contact_value": entity["value"],
            "report_type": scenario["category"],
            "description": scenario["description"],
            "evidence": scenario["evidence"],
        }

        try:
            post_json(f"{API_BASE}/reports", payload, headers=headers)
            logger.info(
                "[%d/%d] Emitted %s report for %s",
                i,
                count,
                scenario["category"].upper(),
                entity["value"],
            )
        except Exception as e:
            logger.error("Request error: %r", e)

        time.sleep(rate_delay_seconds)

    logger.info("Simulator burst completed.")


if __name__ == "__main__":
    burst_count = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    simulate_burst(rate_delay_seconds=2.0, count=burst_count)
