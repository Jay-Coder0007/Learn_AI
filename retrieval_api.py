from fastapi import FastAPI
from qdrant_config import qdrant
from schema import QuerySchema
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI(title="📚 PathShala QnA Retriever API")

# Allow frontend to call the API (optional, for testing from browser or React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

@app.post("/retrieve")
def retrieve(query: QuerySchema):
    try:
        # Step 1: Create embedding for the input query
        vec = model.encode(query.query).tolist()

        # Step 2: Search Qdrant collection
        collection_name = f"class_{query.class_name}"
        results = qdrant.search(
            collection_name=collection_name,
            query_vector=vec,
            limit=query.top_k,
            query_filter={
                "must": [
                    {"key": "subject", "match": {"value": query.subject}}
                ]
            }
        )

        # Step 3: Format and return results
        return [
            {
                "text": r.payload.get("text"),
                "score": r.score,
                "metadata": r.payload
            }
            for r in results
        ]

    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
def health_check():
    return {"status": "ok"}
