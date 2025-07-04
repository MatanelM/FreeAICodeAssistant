# core/project_manager.py
import os
from config import settings


class ProjectManager:
    def __init__(self, base_path: str):
        if not os.path.isdir(base_path):
            raise ValueError(f"The provided path '{base_path}' is not a valid directory.")
        self.base_path = os.path.abspath(base_path)
        self.ignored = settings.IGNORED_PATH

    def get_structure_string(self) -> str:
        """Generates a string representation of the project's file tree."""
        lines = []

        def recurse(path, indent="", is_last_dict=None):
            if os.path.basename(path) in self.ignored:
                return

            real_path = os.path.realpath(path)
            base_name = os.path.basename(real_path)

            if indent == "":  # Root directory
                lines.append(f"{base_name}/")
            else:
                connector = "└── " if is_last_dict.get(path, False) else "├── "
                lines.append(f"{indent}{connector}{base_name}{'/' if os.path.isdir(path) else ''}")

            if os.path.isdir(path):
                next_indent = indent + ("    " if is_last_dict.get(path, False) else "│   ")
                try:
                    entries = [os.path.join(path, e) for e in sorted(os.listdir(path)) if e not in self.ignored]
                    is_last_map = {entries[-1]: True} if entries else {}
                    for entry_path in entries:
                        recurse(entry_path, next_indent, is_last_map)
                except PermissionError:
                    lines.append(f"{next_indent}[Permission Denied]")

        recurse(self.base_path, is_last_dict={})
        return "\n".join(lines)

    def read_file(self, relative_path: str) -> str | None:
        """Reads the content of a file, given a path relative to the project root."""
        full_path = os.path.join(self.base_path, relative_path)
        # Security check
        if not self._is_path_safe(full_path):
            print(f"Error: Attempt to read file outside of project directory: {relative_path}")
            return None

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Error reading file {relative_path}: {e}")
            return None

    def _is_path_safe(self, path: str) -> bool:
        """Ensures the path is within the project's base directory."""
        return os.path.abspath(path).startswith(self.base_path)