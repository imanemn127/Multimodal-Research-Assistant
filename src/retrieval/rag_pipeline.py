import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import Dict, Any
from src.retrieval.retriever import Retriever

load_dotenv()


class RAGPipeline:

    def __init__(self, retriever: Retriever, model: str = "llama-3.3-70b-versatile"):
        self.retriever = retriever
        self.model = model
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )

    def answer(self, question: str) -> Dict[str, Any]:
        results = self.retriever.retrieve(question)
        context = self.retriever.format_context(results)
        prompt = self._build_prompt(question, context)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self._system_prompt()},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        return {
            "question": question,
            "answer": response.choices[0].message.content,
            "sources": results
        }

    def _system_prompt(self) -> str:
        return """You are a scientific research assistant.
Your job is to answer questions about research papers accurately and clearly.
Always base your answers strictly on the provided context.
If the context does not contain enough information, say so honestly.
Always cite which source (Source 1, Source 2, etc.) supports each claim."""

    def _build_prompt(self, question: str, context: str) -> str:
        return f"""Use the following context from a research paper to answer the question.

CONTEXT:
{context}

QUESTION:
{question}

Provide a clear, structured answer with citations to the sources above."""
