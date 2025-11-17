import os
import google.generativeai as genai
from dotenv import load_dotenv

def list_available_models():
    """
    Connects to the Gemini API and lists the models you have access to.
    """
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found.")
        return

    try:
        genai.configure(api_key=api_key)

        print("--- Available Gemini Models ---")
        for model in genai.list_models():
            # The 'generateContent' method is what we use for standard text prompts.
            if 'generateContent' in model.supported_generation_methods:
                print(f"- {model.name}")
        print("-----------------------------")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    list_available_models()