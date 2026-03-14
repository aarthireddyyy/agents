# PROJECT 1 - Research Agent

A conversational AI agent that takes a question, searches the web, reads relevant URLs, and returns a structured answer — built from scratch with no frameworks.

## What it does

Send it a question via API. It searches the web, reads pages, and saves a summary to a file.

```
POST /ask?question=What is the latest news about AI today?
→ { "answer": "..." }
```

## Tools

| Tool | What it does |
|------|-------------|
| `web_search` | Live web search via Tavily API |
| `read_url` | Fetches and parses webpage content |
| `save_to_file` | Writes output to disk |

## Stack

- **LLM** — Groq (llama-3.3-70b-versatile)
- **Search** — Tavily API
- **Web parsing** — BeautifulSoup
- **API** — FastAPI + Uvicorn
- **Deployment** — Railway

## Live

Deployed on Railway — (https://agents-production-83f5.up.railway.app/)
