# gui/threads.py
from PyQt6.QtCore import QObject, pyqtSignal
from ai_client.prompt_builder import build_prompt
from ai_client.response_parser import parse_gemini_response
from schemas.ai_schemas import GeminiResponse


class AiWorker(QObject):
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, ai_client, project_manager, chat_manager):
        super().__init__()
        self.ai_client = ai_client
        self.project_manager = project_manager
        self.chat_manager = chat_manager

    def find_relevant_files(self, query: str) -> dict[str, str]:
        """
        !!! INTELLIGENCE PLACEHOLDER !!!
        This is where the app will get smart. It should parse the query
        for filenames and read them.

        For now, we will keep it simple and not read any files.
        In a future version, you could use another LLM call or regex to find filenames.
        """
        # Example of what this *could* do later:
        # import re
        # filenames = re.findall(r'(\w+\.py)', query)
        # relevant_files = {}
        # for filename in filenames:
        #     content = self.project_manager.read_file(filename)
        #     if content:
        #         relevant_files[filename] = content
        # return relevant_files
        return {}

    def run(self):
        try:
            user_query = self.chat_manager.history[-1]['content']

            self.progress.emit("Analyzing request...")
            structure_str = self.project_manager.get_structure_string()
            history_str = self.chat_manager.get_formatted_history()

            # --- The "Ground Truth" Step ---
            # Find and read any files mentioned in the query.
            relevant_files = self.find_relevant_files(user_query)
            if relevant_files:
                self.progress.emit(f"Reading relevant files: {', '.join(relevant_files.keys())}")

            self.progress.emit("Building prompt for AI...")
            prompt = build_prompt(structure_str, user_query, history_str, relevant_files)

            self.progress.emit("Sending request to Gemini (this may take a moment)...")
            ai_response_str = self.ai_client.generate_response(prompt, schema=GeminiResponse)
            if not ai_response_str:
                raise ValueError("Received an empty response from the API.")

            self.progress.emit("Parsing AI response...")
            parsed_response = parse_gemini_response(ai_response_str)
            if not parsed_response:
                raise ValueError("Failed to parse a valid JSON object from the AI's response.")

            self.finished.emit(parsed_response)
        except Exception as e:
            self.error.emit(f"An error occurred in the AI worker thread: {e}")