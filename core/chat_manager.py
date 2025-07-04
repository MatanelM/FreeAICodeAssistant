# core/chat_manager.py
from typing import List, Dict


class ChatManager:
    """Manages the state of the conversation history."""

    def __init__(self):
        # History will be a list of message dictionaries
        # e.g., [{'role': 'user', 'content': '...'}, {'role': 'model', 'content': '...'}]
        self.history: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str):
        """Adds a new message to the conversation history."""
        # Basic validation
        if role not in ['user', 'model']:
            raise ValueError("Role must be 'user' or 'model'")
        self.history.append({'role': role, 'content': content})

    def get_formatted_history(self) -> str:
        """Formats the history into a simple, clean, plain-text format."""
        if not self.history:
            return "No previous conversation history."

        # We only want to show the last few turns to keep the prompt clean
        # You can adjust this number.
        recent_history = self.history[-6:]

        formatted_lines = []
        for msg in recent_history:
            role = msg['role'].upper()
            content = msg['content']
            formatted_lines.append(f"{role}: {content}")

        return "\n".join(formatted_lines)

    def clear_history(self):
        """Resets the conversation."""
        self.history = []