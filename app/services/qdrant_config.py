from qdrant_client import QdrantClient
qdrant = QdrantClient("http://localhost:6333")

# schema.py
from pydantic import BaseModel

class Metadata(BaseModel):
    class_name: str
    subject: str
    chapter: str
    language: str
    client_id: str

class QuerySchema(BaseModel):
    query: str
    class_name: str
    subject: str
    top_k: int = 3