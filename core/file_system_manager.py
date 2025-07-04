import os, sys
from config.settings import BASE_PROJECT_PATH, IGNORED_PATH

# core/file_system_manager.py
import os
from schemas.ai_schemas import CodeAction


class FileSystemManager:
    def __init__(self, base_path: str):
        self.base_path = os.path.abspath(base_path)

    def _is_path_safe(self, target_path: str) -> bool:
        """
        SECURITY: Crucial check to ensure we don't modify files outside the project directory.
        """
        # Get the absolute path of the target file/folder
        abs_target_path = os.path.abspath(target_path)
        # Check if the absolute target path starts with the project's absolute base path
        return abs_target_path.startswith(self.base_path)

    def apply_action(self, action: CodeAction) -> bool:
        """
        Executes a single CodeAction (CREATE, UPDATE, DELETE).
        Returns True on success, False on failure.
        """
        file_path = os.path.join(self.base_path, action['file_path'])

        if not self._is_path_safe(file_path):
            print(f"SECURITY ERROR: Action blocked. Attempted to modify path outside of project: {action['file_path']}")
            return False

        action_type = action['action_type']

        try:
            if action_type == "CREATE":
                # Ensure parent directory exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(action['code'])
                print(f"CREATED: {action['file_path']}")

            elif action_type == "UPDATE":
                if not os.path.exists(file_path):
                    print(f"ERROR: Cannot update non-existent file: {action['file_path']}")
                    return False
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(action['code'])
                print(f"UPDATED: {action['file_path']}")

            elif action_type == "DELETE":
                if not os.path.exists(file_path):
                    print(f"ERROR: Cannot delete non-existent file: {action['file_path']}")
                    return False
                os.remove(file_path)
                print(f"DELETED: {action['file_path']}")

            else:
                print(f"ERROR: Unknown action type '{action_type}'")
                return False

            return True

        except Exception as e:
            print(f"ERROR performing '{action_type}' on '{action['file_path']}': {e}")
            return False

def get_project_structure(base_path=BASE_PROJECT_PATH, indent=""):
    """
    Returns the nested structure of folders and files starting from base_path.

    Structure format:
    ['folder_name', [...contents...]]
    ['file_name']
    """

    def walk_dir(current_path):
        items = []
        for entry in sorted(os.listdir(current_path)):
            if entry in IGNORED_PATH:continue
            full_path = os.path.join(current_path, entry)
            if os.path.isdir(full_path):
                items.append([entry, walk_dir(full_path)])  # Recursive call for folders
            else:
                items.append([entry])  # Files are leaves
        return items

    return [os.path.basename(base_path), walk_dir(base_path)]


def print_project_structure(base_path=BASE_PROJECT_PATH, indent="", visited=None, root=True):
    if visited is None:
        visited = set()

    real_path = os.path.realpath(base_path)
    if real_path in visited:
        return  # avoid cycles or duplicate visits
    visited.add(real_path)

    base_name = os.path.basename(base_path.rstrip(os.sep))
    if root:
        print(f"{indent}{base_name}/")
    try:
        entries = sorted(os.listdir(base_path))
    except PermissionError:
        print(f"{indent} [Permission Denied]")
        return
    total = len(entries)
    for index, entry in enumerate(entries):
        if entry in IGNORED_PATH: continue
        full_path = os.path.join(base_path, entry)
        is_last = index == total - 1
        connector = "└── " if is_last else "├── "
        next_indent = indent + ("    " if is_last else "│   ")
        if os.path.isdir(full_path) and not os.path.islink(full_path):
            print(f"{indent}{connector}{entry}/")
            print_project_structure(full_path, indent=next_indent, visited=visited, root=False)
        else:
            print(f"{indent}{connector}{entry}")



def get_project_structure_str(base_path=BASE_PROJECT_PATH, indent="", visited=None, root=True, ignored=IGNORED_PATH):
    if visited is None:
        visited = set()
    if ignored is None:
        ignored = set()

    lines = []

    real_path = os.path.realpath(base_path)
    if real_path in visited:
        return ""  # avoid cycles or duplicate visits
    visited.add(real_path)

    base_name = os.path.basename(base_path.rstrip(os.sep))
    if root:
        lines.append(f"{indent}{base_name}/")

    try:
        entries = [e for e in sorted(os.listdir(base_path)) if e not in ignored]
    except PermissionError:
        lines.append(f"{indent}[Permission Denied]")
        return "\n".join(lines)

    total = len(entries)
    for index, entry in enumerate(entries):
        full_path = os.path.join(base_path, entry)
        is_last = index == total - 1
        connector = "└── " if is_last else "├── "
        next_indent = indent + ("    " if is_last else "│   ")

        if os.path.isdir(full_path) and not os.path.islink(full_path):
            lines.append(f"{indent}{connector}{entry}/")
            sub_structure = get_project_structure_str(full_path, next_indent, visited, root=False, ignored=ignored)
            if sub_structure:
                lines.append(sub_structure)
        else:
            lines.append(f"{indent}{connector}{entry}")

    return "\n".join(lines)
