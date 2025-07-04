# ai_client/response_parser.py
import json
from typing import Optional
from schemas.ai_schemas import GeminiResponse


def parse_gemini_response(response_text: str) -> Optional[GeminiResponse]:
    """
    Parses the raw string from the Gemini API into a GeminiResponse TypedDict.

    This version is more robust: it finds the main JSON block within the
    response text, ignoring potential markdown wrappers or conversational text.
    """
    try:
        # Find the first '{' and the last '}' to isolate the JSON block.
        # This is more reliable than just stripping markdown.
        start_index = response_text.find('{')
        end_index = response_text.rfind('}')

        if start_index == -1 or end_index == -1 or end_index < start_index:
            print("Error: Could not find a valid JSON object within the response.")
            print(f"--- Received Text ---\n{response_text}\n---------------------")
            return None

        # Extract the JSON substring
        json_str = response_text[start_index: end_index + 1]

        data = json.loads(json_str)

        # Validation to ensure the parsed data matches our schema's structure
        if "overall_explanation" not in data or "actions" not in data:
            print("Error: Parsed JSON is missing required keys ('overall_explanation', 'actions').")
            return None

        for action in data["actions"]:
            if not all(k in action for k in ["action_type", "file_path", "code", "explanation"]):
                print(f"Error: An action is missing required keys. Action: {action}")
                return None

        # If everything looks good, we return the structured data.
        # The **data syntax unpacks the dictionary into arguments for the TypedDict.
        return GeminiResponse(**data)

    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON from the extracted text: {e}")
        print(f"--- Extracted Text ---\n{json_str}\n---------------------")
        return None
    except TypeError as e:
        print(f"Error: JSON structure does not match GeminiResponse TypedDict: {e}")
        print(f"--- Parsed Data ---\n{data}\n---------------------")
        return None