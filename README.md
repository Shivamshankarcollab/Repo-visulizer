# 🚀 Repo Visualizer

> **AI-Powered Codebase Architecture Inspector & Interactive Visualizer**  
> *Built for DTU Hacktoberfest*

---

## 💡 Overview & Problem Statement
Understanding a new repository takes hours: which file is the entry point, how the modules connect, and what the tech stack is. Judges and reviewers don’t have the time to read the code of every project. 

**Solution:** **Repo Visualizer** fetches a repo from its GitHub URL, prioritizes the important files, and uses the Gemma model to generate an architecture explanation and diagram. Everything is shown with live streaming progress.

---

## ✨ Key Features
* **Smart File Prioritization**: `core_engine.py` uses a scoring system to rank the root README and core source files (`src/`, `app/`, `main.py`, `server.py`) higher, while filtering out redundant documentation and test files.
* **Real-time Streaming**: FastAPI with Server-Sent Events (SSE) shows each file's status live (`Queued` ➔ `Reading now` ➔ `Analysed`).
* **Auto-generated Architecture Diagram**: The AI produces valid Mermaid.js syntax, rendered as a clean, zoomable, scrollable diagram.
* **Context-Aware Follow-up Chat**: After analysis, ask questions like *"Can you give me all the code files present in this repo?"* and get answers grounded in the repository's context.
* **Multi-session Management**: A ChatGPT-style sidebar saves recent analyses so you can switch between repositories without refreshing the page.

---

## 🔄 How It Works
1. **Repository Ingestion**: The user enters a public GitHub URL, and the backend fetches the full folder structure using the GitHub Git Trees API.
2. **Intelligent Selection**: A custom scoring engine selects the most important source files and the main README.
3. **Live File Streaming**: The frontend animates file-by-file reading progress.
4. **AI Architectural Breakdown**: The Gemma model analyzes the codebase and generates the project summary, tech stack, entry point, and Mermaid diagram.
5. **Interactive Q&A**: Session memory activates, allowing the user to ask follow-up questions about the codebase.

---

## 🛠 Tech Stack
* **AI Model**: Google Gemma (`gemma-4-26b-a4b-it`) via `google-genai`.
* **Backend**: Python, FastAPI (`StreamingResponse`), Requests, Pydantic, Python-dotenv.
* **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript, Marked.js, Mermaid.js.
* **Data Source**: GitHub REST APIs.

---

## 🚀 Run Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Shivamshankarcollab/Repo-visulizer.git](https://github.com/Shivamshankarcollab/Repo-visulizer.git)
   cd Repo-visulizer

```

2. **Install dependencies:**
```bash
pip install -r requirements.txt

```


3. **Set your API keys:**
Create a `.env` file in the root directory and add your keys:
```env
GEMINI_API_KEY="your_gemini_api_key"
GITHUB_TOKEN="your_github_token"

```


4. **Run the FastAPI backend server:**
```bash
python server.py

```


5. **Open the UI:**
Open `index.html` in your browser or run it through a live server to start visualizing!
