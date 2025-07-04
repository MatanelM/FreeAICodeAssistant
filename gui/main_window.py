# gui/main_window.py
import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit
from PyQt6.QtCore import Qt, QThread
import json
from config import settings
from core.project_manager import ProjectManager
from core.file_system_manager import FileSystemManager
from core.chat_manager import ChatManager  # <-- IMPORT NEW MANAGER
from ai_client.gemini_client import GeminiClient
from ai_client.prompt_builder import build_prompt
from ai_client.response_parser import parse_gemini_response
from schemas.ai_schemas import GeminiResponse
from gui.threads import AiWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Code Assistant")
        self.setGeometry(100, 100, 800, 600)

        # Initialize core components
        self.project_manager = ProjectManager(settings.BASE_PROJECT_PATH)
        self.fs_manager = FileSystemManager(settings.BASE_PROJECT_PATH)
        self.ai_client = GeminiClient()
        self.chat_manager = ChatManager()  # <-- INSTANTIATE CHAT MANAGER
        # Threading components
        self.ai_thread = None
        self.ai_worker = None

        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Chat display area (replaces the old log_display)
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Enter your code request here...")
        self.input_box.returnPressed.connect(self.handle_send_request)  # Allow pressing Enter
        layout.addWidget(self.input_box)

        self.send_button = QPushButton("Send Request")
        self.send_button.clicked.connect(self.handle_send_request)
        layout.addWidget(self.send_button)

        self.update_chat_display("Application started. Ready for requests.")

    def handle_send_request(self):
        """Starts the AI request process on a background thread."""
        user_query = self.input_box.text().strip()
        if not user_query:
            return

        self.send_button.setEnabled(False)
        self.input_box.clear()

        # Add user message to history and update display
        self.chat_manager.add_message('user', user_query)
        self.update_chat_display()

        # Setup and start the background worker thread
        self.ai_thread = QThread()
        self.ai_worker = AiWorker(self.ai_client, self.project_manager, self.chat_manager)
        self.ai_worker.moveToThread(self.ai_thread)

        # Connect signals from the worker to slots in this main window
        self.ai_thread.started.connect(self.ai_worker.run)
        self.ai_worker.finished.connect(self.on_ai_finished)
        self.ai_worker.error.connect(self.on_ai_error)
        self.ai_worker.progress.connect(self.update_chat_display_system_message)

        # Clean up the thread and worker when they are done
        self.ai_worker.finished.connect(self.ai_thread.quit)
        self.ai_worker.error.connect(self.ai_thread.quit)
        self.ai_thread.finished.connect(self.ai_thread.deleteLater)
        self.ai_worker.finished.connect(self.ai_worker.deleteLater)
        self.ai_worker.error.connect(self.ai_worker.deleteLater)

        self.ai_thread.start()

    def update_chat_display_system_message(self, message: str):
        """Slot to display progress updates from the worker."""
        self.update_chat_display(f"[System]: {message}")

    def on_ai_error(self, error_message: str):
        """Slot to handle errors from the worker."""
        self.update_chat_display_system_message(f"ERROR: {error_message}")
        self.send_button.setEnabled(True)
        self.input_box.setFocus()

    def on_ai_finished(self, parsed_response: dict):
        """Slot to handle the successful completion of the AI task."""
        self.update_chat_display_system_message("AI task complete. Applying changes...")

        # Add AI's JSON response to history (as a string)
        self.chat_manager.add_message('model', parsed_response['overall_explanation'])

        self.update_chat_display()  # Redraw chat with the new AI message

        # Clean paths (same logic as before)
        root_folder_name = os.path.basename(self.project_manager.base_path)
        for action in parsed_response['actions']:
            path_to_check = action['file_path']
            if path_to_check.replace('\\', '/').startswith(f"{root_folder_name}/"):
                action['file_path'] = action['file_path'][len(root_folder_name) + 1:]

        # Execute actions
        for action in parsed_response['actions']:
            success = self.fs_manager.apply_action(action)
            if not success:
                self.update_chat_display_system_message(
                    f"Stopped due to error applying action on {action['file_path']}")
                break

        self.update_chat_display_system_message("Done. Ready for next request.")
        self.send_button.setEnabled(True)
        self.input_box.setFocus()

    def update_chat_display(self, system_message: str = None):
        """Clears and redraws the chat display from the now-clean history."""
        self.chat_display.clear()

        for message in self.chat_manager.history:
            role = message['role']
            content = message['content'].replace('\n', '<br>')
            if role == 'user':
                self.chat_display.append(f"<b>You:</b> {content}")
            else:  # role == 'model'
                self.chat_display.append(f"<b>AI:</b> {content}")
            self.chat_display.append("")

        if system_message:
            self.chat_display.append(f"<i>{system_message}</i>")

        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())
        QApplication.processEvents()