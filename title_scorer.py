import os
import time
from dotenv import load_dotenv
from together import Together # type: ignore

# Load API key
load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
client = Together(api_key=TOGETHER_API_KEY)

def get_title_score_llm(title, target_role, max_retries=5):
    prompt = f"""You are a recruiting assistant. A user is searching for leads with the role: '{target_role}'.
How relevant is this job title to their search: '{title}'?

Give a numeric score from 0 to 100 where:
- 100 = exact match
- 80 = very similar
- 50 = somewhat relevant
- 0 = unrelated

Only respond with a single number. No explanation."""

    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model="deepseek-ai/DeepSeek-V3",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=10
            )
            reply = response.choices[0].message.content.strip() # type: ignore
            score = int(''.join(filter(str.isdigit, reply)))
            if 0 <= score <= 100:
                return score
        except Exception as e:
            print(f"[Retry {attempt+1}/{max_retries}] LLM error: {e}")
            time.sleep(1)

    return 0  # Fallback if all retries fail
