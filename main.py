from src.manager.repo_updater import update_repo
from src.manager.bounties_updater import bounties
from src.manager.tutorial_scraper import scrape_tutorials
from src.indexing.indexer import Indexer
from src.ui.interface import ChatbotInterface
import os
import sys
import time

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
    
    start_time = time.time()
    
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
    
    end_time = time.time()
    print(f"data: indexed and embedded in {end_time - start_time:.2f} seconds!")
    
    print("\nInitializing RAG system...")
    chatbot = ChatbotInterface()
    print("RAG system ready!")
    
    chatbot.run()

if __name__ == "__main__":
    main()