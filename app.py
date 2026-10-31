import os
import base64
import requests
import gradio as gr
from google import genai

# Environment variables se keys utha. Hardcode mat kar.
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "") # GitHub PAT for higher rate limits

# Client initialize kar
client = genai.Client(api_key=GEMINI_API_KEY)

def get_file_score(path):
    """
    Files ko prioritize karne ka smart logic.
    Core logic files ko high score milega, tests aur config ko low.
    """
    path_lower = path.lower()
    score = 0
    # Important folders
    if any(x in path_lower for x in ['src/', 'app/', 'lib/', 'core/']): 
        score += 10
    # Entry point files
    if any(x in path_lower for x in ['main.', 'index.', 'app.', 'server.', 'core.']): 
        score += 20
    # Context ke liye README zaroori hai
    if 'readme' in path_lower: 
        score += 15
    # Tests usually architecture explain nahi karte, token waste karte hain
    if 'test' in path_lower or 'spec' in path_lower: 
        score -= 5
    return score

def analyze_full_github_repo(repo_url):
    try:
        # 1. Solid URL Parsing (handles .git at the end too)
        clean_url = repo_url.strip().rstrip('/')
        if clean_url.endswith('.git'):
            clean_url = clean_url[:-4]
            
        parts = clean_url.split('/')
        if len(parts) < 2:
            return "Error: Invalid GitHub URL format. Use like: https://github.com/owner/repo"
        
        owner, repo = parts[-2], parts[-1]
        
        # Connection pooling for faster multiple requests
        session = requests.Session()
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'CodeArchitect-Bot/1.0'
        }
        if GITHUB_TOKEN:
            headers['Authorization'] = f"token {GITHUB_TOKEN}"
        session.headers.update(headers)
        
        # 2. Fetch Tree
        tree_api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1"
        response = session.get(tree_api_url, timeout=15)
        
        # Fallback to master if main doesn't exist
        if response.status_code != 200:
            tree_api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/master?recursive=1"
            response = session.get(tree_api_url, timeout=15)
            
        if response.status_code != 200:
            return f"Error: Could not fetch repository tree. Status Code: {response.status_code}. Make sure the repo is public."
            
        tree_data = response.json().get('tree', [])
        
        # 3. Smart Filtering & Priority Sorting
        valid_extensions = ('.py', '.js', '.ts', '.java', '.cpp', '.json', '.md', '.txt', '.go', '.rs')
        ignore_dirs = ('node_modules', 'venv', '.git', 'dist', 'build', '__pycache__', 'images', 'assets')
        
        valid_files = []
        for item in tree_data:
            path = item.get('path', '')
            if item.get('type') == 'blob':
                # Ignore unwanted folders completely
                if any(ignored in path.lower() for ignored in ignore_dirs):
                    continue
                # Pick valid extensions or config files
                if path.endswith(valid_extensions) or 'config' in path.lower() or 'readme' in path.lower():
                    valid_files.append(path)
                    
        if not valid_files:
            return "Error: No relevant source code files found in this repository."

        # Score aur sort files based on importance
        valid_files.sort(key=get_file_score, reverse=True)
        
        # Ab purely top 10 core files uthayega, kachra nahi
        code_files = valid_files[:10]
        
        # 4. Fetch Content efficiently
        combined_code_content = f"Repository: {owner}/{repo}\n\n=== CORE FILE STRUCTURE SUMMARY ===\n"
        for f in code_files:
            combined_code_content += f"- {f}\n"
        combined_code_content += "\n=== FILE CONTENTS ===\n"
        
        for file_path in code_files:
            file_api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
            file_resp = session.get(file_api_url, timeout=10)
            
            if file_resp.status_code == 200:
                file_data = file_resp.json()
                if 'content' in file_data:
                    decoded_bytes = base64.b64decode(file_data['content'])
                    file_text = decoded_bytes.decode('utf-8', errors='ignore')
                    
                    combined_code_content += f"\n--- FILE: {file_path} ---\n"
                    # Smart Truncation: Tell AI exactly if the file was cut
                    if len(file_text) > 3000:
                        combined_code_content += file_text[:3000] + "\n\n...[CONTENT TRUNCATED DUE TO SIZE LIMIT]...\n"
                    else:
                        combined_code_content += file_text + "\n"
                        
        # 5. AI Prompt & Execution
        prompt = f"""
        Act as an expert Senior Code Architect. You have been provided with the actual source code files and structure of a GitHub repository.
        
        {combined_code_content}
        
        Perform a deep architectural analysis and provide a structured breakdown in Markdown format:
        1. **Deep Codebase Overview & Tech Stack**: Languages, core frameworks, and architecture pattern used.
        2. **Entry Point & Execution Flow**: Exactly where execution starts and how data flows through these files.
        3. **Module Dependencies**: How different modules/files interact with each other.
        4. **Key Functions & Logic**: Summary of core logic implemented across these files.
        5. **Execution Flow Graph (Mermaid.js syntax)**: Provide a clean Mermaid.js flowchart code block (` ```mermaid ... ``` `) mapping the actual file dependencies and flow.
        """
        
        # Dhyan rakh: 'gemma-4-26b-a4b-it' native GenAI pe shayad properly mapped nahi hoga. 
        # Agar error aaye, toh 'gemini-2.0-flash' use kar liyo.
        ai_response = client.models.generate_content(
            model='gemini-2.0-flash', 
            contents=prompt
        )
        return ai_response.text
        
    except Exception as e:
        return f"Deep Analysis Error: {str(e)}"

# Gradio UI Design
demo = gr.Interface(
    fn=analyze_full_github_repo,
    inputs=gr.Textbox(
        label="Enter Public GitHub Repository URL:",
        placeholder="https://github.com/owner/repo"
    ),
    outputs=gr.Markdown(label="Deep Codebase Analysis & Execution Flow Graph:"),
    title="GitHub Deep Codebase Visualizer & Analyzer",
    description="Fetches prioritized repository core files via GitHub API and maps full architectural execution flows."
)

if __name__ == "__main__":
    demo.launch()