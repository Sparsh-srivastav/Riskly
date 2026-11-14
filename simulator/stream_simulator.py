import random
import time
import requests

BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/auth/login"
REGISTER_URL = f"{BASE_URL}/auth/register"
REPORTS_URL = f"{BASE_URL}/reports"

USER_PAYLOAD = {
    "email": "simulator@riskly.internal",
    "password": "SimulatorPassword123!",
    "role": "analyst"
}

REPORT_TYPES = ["fraud", "phishing", "spam", "impersonation", "harassment"]

SAMPLE_DESCRIPTIONS = [
    "Fake lottery prize scam call requesting OTP.",
    "Phishing SMS impersonating bank customer support.",
    "UPI request scam via fake marketplace listing.",
    "Fraudulent investment scheme promising high returns.",
    "Malicious URL distributing banking trojan."
]

def get_auth_token() -> str:
    try:
        requests.post(REGISTER_URL, json=USER_PAYLOAD, timeout=3)
    except Exception:
        pass

    resp = requests.post(
        LOGIN_URL,
        json={"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]},
        timeout=3
    )
    if resp.status_code == 200:
        return resp.json().get("access_token")
    raise RuntimeError(f"Authentication failed: {resp.status_code} - {resp.text}")

def generate_sample_entity():
    c_type = random.choice(["phone", "upi", "email", "bank_account", "url"])
    if c_type == "phone":
        c_val = f"+91{random.randint(7000000000, 9999999999)}"
    elif c_type == "upi":
        c_val = f"user{random.randint(100, 999)}@okhdfcbank"
    elif c_type == "email":
        c_val = f"alert{random.randint(100, 999)}@phishdomain.com"
    elif c_type == "bank_account":
        c_val = f"{random.randint(10000000000, 99999999999)}"
    else:
        c_val = f"https://secure-login-update{random.randint(10, 99)}.com"
    return c_type, c_val

if __name__ == "__main__":
    print("Authenticating stream simulator...")
    token = get_auth_token()
    print("Simulator authenticated successfully.")
    print("Starting Riskly Real-Time Stream Simulator...")

    while True:
        c_type, c_val = generate_sample_entity()
        payload = {
            "contact_type": c_type,
            "contact_value": c_val,
            "report_type": random.choice(REPORT_TYPES),
            "description": random.choice(SAMPLE_DESCRIPTIONS),
            "evidence": "simulated_stream_evidence"
        }

        headers = {"Authorization": f"Bearer {token}"}

        try:
            response = requests.post(REPORTS_URL, json=payload, headers=headers, timeout=5)
            
            # Auto re-authenticate if token expires or server restarted
            if response.status_code == 401:
                print("Token expired or unauthorized (401). Refreshing token...")
                token = get_auth_token()
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.post(REPORTS_URL, json=payload, headers=headers, timeout=5)

            print(f"Submitted Incident: [{c_type.upper()}] {c_val}, Status: {response.status_code}")
        except requests.exceptions.Timeout:
            print("Server took longer than 5s to respond.")
        except Exception as e:
            print(f"Connection Error: {e}")

        time.sleep(2)
