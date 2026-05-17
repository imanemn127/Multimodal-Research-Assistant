import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from typing import List, Dict, Any
from src.retrieval.rag_pipeline import RAGPipeline

load_dotenv()


class ResearchAgent:

    def __init__(self, rag_pipeline: RAGPipeline):
        self.rag = rag_pipeline
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = "llama-3.3-70b-versatile"

    def answer(self, question: str) -> Dict[str, Any]:
        print(f"\n[Agent] Question: {question}")

        # step 1: plan — break into sub-questions
        sub_questions = self._plan(question)
        print(f"[Agent] Sub-questions: {sub_questions}")

        # step 2: execute — answer each sub-question via RAG
        sub_answers = []
        for sq in sub_questions:
            print(f"[Agent] Retrieving: {sq}")
            result = self.rag.answer(sq)
            sub_answers.append({
                "question": sq,
                "answer": result["answer"]
            })

        # step 3: synthesize — combine into final answer
        final_answer = self._synthesize(question, sub_answers)

        return {
            "question": question,
            "sub_questions": sub_questions,
            "sub_answers": sub_answers,
            "final_answer": final_answer
        }

    def _plan(self, question: str) -> List[str]:
        prompt = f"""You are a research assistant planning how to answer a complex question about a scientific paper.

Break this question into 2-3 focused sub-questions that can each be answered independently by searching the paper.
Return ONLY a JSON array of strings. No explanation, no markdown, just the array.

Question: {question}

Example output:
["What is X?", "What is Y?", "How do X and Y compare?"]"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        raw = response.choices[0].message.content.strip()

        # extract JSON array from response
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start != -1 and end != 0:
            return json.loads(raw[start:end])

        return [question]

    def _synthesize(self, original_question: str, sub_answers: List[Dict]) -> str:
        sub_answers_text = "\n\n".join([
            f"Q: {sa['question']}\nA: {sa['answer']}"
            for sa in sub_answers
        ])

        prompt = f"""You are a scientific research assistant.
Using the following research findings, provide a comprehensive answer to the original question.
Structure your response clearly. Preserve citations from the findings.

ORIGINAL QUESTION:
{original_question}

RESEARCH FINDINGS:
{sub_answers_text}

Provide a well-structured final answer that directly addresses the original question."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        return response.choices[0].message.content
