import json
import re

def safe_json_load(text: str) -> dict:
    """
    Safely extract and parse JSON from LLM output.
    Handles markdown fences and extra text.
    """
    try:
        # Remove markdown code fences if present
        cleaned = re.sub(r"```json|```", "", text).strip()

        # Extract the first JSON object
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found")

        return json.loads(match.group())

    except Exception as e:
        raise ValueError(f"Invalid JSON from agent: {e}")
