from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from functools import lru_cache
import asyncio
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

class Generator:
    def __init__(self, model_name="gpt-4o-mini-2024-07-18"):
        self.llm = ChatOpenAI(model_name=model_name, temperature=0.0, api_key=os.getenv("OPENAI_API_KEY"))
        self.prompt_template = PromptTemplate(
            input_variables=["query", "context"],
            template="""
            You are a helpful assistant answering questions about the tinygrad codebase, bounties, and related tutorials.
            Use the retrieved context to provide an accurate answer. If the context doesn't answer the question, use your general knowledge but prioritize the context.

            Context:
            {context}

            Question: {query}

            Answer:
            """
        )

    @lru_cache(maxsize=100)
    def _format_context(self, context: str) -> str:
        return context

    async def generate_async(self, query: str, retrieved_docs: List[Dict]) -> str:
        top_docs = sorted(retrieved_docs, key=lambda x: x["score"], reverse=True)[:2]
        context = "\n\n".join([doc["content"] for doc in top_docs])
        formatted_context = self._format_context(context)
        prompt = self.prompt_template.format(query=query, context=formatted_context)
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: self.llm.invoke(prompt))
        return response.content

    def generate(self, query: str, retrieved_docs: List[Dict]) -> str:
        return asyncio.run(self.generate_async(query, retrieved_docs))