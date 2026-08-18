from dotenv import load_dotenv
import os

load_dotenv()

gemini_key = os.getenv("GEMINI_API_KEY")
composio_key = os.getenv("COMPOSIO_API_KEY")

print("Gemini key loaded:", bool(gemini_key))
print("Composio key loaded:", bool(composio_key))

groq_key = os.getenv("GROQ_API_KEY")
print("Groq key loaded:", bool(groq_key))