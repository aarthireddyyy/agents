from dotenv import load_dotenv
import os
import json
import requests
import time
from groq import Groq
from bs4 import BeautifulSoup
from tavily import TavilyClient

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# ── TOOLS ──────────────────────────────────────────────

def web_search(query):
    results = tavily_client.search(query)
    return results["results"]

def read_url(url):
    response = requests.get(url, timeout=5)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.get_text()[:2000]  # limit to avoid context overflow

def save_to_file(filename, content):
    with open(filename, "w") as f:
        f.write(content)
    return "Saved successfully!"

# ── TOOL SCHEMA ────────────────────────────────────────

tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Searches the web for current real-time information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "search term"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_url",
            "description": "Fetches and reads content from a URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "the URL to read"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_to_file",
            "description": "Saves content to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "name of the file"},
                    "content": {"type": "string", "description": "content to save"}
                },
                "required": ["filename", "content"]
            }
        }
    }
]

# ── AGENT LOOP ─────────────────────────────────────────

def run_agent(user_question):
    messages = [
        {
            "role": "system",
            "content": "You are a research assistant. Call ONE tool at a time. Wait for results before calling the next tool. Never assume what a tool will return."
        },
        {"role": "user", "content": user_question}
    ]

    max_steps = 8
    step = 0

    while step < max_steps:
        step += 1
        print(f"\n--- Step {step} ---")

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            tools=tools
        )

        message = response.choices[0].message

        # LLM wants to call a tool
        if message.tool_calls:
            print(f"Tool called: {message.tool_calls[0].function.name}")
            messages.append(message)

            for tool_call in message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                if name == "web_search":
                    result = web_search(args["query"])
                elif name == "read_url":
                    result = read_url(args["url"])
                elif name == "save_to_file":
                    result = save_to_file(args["filename"], args["content"])
                else:
                    result = "Unknown tool"

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })

            time.sleep(10)  # respect rate limits

        # LLM has final answer
        else:
            print("\n--- Final Answer ---")
            return message.content

    return "Max steps reached without final answer."

# ── RUN ────────────────────────────────────────────────

print(run_agent("What is the latest news about AI today? Save a summary to ai_news.txt"))