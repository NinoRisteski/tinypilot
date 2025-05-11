from src.rag.retriever import Retriever
from src.rag.generator import Generator
from src.ui.interface import ChatbotInterface
import os
import sys

def check_openai_api_key():
    if not os.getenv("OPENAI_API_KEY"):
        return False
    return True

def main():
    print("Starting TinyPilot interface...")
    
    if not check_openai_api_key():
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it with:")
        print("export OPENAI_API_KEY='your-api-key'")
        sys.exit(1)
    
    try:
        # Initialize RAG components with existing data
        retriever = Retriever()
        generator = Generator(model_name="gpt-4o-mini-2024-07-18")
        
        # Create and run interface
        chatbot = ChatbotInterface(retriever=retriever, generator=generator)
        chatbot.run()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nIf you haven't run the full initialization yet, please run:")
        print("python main.py")
        sys.exit(1)

if __name__ == "__main__":
    main() 