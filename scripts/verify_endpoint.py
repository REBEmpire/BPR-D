import requests
import os

url = "https://bprd-meetings.onrender.com/api/v1/meetings/manual-trigger"
print(f"Testing URL: {url}")

try:
    # Sending a request without API key to see if it responds (expecting 401/403 or 422 validation error)
    response = requests.post(url, json={"meeting_type": "test"})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code in [401, 403]:
        print("✅ Endpoint exists (auth required). URL is likely correct.")
    elif response.status_code == 404:
        print("❌ Endpoint not found (404). URL is incorrect.")
    elif response.status_code == 405:
        print("❌ Method Not Allowed (405). URL is incorrect or not a POST.")
    elif response.status_code == 422:
        print("✅ Endpoint exists (Validation Error). URL is correct.")
    elif response.status_code == 200:
        print("✅ Endpoint exists and accepted request (unexpected without key but ok).")
    else:
        print(f"⚠️ Unexpected status code: {response.status_code}")

except Exception as e:
    print(f"❌ Connection failed: {e}")
