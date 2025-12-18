import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
with open('models.txt', 'w') as f:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        f.write("No GEMINI_API_KEY found")
    else:
        genai.configure(api_key=api_key)
        try:
            f.write("Listing available models:\n")
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    f.write(f"{m.name}\n")
        except Exception as e:
            f.write(f"Error listing models: {e}")
