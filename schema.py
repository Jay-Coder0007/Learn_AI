

from pydantic import BaseModel

class RAGQuery(BaseModel):
    query: str
    class_name: str  # e.g., "8"
    subject: str     # e.g., "science"
    role: str        # e.g., "student", "teacher", "parent"
    age: int         # e.g., 14
    topic: str       # e.g., "food chain"








class Metadata(BaseModel):
    class_name: str
    subject: str
    chapter_name: str
    language: str
    client_id: str


class QuerySchema(BaseModel):
    query: str
    class_name: str
    subject: str
    top_k: int = 3

