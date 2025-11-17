import json
import re

def extract_json_from_string(text: str) -> dict | None:
    """
    Finds and parses the first valid JSON object from a string,
    even if it's embedded in a Markdown code block.

    Args:
        text: The string potentially containing a JSON object.

    Returns:
        A dictionary if a JSON object is found and parsed, otherwise None.
    """
    if not text:
        return None

    # This regex pattern looks for a Markdown JSON code block ```json ... ```
    # It uses a non-greedy match `(.+?)` to find the first complete block.
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    
    json_string = ""
    if match:
        json_string = match.group(1)
    else:
        # If no Markdown block is found, assume the whole string might be JSON,
        # or a JSON object might start with '{'.
        start_index = text.find('{')
        if start_index != -1:
            json_string = text[start_index:]
    
    if not json_string:
        return None

    try:
        # Attempt to parse the extracted string
        return json.loads(json_string)
    except json.JSONDecodeError:
        # Handle cases where the extracted string is still not valid JSON
        print("Warning: Failed to decode JSON from the extracted string.")
        return None