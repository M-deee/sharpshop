# filepath: test_api.py (create this file in the root directory)
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
base_url = "https://openrouter.ai/api/v1"
model = "meta-llama/llama-3.3-70b-instruct:free"

if not api_key:
    print("❌ API key not found in .env")
    exit(1)

client = OpenAI(base_url=base_url, api_key=api_key)

try:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Hello"}],
        temperature=0.7
    )
    print("✅ API key works! Response:", response.choices[0].message.content)
except Exception as e:
    print("❌ API error:", e)