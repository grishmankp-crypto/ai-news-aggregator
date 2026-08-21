from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

models_to_test = ["openai/gpt-oss-20b", "qwen/qwen3.6-27b", "groq/compound-mini"]

for m in models_to_test:
    try:
        res = client.chat.completions.create(
            model=m,
            messages=[{"role": "user", "content": "Respond with: OK"}],
            max_tokens=10
        )
        print(f"SUCCESS with {m}: {res.choices[0].message.content.strip()}")
    except Exception as e:
        print(f"FAILED with {m}: {e}")
