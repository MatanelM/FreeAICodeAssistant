# ai_client/prompt_builder.py

def build_prompt(project_structure_str: str, user_query: str, conversation_history_str: str, relevant_files: dict[str, str] | None = None) -> str:
    """
    Constructs a highly focused and clean prompt.
    It provides file content as the primary context for modifications.
    """
    # Build the file contents string. This is now the most important context.
    file_contents_str = ""
    if relevant_files:
        file_contents_str = "--- Relevant File Contents ---\n"
        for path, content in relevant_files.items():
            file_contents_str += f"File: {path}\n```\n{content}\n```\n\n"
    else:
        file_contents_str = "No specific files were provided for context.\n"

    final_prompt = f"""
You are CodeGenius, an expert AI programming assistant. Your task is to generate a JSON object describing file modifications to fulfill the user's request.

--- CORE INSTRUCTIONS ---
1.  Your response MUST be a single, valid JSON object. The API enforces the schema.
2.  Analyze the user's request, the project tree, the conversation history, and ESPECIALLY the provided file contents.
3.  Be direct and factual. Do not comment on your own process.

--- CONTEXT ---
Project Tree:
{project_structure_str}

{file_contents_str}
Conversation History (for context on follow-up questions):
{conversation_history_str}
--- END CONTEXT ---

User Request: "{user_query}"

Generate the JSON response describing the actions to take.
"""
    return final_prompt