import hashlib
import hmac
import json
import requests
import os
from dotenv import load_dotenv

# Load your .env to get the matching secret
load_dotenv()

# CONFIG
WEBHOOK_URL = "http://localhost:8000/webhook/github"
SECRET = os.getenv("WEBHOOK_SECRET", "your_secret_here")  # Must match .env


def generate_signature(secret: str, payload: bytes) -> str:
    return "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


def send_test_event():
    # Mock GitHub Pull Request Payload
    payload_data = {
        "action": "opened",
        "repository": {
            "full_name": "himanshu2541/git-sentinel",
            "name": "git-sentinel",
            "owner": {"login": "himanshu2541"},
        },
        "number": 1, 
        "installation": {"id": 12345},
        "pull_request": {
            # This URL is just for reference in the mock, the worker constructs its own API calls
            "url": "https://api.github.com/repos/himanshu2541/git-sentinel/pulls/1",
            "title": "Test AI Reviewer",
        },
    }

    payload_bytes = json.dumps(payload_data).encode("utf-8")
    signature = generate_signature(SECRET, payload_bytes)

    headers = {
        "Content-Type": "application/json",
        "X-GitHub-Event": "pull_request",
        "X-Hub-Signature-256": signature,
    }

    print(f"Sending webhook to {WEBHOOK_URL}...")
    try:
        response = requests.post(WEBHOOK_URL, headers=headers, data=payload_bytes)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Failed to connect: {e}")


if __name__ == "__main__":
    send_test_event()
