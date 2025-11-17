import asyncio
import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

# Ensure the root directory is on the Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import our scraper function
from scraper_service import fetch_and_parse_url

async def main():
    """
    Tests the full end-to-end flow:
    1. Scrapes a URL for context.
    2. Engineers a prompt with that context.
    3. Sends the prompt to the Gemini API.
    4. Prints the final analysis.
    """
    print("--- Starting Full Integration Test ---")

    # --- Part 1: Configuration ---
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found.")
        return
    genai.configure(api_key=api_key)

    # --- Part 2: Context Engineering (Scraping) ---
    test_url = "https://www.gov.za/documents/constitution/chapter-2-bill-rights"
    document_text = ""
    try:
        document_text = await fetch_and_parse_url(test_url)
        print(f"Scraping successful. Extracted {len(document_text)} characters.")
    except RuntimeError as e:
        print(f"Scraping failed: {e}")
        return # Exit if we can't get the context

    # --- Part 3: Prompt Engineering ---
    # We'll use hardcoded values for the test, just like our frontend would provide
    analysis_role = "Constitutional Law Professor"
    target_audience = "a first-year university student"
    explanation_scope_text = "a concise, single-paragraph overview of the entire chapter's purpose and key themes"
    
    # This is the prompt template we designed
    prompt = f"""
    <prompt>
    <system_instructions>
        You are a highly specialized AI assistant. Your function is to analyze a provided legal text and generate a structured response based on user-defined parameters.
        Your response MUST be based *only* on the text provided in the <constitutional_text> tag. Do not use any external knowledge.
        Your final output MUST be a single, valid JSON object. Do not include any text or formatting outside of the JSON structure.

        <style_guide>
        1.  **Tone and Persona:** Strictly adhere to the requested <role> and <audience>. The tone should be formal, neutral, and academic.
        2.  **Clarity:** Use clear and direct language. Avoid jargon where possible, unless appropriate for the requested persona.
        3.  **Markdown Usage:** Format the main 'analysis' text using simple Markdown. You MAY use headers (#, ##), bold (**text**), italics (*text*), and unordered lists (- item). Do NOT use blockquotes or tables.
        4.  **Citations:** Do NOT add citations or references unless they are explicitly present in the provided <constitutional_text>.
        5.  **Handling Uncertainty:** If an answer to a specific question cannot be found within the <constitutional_text>, you MUST respond with the exact phrase: "The provided text does not contain a direct answer to this question." Do not attempt to infer or guess the answer.
        </style_guide>

        <negative_constraints>
            - Do not offer any form of legal advice.
            - Do not express personal opinions or interpretations.
            - Do not invent or infer information that is not explicitly in the source text.
            - Do not use overly emotional or persuasive language.
        </negative_constraints>

        Before generating the final JSON output, perform a self-correction step.
        Review your drafted response against this checklist and ensure it complies with every rule:
        <self_correction_checklist>
            1.  **Factual Grounding:** Is every statement in my analysis directly supported by the provided `<constitutional_text>`?
            2.  **Completeness:** Have I addressed both the `scope` and all `specific_questions` from the `<user_request>`?
            3.  **Style Guide Adherence:** Does my response follow all rules in the `<style_guide>`, especially the rule on handling uncertainty?
            4.  **Negative Constraints:** Have I avoided all forbidden actions listed in the `<negative_constraints>`?
            5.  **Format Compliance:** Is my final output a single, valid JSON object with no extra text?
        </self_correction_checklist>
            </system_instructions>

    <persona_and_audience>
        <role>{analysis_role}</role>
        <audience>{target_audience}</audience>
    </persona_and_audience>
    
    <constitutional_text>
    {document_text}
    </constitutional_text>
    
    <user_request>
        <scope>{explanation_scope_text}</scope>
        <specific_questions>
            <question>What are the limitations placed on the right to freedom of expression in section 16?</question>
            <question>How does the constitution define "equality" in section 9?</question>
            <question>Explain the process for declaring a state of emergency according to section 37.</question>
        </specific_questions>
    </user_request>
    
    <output_format>
    {{
        "analysis": "Your complete analysis text, formatted as a single string following the style guide, goes here.",
        "answered_questions": [
        {{ "question": "The user's first question", "answer": "Your answer to the first question" }},
        {{ "question": "The user's second question", "answer": "Your answer to the second question" }}
        ]
    }}
    </output_format>
    </prompt>"""

    print("\n--- Prompt Assembled. Sending to Gemini... ---")

    # --- Part 4: AI Generation ---
    try:
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        response = await model.generate_content_async(prompt) # Use async for consistency
        
        print("\n\n--- INTEGRATION TEST SUCCESSFUL ---")
        print("--- Final AI Analysis: ---")
        print(response.text)
        print("--------------------------")

    except Exception as e:
        print(f"\n--- AI Generation Failed ---")
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())