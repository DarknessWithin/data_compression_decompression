import os
import requests
from dotenv import load_dotenv

load_dotenv()
DEFAULT_MODEL = "meta-llama/llama-3-8b-instruct"

def generate_rich_metadata(text, api_key=None, model=DEFAULT_MODEL):
    if api_key is None:
        raise Exception("❌ API key must be provided.")

    # 🔧 System prompt ensures strict JSON output
    system_prompt = (
        "You are a strict JSON metadata generator. "
        "Respond ONLY with a JSON object. Do not use markdown, greetings, or explanations."
    )

    # 📄 Document analysis task prompt
    user_prompt = f"""
Extract the following metadata from the document below:

1. Title
2. Keywords (5–10)
3. Short Summary (2–3 lines)
4. Document Category (e.g., Legal, Academic, Finance, Resume, etc.)
5. Language
6. Sentiment (Positive, Negative, Neutral)
7. Named Entities (People, Organizations, Locations)
8. Is Confidential? (Yes/No)
9. Important Dates
10. Sections Present
11. Author
12. Intended Audience
13. Estimated Reading Time (in minutes)
14. Tables/Charts/Images Present? (Yes/No)
15. Topic Tags (e.g., ["Finance", "Resume", "Government"])
16. Summary Bullet Points

Return ONLY the metadata in raw JSON format.

Document:
{text}
    """

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 1200
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"❌ OpenRouter API error: {response.status_code}\n{response.text}")


# ✅ Main entry point
def generate_metadata(text):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise EnvironmentError("❌ OPENROUTER_API_KEY not found in environment variables.")
    return generate_rich_metadata(text, api_key=api_key)
