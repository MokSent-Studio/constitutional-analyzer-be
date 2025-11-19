import os
import google.generativeai as genai
from google.generativeai.types import generation_types
from dotenv import load_dotenv
import json

# Import our Pydantic models and our scraper function
from app.models.schemas import AnalysisRequest, FollowUpRequest
from app.services.scraper_service import fetch_and_parse_url

load_dotenv()
# --- SDK CONFIGURATION ---
# This configures the client for the entire application using the API key
# loaded from the .env file (which should be done in main.py).
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except KeyError:
    raise RuntimeError("GOOGLE_API_KEY not found. Please ensure it is set in your .env file and loaded before this module.")

# --- PRIVATE HELPER FUNCTIONS (Prompt Construction) ---

def _construct_initial_prompt(request: AnalysisRequest, document_text: str) -> str:
    """
    Dynamically assembles the initial, detailed prompt based on the user's request,
    handling optional fields gracefully.
    """
    # Start with the mandatory, non-negotiable parts of the prompt
    prompt_parts = [
        "<prompt>",
        "  <system_instructions>",
        "    You are a highly specialized AI assistant.",
        "    Your response MUST be based *only* on the text provided in the <constitutional_text> tag.",
        "    <style_guide>",
        "      1. **Tone and Persona:** Strictly adhere to the requested persona and audience.",
        "      2. **Markdown Usage:** Format the main 'analysis' text using simple Markdown (headers, bold, italics, lists).",
        "      3. **Handling Uncertainty:** If an answer to a specific question cannot be found in the text, you MUST respond with the exact phrase: \"The provided text does not contain a direct answer to this question.\"",
        "    </style_guide>",
        "    <negative_constraints>",
        "      - Do not offer any form of legal advice.",
        "      - Do not express personal opinions or interpretations.",
        "      - Do not invent or infer information not explicitly in the source text.",
        "    </negative_constraints>",
        "    <self_correction_checklist>",
        "      1. **Factual Grounding:** Is every statement supported by the <constitutional_text>?",
        "      2. **Completeness:** Have I addressed the `scope` and all `specific_questions`?",
        "      3. **Style Guide Adherence:** Does my response follow all rules?",
        "      4. **Format Compliance:** Is my final output a single, valid JSON object?",
        "    </self_correction_checklist>",
        "  </system_instructions>",
    ]

    # Conditionally add the persona and audience block if provided
    persona_parts = []
    if request.analysis_role:
        persona_parts.append(f"    <role>{request.analysis_role}</role>")
    if request.target_audience:
        persona_parts.append(f"    <audience>{request.target_audience}</audience>")
    
    if persona_parts:
        prompt_parts.append("  <persona_and_audience>")
        prompt_parts.extend(persona_parts)
        prompt_parts.append("  </persona_and_audience>")

    # Add the main constitutional text
    prompt_parts.extend([
        "  <constitutional_text>",
        f"  {document_text}",
        "  </constitutional_text>",
    ])

    # Build the user request block
    prompt_parts.append("  <user_request>")
    prompt_parts.append(f"    <scope>{request.explanation_scope.name.replace('_', ' ')}</scope>")

    # Conditionally add the specific questions block if provided
    valid_questions = [q for q in request.follow_up_questions if q.strip()]
    if valid_questions:
        questions_xml = "\n".join([f"      <question>{q}</question>" for q in valid_questions])
        prompt_parts.append("    <specific_questions>")
        prompt_parts.append(questions_xml)
        prompt_parts.append("    </specific_questions>")
    
    prompt_parts.append("  </user_request>")

    # Add the mandatory output format guide
    prompt_parts.extend([
        "  <output_format>",
        "  {",
        '    "analysis": "Your complete analysis text, formatted as a single string following all rules, goes here.",',
        '    "answered_questions": [',
        '      { "question": "The user\'s first question", "answer": "Your answer to the first question" }',
        "    ]",
        "  }",
        "  </output_format>",
        "</prompt>"
    ])
    
    return "\n".join(prompt_parts)


def _construct_follow_up_prompt(request: FollowUpRequest, full_document_text: str) -> str:
    """
    Constructs the prompt for follow-up questions using the "Dual Context" strategy.
    """
    return f"""
<prompt>
  <system_instructions>
    You are an AI assistant in a follow-up Q&A session.
    Your primary goal is to answer the user's question based on the two sources of information provided.

    <sources>
      1.  `<original_document_text>`: This is the complete, authoritative source text. This is the ultimate source of truth.
      2.  `<conversation_context>`: This is the initial analysis that has already been provided to the user.
    </sources>

    <reasoning_steps>
      1.  First, check if the `<conversation_context>` contains a sufficient answer to the user's question.
      2.  If it does not, you MUST then search the `<original_document_text>` for the specific information needed.
      3.  Formulate a concise answer based on the information you find.
    </reasoning_steps>

    <style_guide>
      - If an answer cannot be found in EITHER source, you MUST respond with the exact phrase: "The provided text does not contain a direct answer to this question."
    </style_guide>
  </system_instructions>

  <original_document_text>
  {full_document_text}
  </original_document_text>

  <conversation_context>
  {request.initial_analysis_text}
  </conversation_context>

  <user_question>
  {request.question}
  </user_question>

  <output_format>
  {{
    "answer": "Your concise, fact-based answer goes here."
  }}
  </output_format>
</prompt>
"""


# --- PUBLIC SERVICE FUNCTIONS ---

async def generate_initial_analysis(request: AnalysisRequest) -> str:
    """
    Orchestrates the initial analysis: scrapes URL, constructs prompt, calls Gemini.
    """
    print("--- Starting initial analysis generation ---")
    # 1. Scrape the content from the URL
    document_text = await fetch_and_parse_url(str(request.chapter_url))
    
    # 2. Construct the dynamic, robust prompt
    prompt = _construct_initial_prompt(request, document_text)
    
    # 3. Call the AI model (using the powerful "Pro" model for the heavy lift)
    print("Prompt constructed. Calling Gemini 2.5 Pro...")

    json_generation_config = genai.GenerationConfig(response_mime_type="application/json")

    model = genai.GenerativeModel('models/gemini-2.5-pro')
    
    try:
        response = await model.generate_content_async(prompt, generation_config=json_generation_config)
        
        if not response.parts:
            block_reason = response.prompt_feedback.block_reason.name if response.prompt_feedback else "Unknown"
            raise ValueError(f"Response was blocked for safety reasons: {block_reason}")
        
        parsed_response = json.loads(response.text)
        
        print("--- Initial analysis successful ---")
        return parsed_response
    except Exception as e:
        print(f"ERROR: An exception occurred during the Gemini API call: {e}")
        raise RuntimeError("Failed to get a valid response from the AI service.")


async def generate_follow_up_answer(request: FollowUpRequest) -> str:
    """
    Orchestrates the follow-up: re-scrapes URL, constructs dual-context prompt, calls Gemini.
    """
    print("--- Starting follow-up answer generation ---")
    # 1. Re-scrape the original URL to get the full source of truth
    full_document_text = await fetch_and_parse_url(str(request.original_url))
    
    json_generation_config = genai.GenerationConfig(response_mime_type="application/json")

    # 2. Construct the dual-context prompt
    prompt = _construct_follow_up_prompt(request, full_document_text)

    # 3. Call the AI model (using the fast "Flash" model for quick Q&A)
    print("Prompt constructed. Calling Gemini 2.0 Flash...")
    model = genai.GenerativeModel('models/gemini-2.0-flash')

    try:
        response = await model.generate_content_async(prompt, generation_config=json_generation_config)

        if not response.parts:
            block_reason = response.prompt_feedback.block_reason.name if response.prompt_feedback else "Unknown"
            raise ValueError(f"Response was blocked for safety reasons: {block_reason}")
        
        parsed_response = json.loads(response.text)
            
        print("--- Follow-up answer successful ---")
        return parsed_response
    except Exception as e:
        print(f"ERROR: An exception occurred during the Gemini API call: {e}")
        raise RuntimeError("Failed to get a valid response from the AI service for the follow-up.")