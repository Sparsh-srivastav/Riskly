import random
import time

CONTACT_TYPES = ['phone', 'upi', 'bank_account', 'url']
REPORT_TYPES = ['fraud', 'phishing', 'spam', 'impersonation', 'harassment']

sample_desc = [
    'Fake lottery prize scam call requesting OTP.',
    'Phishing SMS impersonating bank customer support.',
    'UPI request scam via fake marketplace listing.',
    'Fraudulent investment scheme promising high returns.',
    'Malicious URL distributing banking trojan.'
]

def generate_mock_incident():
    return {
        'contact_type': random.choice(CONTACT_TYPES),
        'contact_value': f'+91{random.randint(7000000000, 9999999999)}',
        'report_type': random.choice(REPORT_TYPES),
        'description': random.choice(sample_desc),
        'evidence': 'simulated_telemetry_hash'
    }

if __name__ == '__main__':
    print('Starting Riskly Mock Incident Generator...')
    for i in range(5):
        print(generate_mock_incident())
