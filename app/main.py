from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schema import RAGQuery
from rag_chain import run_rag_chain

app = FastAPI(title="📚 PathShala RAG QA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/rag-query")
async def rag_query(payload: RAGQuery):
    try:
        answer = await run_rag_chain(payload)
        return {"answer": answer}
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
def health_check():
    return {"status": "ok"}

