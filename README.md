# GitHub Deep Codebase Visualizer & Analyzer

An AI-powered codebase architect that analyzes public GitHub repositories, inspects prioritized source code files, and generates execution flows alongside Mermaid.js architecture diagrams.

## Features
- Fetches directory trees via GitHub Git Tree API.
- Intelligent file scoring to prioritize core logic over configs and tests.
- Summarizes tech stacks, entry points, and module interactions.
- Generates interactive Mermaid.js flowcharts.

## Setup & Running Locally

1. **Clone the repository:**
   \`\`\`bash
   git clone https://github.com/Shivamshankarcollab/Repo-visulizer.git
   cd Repo-visulizer
   \`\`\`

2. **Install dependencies:**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. **Set Environment Variables:**
   \`\`\`bash
   export GEMINI_API_KEY="your_gemini_api_key"
   export GITHUB_TOKEN="your_github_personal_access_token" # optional, increases API limits
   \`\`\`

4. **Run the App:**
   \`\`\`bash
   python app.py
   \`\`\`
