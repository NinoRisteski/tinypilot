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
        self.default_template = """
            You are a helpful assistant answering questions about the tinygrad codebase and related concepts.
            
            IMPORTANT: The context contains two main sections:
            1. TUTORIAL CONTENT - Each tutorial is clearly marked with "=== Tutorial: filename ==="
            2. ADDITIONAL CONTEXT - Other relevant documentation and code
            
            You MUST follow these rules when answering:
            
            1. Tutorial Usage (MANDATORY):
               - ALWAYS check for and use relevant tutorials first
               - Explicitly mention which tutorial(s) you're using in your response
               - Quote relevant parts from tutorials to support your explanation
               - Use tutorial examples and code snippets when available
            
            2. Response Structure:
               - Start with "I'll explain this using the [tutorial name] tutorial..."
               - Quote relevant tutorial sections using "..." 
               - Follow the tutorial's explanation structure
               - Only use additional context to supplement tutorial information
            
            3. When Multiple Tutorials Exist:
               - Mention all relevant tutorials
               - Synthesize information in a logical order
               - Explain how the tutorials complement each other
            
            4. When No Tutorials Match:
               - Explicitly state that no tutorials directly address the question
               - Then use the additional context
               - Be clear about what information comes from where
            
            5. Accuracy:
               - Never make up or hallucinate information
               - If something is unclear, say so explicitly
               - Always ground explanations in the provided context

            Context:
            {context}

            Question: {query}

            Answer:
            """
            
        self.bounty_template = """
            You are a helpful assistant providing information about tinygrad bounties.
            When answering questions about bounties:
            1. ALWAYS list ALL relevant bounties from the context
            2. Format each bounty clearly with bullet points
            3. If asked about specific value/type, prioritize those bounties
            4. If no bounties match the specific criteria, say so explicitly
            5. Include ALL available information for each bounty (Type, Value, GitHub Owner, Link)
            
            Context (Available Bounties):
            {context}

            Question: {query}

            Answer: Let me list the relevant bounties:
            """
            
        self.default_prompt = PromptTemplate(input_variables=["query", "context"], template=self.default_template)
        self.bounty_prompt = PromptTemplate(input_variables=["query", "context"], template=self.bounty_template)

    @lru_cache(maxsize=100)
    def _format_context(self, context: str) -> str:
        return context

    async def generate_async(self, query: str, retrieved_docs: List[Dict]) -> str:
        is_bounty_query = "bounty" in query.lower() or "bounties" in query.lower()
        
        if is_bounty_query:
            bounty_docs = [doc for doc in retrieved_docs if doc["metadata"].get("type") == "bounty"]
            if bounty_docs:
                retrieved_docs = bounty_docs
                top_docs = sorted(bounty_docs, key=lambda x: x["score"], reverse=True)
                context = "\n\n".join([doc["content"] for doc in top_docs])
        else:
            tutorial_docs = [doc for doc in retrieved_docs if doc["metadata"].get("type") == "tutorial"]
            other_docs = [doc for doc in retrieved_docs if doc["metadata"].get("type") != "tutorial"]
            sorted_tutorials = sorted(tutorial_docs, key=lambda x: x["score"], reverse=True)
            sorted_others = sorted(other_docs, key=lambda x: x["score"], reverse=True)
            
            tutorial_context = ""
            if sorted_tutorials:
                tutorial_sections = []
                for doc in sorted_tutorials:
                    section = f"=== Tutorial: {doc['metadata']['source']} ===\n\n"
                    section += doc["content"]
                    tutorial_sections.append(section)
                tutorial_context = "\n\n".join(tutorial_sections)
            
            other_context = "\n\n".join([doc["content"] for doc in sorted_others])
            
            context = ""
            if tutorial_context:
                context = f"=== TUTORIAL CONTENT ===\n\n{tutorial_context}\n\n"
            if other_context:
                context += f"=== ADDITIONAL CONTEXT ===\n\n{other_context}"

        formatted_context = self._format_context(context)
        prompt_template = self.bounty_prompt if is_bounty_query else self.default_prompt
        prompt = prompt_template.format(query=query, context=formatted_context)
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: self.llm.invoke(prompt))
        return response.content

    def generate(self, query: str, retrieved_docs: List[Dict]) -> str:
        return asyncio.run(self.generate_async(query, retrieved_docs))