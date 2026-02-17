import requests
import sys

URL = "https://bprd-meetings.onrender.com/api/v1/meeting"
PAYLOAD = {
    "meeting_type": "work_session",
    "participants": ["abacus"]
}

print(f"Triggering Abacus Work Session at {URL}...")
try:
    response = requests.post(URL, json=PAYLOAD, timeout=10)
    if response.status_code == 200:
        print("✅ SUCCESS: Work session triggered!")
        print(response.json())
    else:
        print(f"❌ FAILED: Status {response.status_code}")
        print(response.text)
        sys.exit(1)
except Exception as e:
    print(f"❌ ERROR: {e}")
    sys.exit(1)
