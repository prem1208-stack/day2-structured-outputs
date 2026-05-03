# Day 2 — Structured Outputs and Tool Use

Day 2 of a 14-day AI builder sprint. Two patterns that turn Claude from a chatbot into a building block: structured extraction (messy text → clean JSON) and multi-tool dispatch (natural language → the right function call).

## What's in here

- `extract.py` — extracts structured ops metrics from shift manager messages
- `dispatcher.py` — routes natural-language requests to the right tool (metrics, rider lookup, complaints, scheduling)
- 'creative.py' — to convert a text to structued creative brief 

## Stack

- Python with `uv`
- `anthropic` SDK
- Tool use API for structured output and function routing

## Key concepts internalized

- Tool use produces reliable structured data; never parse JSON from prose
- `tool_choice: {"type": "tool", "name": ...}` forces a specific tool; `auto` lets Claude decide
- Tools and system prompts work together — neither is sufficient alone
- Claude often emits both `text` and `tool_use` blocks; code must scan all blocks before deciding what to do
- Tool design is product design — schemas must match user query shapes, not backend table shapes

## Run it

\`\`\`bash
uv add anthropic python-dotenv
echo "ANTHROPIC_API_KEY=your-key-here" > .env
uv run extract.py
uv run dispatcher.py
\`\`\`

## Next

Day 3 — first deployed web app (Next.js + Vercel).