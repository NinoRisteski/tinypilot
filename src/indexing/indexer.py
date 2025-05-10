import os
import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer


class Indexer:
    def __init__(self, collection_name: str, model_name: str = "all-MiniLM-L6-v2", persist_directory: str = "./chroma_db"):
        self.collection_name = collection_name
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(collection_name)

    def index_repo(self, repo_path: str = "data/tinygrad"):
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith(".py"):
                    with open(os.path.join(root, file), "r") as f:
                        content = f.read()
                        embedding = self.model.encode(content).tolist()
                        self.collection.add(ids=[f"repo_{file}"], embeddings=[embedding], metadatas=[{"source": file, "type": "code"}])

    def index_bounties(self, bounty_path: str = "data/bounties.csv"):
        bounties = pd.read_csv(bounty_path)
        for idx, row in bounties.iterrows():
            content = " ".join(str(v) for v in row.values)
            embedding = self.model.encode(content).tolist()
            self.collection.add(ids=[f"bounty_{idx}"], embeddings=[embedding], metadatas=[{"source": "bounties.csv", "type": "bounty"}])

    def index_tutorials(self, scraped_path: str = "data/tutorials"):
        for file in os.listdir(scraped_path):
            with open(os.path.join(scraped_path, file), "r") as f:
                content = f.read()
                embedding = self.model.encode(content).tolist()
                self.collection.add(ids=[f"tutorial_{file}"], embeddings=[embedding], metadatas=[{"source": file, "type": "tutorial"}])


