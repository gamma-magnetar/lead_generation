import os
import requests
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from together import Together  # type: ignore
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

# Load API key from .env
load_dotenv()
client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

# Extract and clean website text
def extract_text_from_url(url, max_chars=4000):
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "meta", "link", "svg", "footer", "nav", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r"\s+", " ", text)
        return text[:max_chars]
    except Exception as e:
        logging.warning(f"Error fetching content from {url}: {e}")
        return None

# Classify website using DeepSeek
def classify_website(text):
    prompt = f"""
You are a lead qualification agent.

Based on this website content:
---
{text}
---

Is this a real business website?

Answer with only one of:
- Real Business
- Placeholder / Parked
- Junk / Spam
"""

    try:
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        # Safely access content
        message = response.choices[0].message if response.choices else None # type: ignore
        reply = message.content.strip().lower() if message and message.content else "" # type: ignore

        if "real" in reply:
            return "real_business"
        elif "placeholder" in reply or "parked" in reply:
            return "placeholder"
        elif "junk" in reply or "spam" in reply:
            return "junk_or_unclear"
        else:
            return "llm_unclear"

    except Exception as e:
        logging.warning(f"DeepSeek error: {e}")
        return "llm_error"

# Example (only for manual testing)
if __name__ == "__main__":
    test_url = input("Enter website URL: ").strip()
    content = extract_text_from_url(test_url)
    if content:
        result = classify_website(content)
        print(f"\n✅ Classification for {test_url}: {result}")
    else:
        print("❌ Could not extract content from the site.")
