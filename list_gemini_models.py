import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure the API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY not found in .env file.")
    print("Please set GOOGLE_API_KEY='your_api_key_here' in your .env file.")
    exit()

genai.configure(api_key=GOOGLE_API_KEY)

print("Available Gemini models:")
for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print(f"- {m.name}")
