# smoke.py
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

response = client.messages.create(
    model=MODEL,
    max_tokens=100,
    messages=[{"role": "user", "content": "Say hi in 5 words."}]
)
print(response.content[0].text)