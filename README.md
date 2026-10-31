🚀 Repo Visualizer
AI-powered codebase architecture inspector and interactive visualizer
Built for DTU Hacktoberfest
🎯 Problem
Understanding a new repository takes hours: which file is the entry point, how the modules connect, and what the tech stack is. Judges and reviewers don’t have the time to read the code of every project.
💡 Solution
Repo Visualizer fetches a repo from its GitHub URL, prioritizes the important files, and uses the Gemma model to generate an architecture explanation and diagram. Everything is shown with live streaming progress.
✨ Features
	•	Smart file prioritization: core_engine.py uses a scoring system to rank the root README and core source files (src/, app/, main.py, server.py) higher, while filtering out redundant documentation and test files. This makes the best use of the model’s limited context window.
	•	Real-time streaming: FastAPI with Server-Sent Events (SSE) shows each file’s status live (Queued → Reading now → Analysed).
	•	Auto-generated architecture diagram: The AI produces valid Mermaid.js syntax, rendered as a clean, zoomable, scrollable diagram.
	•	Context-aware follow-up chat: After analysis, ask questions like “Can you give me all the code files present in this repo?” and get answers grounded in the repository’s context.
	•	Multi-session management: A ChatGPT-style sidebar saves recent analyses so you can switch between repositories without refreshing the page.
🔄 How It Works
	1	Repository ingestion: The user enters a public GitHub URL, and the backend fetches the full folder structure using the GitHub Git Trees API.
	2	Intelligent selection: A custom scoring engine selects the most important source files and the main README.
	3	Live file streaming: The frontend animates file-by-file reading progress.
	4	AI architectural breakdown: The Gemma model analyzes the codebase and generates the project summary, tech stack, entry point, and Mermaid diagram.
	5	Interactive Q&A: Session memory activates so the user can ask follow-up questions about the codebase.
🛠 Tech Stack
Layer
Tools
AI Model
Google Gemma (gemma-4-26b-a4b-it) via google-genai
Backend
Python, FastAPI (StreamingResponse), Requests, Pydantic
Frontend
HTML5, Tailwind CSS, Vanilla JavaScript, Marked.js, Mermaid.js
Data Source
GitHub REST API
Tools
Git, GitHub, REST APIs
▶️ Run Locally
	1	Clone the repository:

bash
git clone https://github.com/Shivamshankarcollab/Repo-visulizer
cd Repo-visulizer
	2	Install dependencies:

bash
pip install fastapi uvicorn requests google-genai pydantic
	3	Set your API keys as environment variables:

bash
export GEMINI_API_KEY="your_gemini_api_key"
export GITHUB_TOKEN="your_github_token"
	4	Run the FastAPI backend server:

bash
python server.py
	5	Open index.html in your browser, or serve it locally, to use the UI.
🚧 Challenges
	•	Fitting large repositories into the model’s context limit, solved with file scoring.
	•	Getting the AI to produce valid Mermaid syntax, since invalid syntax breaks the diagram.
	•	Keeping the UI smooth while streaming live updates.
🔮 Future Scope
Private repository support, file-level dependency graphs, multi-repo comparison, and diagram export (PNG/SVG).
