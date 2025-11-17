import os
import google.generativeai as genai
from dotenv import load_dotenv

def run_gemini_test():
    """
    A simple function to connect to Gemini and get a response.
    """
    # 1. Load Environment Variables
    # This line reads the GOOGLE_API_KEY from our .env file.
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found. Please set it in your .env file.")
        return

    print("API Key loaded successfully.")

    try:
        # 2. Configure the SDK
        # This tells the SDK which key to use for all future requests.
        genai.configure(api_key=api_key)

        # 3. Instantiate the Model
        # We create an instance of the Gemini model we want to use.
        print("Connecting to Gemini Pro...")
        model = genai.GenerativeModel('models/gemini-2.0-flash')

        # 4. Define a Simple Prompt
        prompt = "Hello! In one sentence, what is the purpose of a constitution?"

        print(f"Sending prompt: '{prompt}'")

        # 5. Generate Content
        # This is the actual API call to Google.
        response = model.generate_content(prompt)

        # 6. Print the Result
        # The AI's response is in the .text attribute.
        print("\n--- Gemini's Response ---")
        print(response.text)
        print("-------------------------\n")
        print("Test successful!")

    except Exception as e:
        # This will catch any errors during the API call, like a bad key or network issue.
        print(f"\nAn error occurred: {e}")

# This is the standard way to make a Python script runnable
if __name__ == "__main__":
    run_gemini_test()