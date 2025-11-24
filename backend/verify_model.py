import google.generativeai as genai
from app.config.settings import settings
import asyncio

async def verify_model():
    print(f"Testing with model: {settings.GEMINI_MODEL}")
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    try:
        response = model.generate_content("Hello, are you working?")
        print(f"Success! Response: {response.text[:50]}...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_model())
