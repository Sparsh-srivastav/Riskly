import time
import random
import requests

API_URL = "http://127.0.0.1:8000/reports"

MOCK_IDENTITIES = [
    ("phone", "+919811223344", "impersonation", "Fake electricity department bill suspension call."),
    ("email", "alert-security@login-verify99.net", "phishing", "Banking credential harvesting page mimicking HDFC netbanking."),
    ("upi", "refund-support@okhdfcbank", "fraud", "QR code refund fraud requesting immediate PIN entry."),
    ("url", "https://kyc-update-portal-axis.com", "phishing", "Malicious phishing clone harvesting Aadhaar and PAN card details."),
    ("phone", "+919988776655", "spam", "Automated pre-recorded personal loan telemarketing robocall."),
    ("bank_account", "SBIN0001234-998822331", "fraud", "Mule account associated with illicit telegram investment tasks."),
    ("url", "https://free-crypto-giveaway-airdrop.org", "fraud", "Drainer smart contract scam asking for wallet signature.")
]

def main():
    print("[*] Starting Riskly Ingestion Stream Telemetry...")
    count = 0
    while True:
        try:
            ctype, cval, rtype, desc = random.choice(MOCK_IDENTITIES)
            
            if ctype == "phone":
                cval = f"+9198{random.randint(10000000, 99999999)}"
            elif ctype == "url":
                cval = f"https://secure-login-update{random.randint(10, 99)}.com"
            elif ctype == "email":
                cval = f"alert{random.randint(100, 999)}@phishdomain.com"
            elif ctype == "upi":
                cval = f"user{random.randint(100, 999)}@okhdfcbank"

            payload = {
                "contact_type": ctype,
                "contact_value": cval,
                "report_type": rtype,
                "description": desc,
                "evidence": None
            }
            
            r = requests.post(API_URL, json=payload, timeout=5)
            if r.status_code in [200, 201]:
                count += 1
                data = r.json()
                print(f"[+] Ingested #{count}: {cval} ({rtype.upper()}) | ML: {data.get('ml_risk_score')}%")
            else:
                print(f"[-] HTTP {r.status_code}: {r.text}")

        except Exception as err:
            print(f"[!] Stream error: {err}")

        time.sleep(random.uniform(1.2, 2.2))

if __name__ == "__main__":
    main()
