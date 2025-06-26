# import httpx
# from prompts import SYSTEM_PROMPT_TEMPLATE
# from schema import RAGQuery
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.output_parsers import StrOutputParser

# from dotenv import load_dotenv
# import os

# load_dotenv()
# api_key = os.getenv("GOOGLE_API_KEY")

# import google.generativeai as genai

# genai.configure(api_key=api_key)


# async def get_retrieved_context(query, class_name, subject, top_k=5):
#     async with httpx.AsyncClient() as client:
#         response = await client.post(
#             "http://127.0.0.1:9000/retrieve",  # ✅ Correct endpoint and port
#             json={
#                 "query": query,
#                 "class_name": class_name,
#                 "subject": subject,
#                 "top_k": top_k
#             }
#         )
#     response.raise_for_status()
#     return response.json()


# async def run_rag_chain(payload: RAGQuery):
#     context_data = await get_retrieved_context(
#         payload.query,
#         payload.class_name,
#         payload.subject


#     )

#     context_text = "\n".join([doc["text"] for doc in context_data])

#     # System Prompt customization
#     prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT_TEMPLATE)

#     chain = (
#         prompt
#         | ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key="YOUR_GEMINI_API_KEY")
#         | StrOutputParser()
#     )
# #     ChatGoogleGenerativeAI(
# #     model="gemini-2.0-flash",
# #     google_api_key=api_key  # already loaded by load_dotenv()
# # )


#     response = await chain.ainvoke({
#         "query": payload.query,
#         "context": context_text,
#         "age": payload.age,
#         "role": payload.role,
#         "focus": payload.topic
#     })

#     return response



# import httpx
# from app.services.prompts import SYSTEM_PROMPT_TEMPLATE
# from app.utils.schema import RAGQuery

# from langchain_core.prompts import ChatPromptTemplate
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.output_parsers import StrOutputParser

# from dotenv import load_dotenv
# import os

# load_dotenv()
# api_key = os.getenv("GOOGLE_API_KEY")

# import google.generativeai as genai
# genai.configure(api_key=api_key)

# async def get_retrieved_context(query, class_name, subject, top_k=5):
#     async with httpx.AsyncClient() as client:
#         response = await client.post(
#             "http://127.0.0.1:9000/retrieve",  # ✅ Correct endpoint and port
#             json={
#                 "query": query,
#                 "class_name": class_name,
#                 "subject": subject,
#                 "top_k": top_k
#             }
#         )
#     response.raise_for_status()
#     return response.json()

# async def run_rag_chain(payload: RAGQuery):
#     context_data = await get_retrieved_context(
#         payload.query,
#         payload.class_name,
#         payload.subject
#     )

#     context_text = "\n".join([doc["text"] for doc in context_data])

#     prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT_TEMPLATE)

#     chain = (
#         prompt
#         | ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key)
#         | StrOutputParser()
#     )

#     response = await chain.ainvoke({
#         "query": payload.query,
#         "context": context_text,
#         "age": payload.age,
#         "role": payload.role,
#         "focus": payload.topic
#     })

#     return response




from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from app.utils.schema import RAGQuery

import httpx
from app.services.prompts import SYSTEM_PROMPT_TEMPLATE
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

import google.generativeai as genai
genai.configure(api_key=api_key)

app = FastAPI()

# Allow CORS (optional but useful)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_retrieved_context(query, class_name, subject, top_k=5):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:8000/retrieve",  # ✅ Make sure this endpoint exists and works
            json={
                "query": query,
                "class_name": class_name,
                "subject": subject,
                "top_k": top_k
            }
        )
    response.raise_for_status()
    return response.json()

async def run_rag_chain(payload: RAGQuery):
    context_data = await get_retrieved_context(
        payload.query,
        payload.class_name,
        payload.subject
    )

    context_text = "\n".join([doc["text"] for doc in context_data])

    prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT_TEMPLATE)

    chain = (
        prompt
        | ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key)
        | StrOutputParser()
    )

    response = await chain.ainvoke({
        "query": payload.query,
        "context": context_text,
        "age": payload.age,
        "role": payload.role,
        "focus": payload.topic
    })

    return response

# ✅ FastAPI endpoint to call run_rag_chain
@app.post("/generate")
async def generate_answer(payload: RAGQuery):
    try:
        result = await run_rag_chain(payload)
        return {"response": result}
    except Exception as e:
        return {"error": str(e)}

