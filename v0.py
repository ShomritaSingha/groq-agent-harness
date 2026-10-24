import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # so emoji don't crash the Windows console

from dotenv import load_dotenv
from groq import Groq

# Load .env next to this script, then read GROQ_API_KEY from the environment.
load_dotenv(Path(__file__).with_name(".env"))
client = Groq()

MODEL = "openai/gpt-oss-120b"

def chat(user_message: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful personal assistant."},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content or ""

# chat('what is 2+2?')
# chat('what is 2+8?')

# print(chat('what is 2+2?'))

# print("First answer:", chat("what does the cat say?"))
# print("Second answer:", chat("what is 2+8?"))
if __name__ == "__main__":
    print(f"v0 assistant ({MODEL}) - ctrl+c to quit")
    try:
        while True:
            question = input("\nyou: ")
            print("\nassistant:", chat(question))
    except (EOFError, KeyboardInterrupt):
        print("\nbye!")


