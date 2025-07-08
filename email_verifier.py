import os
import requests
from dotenv import load_dotenv

# Load NeverBounce API key from environment
load_dotenv()
NEVERBOUNCE_API_KEY = os.getenv("NEVERBOUNCE_API_KEY")

def verify_email_neverbounce(email: str) -> dict:
    if not email or "@" not in email:
        return {
            "email_status": "invalid_format",
            "is_valid_email": False,
            "suggested_correction": None
        }

    url = "https://api.neverbounce.com/v4/single/check"
    params = {
        "email": email,
        "key": NEVERBOUNCE_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                result = data.get("result", "unknown")
                return {
                    "email_status": result,  # valid, invalid, disposable, catchall, unknown
                    "is_valid_email": result == "valid",
                    "suggested_correction": data.get("suggested_correction")
                }

        # Fallback for unexpected cases
        return {
            "email_status": "invalid",
            "is_valid_email": False,
            "suggested_correction": None
        }

    except Exception as e:
        print(f"Email verification error for {email}: {e}")
        return {
            "email_status": "invalid",
            "is_valid_email": False,
            "suggested_correction": None
        }
