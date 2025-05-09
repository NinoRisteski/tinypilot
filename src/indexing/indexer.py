import os
import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer


class Indexer:
    def __init__(self, collection_name: str, model_name: str = "all-MiniLM-L6-v2"):
        self.collection_name = collection_name
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def index_repo(self, repo_path: str = "data/tinygrad"):
        #TODO:
        pass

    def index_bounties(self, bounty_path: str = "data/bounties.csv"):
        #TODO:
        pass

    def index_tutorials(self, scraped_path: str = "data/tutorials"):
        #TODO:
        pass

