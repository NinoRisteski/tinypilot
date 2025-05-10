from src.manager.repo_updater import update_repo
from src.manager.bounties_updater import bounties
from src.manager.tutorial_scraper import scrape_tutorials
from src.indexing.indexer import Indexer

def main():
    print("Starting tinypilot!")
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

if __name__ == "__main__":
    main()