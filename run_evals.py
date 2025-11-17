import asyncio
import json
import google.generativeai as genai
from dotenv import load_dotenv
import os

from ai_service import generate_initial_analysis, generate_follow_up_answer
from models import AnalysisRequest, FollowUpRequest
from utils import extract_json_from_string

async def grade_initial_output(eval_case: dict, actual_output: dict) -> dict:
    """Uses Gemini to grade the main analysis output against a rubric."""
    model = genai.GenerativeModel('models/gemini-2.0-flash') # Using the updated flash model name
    
    # --- THIS IS THE CORRECTED PROMPT ---
    prompt = f"""
    <prompt>
      <system_instructions>
        You are a meticulous AI Test Engineer. Your task is to evaluate an AI's generated response by checking if it adheres to a rubric of required facts and formatting rules.
        Your final output MUST be a single, valid JSON object.

        <scoring_rubric>
          For each criterion (accuracy, completeness, tone), use the following 1-5 scale:
          1:  Completely fails to meet the criterion.
          3:  Partially meets the criterion but has significant flaws.
          5:  Perfectly meets or exceeds the criterion.
        </scoring_rubric>

        <reasoning_steps>
          1.  Read the `<ideal_output_rubric>`. For each fact in the `fact_rubric`, verify if it is present and accurately represented in the `<actual_output>`.
          2.  For each rule in the `format_rubric`, evaluate if the `<actual_output>` adheres to it.
          3.  Assign scores for accuracy, completeness, and tone based on how many rubric items were successfully met.
          4.  Write a concise, evidence-based 'reasoning' string explaining your scores.
        </reasoning_steps>
      </system_instructions>

      <user_request>
      {json.dumps(eval_case['request'], indent=2)}
      </user_request>

      <ideal_output_rubric>
      {json.dumps(eval_case['ideal_output'], indent=2)}
      </ideal_output_rubric>

      <actual_output>
      {json.dumps(actual_output, indent=2)}
      </actual_output>

      <output_format>
      {{
        "scores": {{
          "accuracy": <score_1_to_5>,
          "completeness": <score_1_to_5>,
          "tone": <score_1_to_5>
        }},
        "reasoning": "A brief, evidence-based explanation for your scores."
      }}
      </output_format>
    </prompt>
    """
    
    response = await model.generate_content_async(prompt)
    parsed = extract_json_from_string(response.text)
    return parsed if parsed else {"scores": {}, "reasoning": "Failed to parse grader response."}

async def grade_follow_up(question: str, ideal_answer: str, actual_answer: str) -> dict:
    """Uses Gemini to grade a single follow-up answer."""
    model = genai.GenerativeModel('models/gemini-2.0-flash')
    prompt = f"""
    <prompt>
    <system_instructions>
        You are a meticulous AI Test Engineer. Your task is to evaluate an AI's answer to a follow-up question against a golden "ideal answer".
        The single most important criterion is factual accuracy based on the ideal answer.
        Your final output MUST be a single, valid JSON object.

        <scoring_rubric>
        Use the following 1-5 scale for the 'score':
        1:  The answer is completely incorrect or fabricated.
        3:  The answer is partially correct but is missing key information or contains inaccuracies.
        5:  The answer is perfectly accurate and aligns completely with the ideal answer.
        </scoring_rubric>

        <reasoning_steps>
        1.  Compare the factual content of the `<actual_answer>` with the `<ideal_answer>`.
        2.  Assign a score from 1-5 based on the rubric.
        3.  Write a concise reasoning for your score.
        </reasoning_steps>
    </system_instructions>

    <user_question>
    {question}
    </user_question>

    <ideal_answer>
    {ideal_answer}
    </ideal_answer>

    <actual_answer>
    {actual_answer}
    </actual_answer>

    <output_format>
    {{
        "score": <score_1_to_5>,
        "reasoning": "A brief, evidence-based explanation for your score."
    }}
    </output_format>
    </prompt>
    """
    response = await model.generate_content_async(prompt)
    parsed = extract_json_from_string(response.text)
    return parsed if parsed else {"score": 0, "reasoning": "Failed to parse grader response."}


async def main():
    """Runs the full evaluation pipeline, including follow-ups."""
    load_dotenv()
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    
    with open('eval_dataset.json', 'r') as f:
        eval_cases = json.load(f)
        
    print("--- Starting Evaluation Pipeline ---")
    
    for case in eval_cases:
        print(f"\n--- Running Initial Eval: {case['eval_id']} ---")
        actual_initial_output = None
        try:
            request_data = {
                "chapter_url": case['request']['source_url'],
                "explanation_scope": case['request']['user_request']['scope'],
                "analysis_role": case['request']['persona_and_audience'].get('role'),
                "target_audience": case['request']['persona_and_audience'].get('audience'),
                "follow_up_questions": case['request']['user_request'].get('specific_questions', [])
            }
            request_model = AnalysisRequest(**request_data)
            
            raw_response = await generate_initial_analysis(request_model)
            actual_initial_output = extract_json_from_string(raw_response)

            # request_model = AnalysisRequest(**case['input_data'])
            # raw_response = await generate_initial_analysis(request_model)
            # actual_initial_output = extract_json_from_string(raw_response)

            if not actual_initial_output:
                print("  EVALUATION FAILED: Could not parse JSON from the initial analysis response.")
                continue

            evaluation = await grade_initial_output(case, actual_initial_output)
            print(f"  Initial Scores: {evaluation.get('scores')}")
            print(f"  Reasoning: {evaluation.get('reasoning')}")

        except Exception as e:
            print(f"  INITIAL EVALUATION FAILED with error: {e}")
            continue # If the initial analysis fails, we can't test follow-ups

        # --- NEW: RUN FOLLOW-UP EVALUATIONS ---
        if actual_initial_output and 'follow_up_evals' in case:
            print(f"  --- Running Follow-up Evals for {case['eval_id']} ---")
            for follow_up_case in case['follow_up_evals']:
                question = follow_up_case['question']
                ideal_answer = follow_up_case['ideal_answer']
                
                print(f"    Testing Question: '{question[:50]}...'")
                
                try:
                    follow_up_request = FollowUpRequest(
                        question=question,
                        initial_analysis_text=json.dumps(actual_initial_output),
                        original_url=case['request']['source_url']
                    )
                    
                    raw_follow_up_response = await generate_follow_up_answer(follow_up_request)
                    actual_follow_up_output = extract_json_from_string(raw_follow_up_response)
                    
                    if not actual_follow_up_output or 'answer' not in actual_follow_up_output:
                        print("      ERROR: Could not parse valid answer from follow-up response.")
                        continue
                        
                    actual_answer = actual_follow_up_output['answer']
                    
                    follow_up_eval = await grade_follow_up(question, ideal_answer, actual_answer)
                    print(f"      Score: {follow_up_eval.get('score')}/5")
                    print(f"      Reasoning: {follow_up_eval.get('reasoning')}")

                except Exception as e:
                    print(f"      FOLLOW-UP EVAL FAILED with error: {e}")

    print("\n--- Evaluation Pipeline Complete ---")

if __name__ == "__main__":
    asyncio.run(main())