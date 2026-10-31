import os
import base64
import re
import requests
import html
import json
import time
from google import genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

client = genai.Client(api_key=GEMINI_API_KEY)

def get_file_score(path):
    path_lower = path.lower()
    score = 0
    
    if path_lower == 'readme.md': 
        score += 100
    elif 'readme' in path_lower: 
        score -= 50
        
    if any(x in path_lower for x in ['src/', 'app/', 'lib/', 'core/']): 
        score += 15
        
    if any(x in path_lower for x in ['main.', 'index.', 'app.', 'server.', 'core.', 'client.']): 
        score += 25
        
    if 'test' in path_lower or 'spec' in path_lower: 
        score -= 20
        
    if path_lower.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.go', '.rs')):
        score += 5
        
    return score

def extract_mermaid_and_summary(full_text):
    mermaid_match = re.search(r"```mermaid(.*?)```", full_text, re.DOTALL)
    if mermaid_match:
        mermaid_code = mermaid_match.group(1).strip()
        analysis_text = full_text.replace(mermaid_match.group(0), "").strip()
        
        analysis_text = re.sub(r'^.*Visual Architecture Diagram.*$\n?', '', analysis_text, flags=re.MULTILINE | re.IGNORECASE).strip()
        
        iframe_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script type="module">
                import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
            </script>
            <style>
                body {{ background: #ffffff; margin: 0; padding: 0; }}
                .scroll-container {{ width: 100%; height: 100vh; overflow: auto; padding: 20px; box-sizing: border-box; display: flex; justify-content: center; align-items: flex-start; }}
                .mermaid svg {{ width: 100% !important; min-width: 900px !important; max-width: none !important; height: auto !important; }}
            </style>
        </head>
        <body>
            <div class="scroll-container">
                <div class="mermaid">
{mermaid_code}
                </div>
            </div>
        </body>
        </html>
        """
        escaped_iframe = html.escape(iframe_content)
        chart_html = f'<iframe srcdoc="{escaped_iframe}" width="100%" height="600px" style="border:none; border-radius:0 0 12px 12px; background:#ffffff;"></iframe>'
    else:
        analysis_text = full_text
        chart_html = "<p style='color:#ef4444; padding:20px; text-align:center;'>Flowchart generate nahi ho saka. AI ne valid Mermaid syntax return nahi kiya.</p>"
    return analysis_text, chart_html

def analyze_full_github_repo_stream(repo_url):
    try:
        clean_url = repo_url.strip().rstrip('/')
        if clean_url.endswith('.git'): clean_url = clean_url[:-4]
            
        parts = clean_url.split('/')
        if len(parts) < 2:
            yield json.dumps({"type": "error", "message": "Invalid GitHub URL."}) + "\n"
            return
        
        owner, repo = parts[-2], parts[-1]
        
        yield json.dumps({"type": "status", "message": f"Fetching repository tree for {owner}/{repo}..."}) + "\n"
        
        session = requests.Session()
        headers = {'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'RepoArchitect/1.0'}
        if GITHUB_TOKEN: headers['Authorization'] = f"token {GITHUB_TOKEN}"
        session.headers.update(headers)
        
        tree_api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1"
        response = session.get(tree_api_url, timeout=10)
        
        if response.status_code != 200:
            tree_api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/master?recursive=1"
            response = session.get(tree_api_url, timeout=10)
            
        if response.status_code != 200:
            yield json.dumps({"type": "error", "message": "Repo fetch failed."}) + "\n"
            return
            
        tree_data = response.json().get('tree', [])
        valid_extensions = ('.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.json', '.md')
        ignore_dirs = ('node_modules', 'venv', '.git', 'dist', 'build', '__pycache__', 'images', 'assets')
        
        valid_files = [
            item.get('path', '') for item in tree_data 
            if item.get('type') == 'blob' 
            and not any(ignored in item.get('path', '').lower() for ignored in ignore_dirs)
            and (item.get('path', '').endswith(valid_extensions) or 'readme' in item.get('path', '').lower())
        ]
                    
        valid_files.sort(key=get_file_score, reverse=True)
        code_files = valid_files[:6]
        
        yield json.dumps({"type": "file_list", "files": code_files}) + "\n"
        
        combined_code_content = f"Repository: {owner}/{repo}\n\n"
        
        for file_path in code_files:
            yield json.dumps({"type": "file_update", "file": file_path, "status": "reading"}) + "\n"
            
            time.sleep(1.5)
            
            file_api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
            file_resp = session.get(file_api_url, timeout=8)
            if file_resp.status_code == 200:
                file_data = file_resp.json()
                if 'content' in file_data:
                    file_text = base64.b64decode(file_data['content']).decode('utf-8', errors='ignore')
                    combined_code_content += f"\n--- FILE: {file_path} ---\n{file_text[:2000]}\n"
            
            yield json.dumps({"type": "file_update", "file": file_path, "status": "analysed"}) + "\n"
                        
        prompt = f"""
Act as an expert Senior Code Architect. You have been provided with source code from a GitHub repository.
{combined_code_content}

Perform a structured architectural breakdown in clean Markdown:
1. ### 📝 Project Summary (From README)
2. ### 🛠 Tech Stack
3. ### 🚀 Entry Point & Execution Flow
4. ### 🧩 Module Relationships & Key Components

IMPORTANT: After section 4, directly output the strict, valid Mermaid flowchart syntax code block inside ```mermaid ... ``` mapping file interactions. DO NOT write the words "Visual Architecture Diagram" anywhere in your response.
"""

        yield json.dumps({"type": "status", "message": "Gemma is generating architectural insights..."}) + "\n"
        
        ai_response_stream = client.models.generate_content_stream(
            model='gemma-4-26b-a4b-it',
            contents=prompt
        )
        
        full_ai_text = ""
        for chunk in ai_response_stream:
            chunk_text = chunk.text if chunk.text else ""
            full_ai_text += chunk_text
            yield json.dumps({"type": "token", "text": chunk_text}) + "\n"
            
        analysis_markdown, mermaid_markup = extract_mermaid_and_summary(full_ai_text)
        yield json.dumps({
            "type": "done", 
            "mermaid_chart": mermaid_markup, 
            "clean_markdown": analysis_markdown,
            "context": combined_code_content
        }) + "\n"
        
    except Exception as e:
        yield json.dumps({"type": "error", "message": str(e)}) + "\n"

def chat_with_codebase(query, repo_context, history):
    history_text = ""
    for msg in history[-4:]: 
        prefix = "User" if msg["role"] == "user" else "AI"
        history_text += f"{prefix}: {msg['content']}\n"
        
    prompt = f"=== CODEBASE CONTEXT ===\n{repo_context}\n\n=== CONVERSATION HISTORY ===\n{history_text}\n\n=== NEW QUESTION ===\nUser: {query}\n\nProvide a direct technical answer based strictly on the codebase context using Markdown."
    try:
        ai_response = client.models.generate_content(model='gemma-4-26b-a4b-it', contents=prompt)
        return ai_response.text
    except Exception as e:
        return f"❌ Chat Error: {str(e)}"