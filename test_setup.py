import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Error: API Key not found!")
else:
    try:
        client = genai.Client(api_key=api_key)
        
        # ✅ WE FOUND IT! Using the official Hackathon model from your list:
        MODEL_ID = "gemini-3-flash-preview" 

        print(f"🤖 Connecting to {MODEL_ID}...")
        
        response = client.models.generate_content(
            model=MODEL_ID, 
            contents="Hello Gemini 3! Are you ready to analyze some contracts?"
        )
        
        print("\n🎉 GEMINI 3 SUCCESS!")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")