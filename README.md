
Readme · MD
# AI Coding Agent
 
A simple command-line AI agent built with Python and the Gemini API. It can read files, list directories, write files, and run Python scripts inside a sandboxed working directory — all on its own, by deciding which tools to call to complete a task.
 
## What it does
 
You give it a task in plain English, and it figures out the rest:
 
```bash
uv run main.py "Fix the bug: 3 + 7 * 2 shouldn't be 20."
```
 
The agent will look at the project files, find the problem, fix it, and verify the fix — calling its tools step by step until it has a final answer.
 
## Available tools
 
The agent can:
 
- **List files** in a directory (name, size, type)
- **Read file contents** (truncated if too large)
- **Write or overwrite files**
- **Run Python files** with optional arguments
All of this is scoped to a single working directory (`calculator/` by default) — the agent can't read or write anything outside of it.
 
## Setup
 
1. Install dependencies:
```bash
   uv sync
```
2. Add your Gemini API key to a `.env` file in the project root:
```
   GEMINI_API_KEY=your_key_here
```
 
## Usage
 
```bash
uv run main.py "your prompt here"
```
 
Add `--verbose` to see each tool call, its arguments, and its result:
 
```bash
uv run main.py "your prompt here" --verbose
```
 
## Project structure
 
```
.
├── main.py                  # Entry point, runs the agent loop
├── call_function.py         # Maps function calls to real functions
├── prompts/
│   └── prompts.py           # System prompt
├── functions/
│   ├── get_files_info.py
│   ├── get_file_content.py
│   ├── write_file.py
│   └── run_python_file.py
└── calculator/               # Sample project the agent operates on
```
 
## How it works
 
1. Your prompt is sent to Gemini along with a list of available tools.
2. The model decides which tool (if any) to call, and with what arguments.
3. The agent runs that tool for real and feeds the result back to the model.
4. This repeats — up to 20 times — until the model has a final answer instead of another tool


## ⚠️ Safety note

This is a learning project, not production software. The agent can execute arbitrary Python code and overwrite files with no undo and minimal safeguards. If you run this yourself:

- Only point it at a disposable/sandboxed directory (never your real projects or system files).
- Don't run it with elevated permissions.
- Treat any code or file changes it makes as untrusted until you've reviewed them.
