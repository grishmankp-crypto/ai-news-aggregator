from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

models = client.models.list()
print("Available Groq models:")
for m in sorted(models.data, key=lambda x: x.id):
    print(" -", m.id)
