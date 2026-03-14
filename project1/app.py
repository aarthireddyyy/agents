from fastapi import FastAPI
app = FastAPI()
from agent import run_agent
@app.post("/ask")
def ask(question: str):
    answer = run_agent(question)
    return {"answer": answer}
