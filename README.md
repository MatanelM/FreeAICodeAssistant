# Gemini AI Coding Assistant

An AI assistant that uses Google Gemini to automatically write and modify code in your local project.

▶️ **[Watch the Demo Video]**
[input.webm](https://github.com/user-attachments/assets/e455b0c8-c3eb-4134-a2ee-47bc43b339a3)


---

## ⚠️ **CRITICAL WARNING**

This AI has permission to **modify and delete your files**. It can and will make mistakes.

*   **ALWAYS use this on a project with version control (Git).**
*   **Commit your work before running commands.** 

---

## 🚀 Quick Start

### 1. Install

Clone the repository and install the dependencies.
```
git clone https://github.com/MatanelM/FreeAICodeAssistant
cd FreeAICodeAssistant
pip install -r requirements.txt
```
### 2. Configure

Open config/settings.py and set these two variables:

```
# config/settings.py

# 1. Add your API key from Google AI Studio
GOOGLE_API_KEY="YOUR_GEMINI_API_KEY_HERE"

# 2. Set the ABSOLUTE path to the project you want the AI to edit
#    Example Linux/macOS: "/home/user/projects/my-app"
#    Example Windows: "C:/Users/user/Projects/my-app"
BASE_PROJECT_PATH = "/path/to/your/code"
```
# 3. Run

Start the assistant and give it instructions in plain English.

That's it!

