from typing import TypedDict, Literal, List

class CodeAction(TypedDict):
    action_type: Literal["CREATE", "UPDATE", "DELETE"]
    file_path: str
    code: str  # For CREATE/UPDATE, empty for DELETE
    explanation: str # The model's reasoning for this specific action

class GeminiResponse(TypedDict):
    overall_explanation: str # A high-level summary of the plan
    actions: List[CodeAction]