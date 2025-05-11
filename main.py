from src.manager.repo_updater import update_repo
from src.manager.bounties_updater import bounties
from src.manager.tutorial_scraper import scrape_tutorials
from src.indexing.indexer import Indexer
from src.rag.retriever import Retriever
from src.rag.generator import Generator
import os
import sys

def check_openai_api_key():
    if not os.getenv("OPENAI_API_KEY"):
        return False
    return True

def main():
    print("Starting tinypilot!")
    
    if not check_openai_api_key():
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it with:")
        print("export OPENAI_API_KEY='your-api-key'")
        sys.exit(1)
    
    update_repo()
    print("tinygrad repo: updated.")
    bounties()
    print("bounties: updated.")
    scrape_tutorials()
    print("tutorials: scraped.")
    
    print("\nIndexing data (this may take a while)...")
    indexer = Indexer("tinygrad_data")
    indexer.index_repo()
    indexer.index_bounties()
    indexer.index_tutorials()
    print("data: indexed and embedded!")
    
    print("\nInitializing RAG system...")
    retriever = Retriever()
    generator = Generator()
    print("RAG system ready!")
    
    print("\nYou can now start learning tinygrad with the tinypilot! Type 'exit' to quit.")
    while True:
        query = input("\nYour question: ").strip()
        if query.lower() == 'exit':
            break
            
        results = retriever.retrieve(query)
        print(f"\nFound {len(results)} relevant documents")
        
        response = generator.generate(query, results)
        print("\nAnswer:")
        print(response)

if __name__ == "__main__":
    main()