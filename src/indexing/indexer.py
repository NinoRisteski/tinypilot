import os
import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any


class Indexer:
    def __init__(self, collection_name: str, model_name: str = "all-MiniLM-L6-v2", persist_directory: str = "./chroma_db", batch_size: int = 32):
        self.collection_name = collection_name
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(collection_name)
        self.batch_size = batch_size

    def process_batch(self, texts: List[str], metadata: List[Dict[str, Any]], ids: List[str]) -> None:
        if not texts: return
        
        embeddings = self.model.encode(texts, show_progress_bar=False)
        self.collection.add(ids=ids, embeddings=embeddings.tolist(), documents=texts, metadatas=metadata)

    def batch_iterator(self, items: List[Any], batch_size: int):
        for i in range(0, len(items), batch_size): yield items[i:i + batch_size]

    def index_repo(self, repo_path: str = "data/tinygrad"):
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith(".py"):
                    with open(os.path.join(root, file), "r") as f:
                        content = f.read()
                        embedding = self.model.encode(content).tolist()
                        self.collection.add(ids=[f"repo_{file}"], embeddings=[embedding], documents=[content], metadatas=[{"source": file, "type": "code"}])

    def index_bounties(self, bounty_path: str = "data/bounties.csv"):
        bounties = pd.read_csv(bounty_path)
        for idx, row in bounties.iterrows():
            content = f"• {row['Short Description']}\n"
            content += f"  - Type: {row['Type']}\n"
            content += f"  - Value: {row['Value']}\n"
            if pd.notna(row['GitHub Owner']) and row['GitHub Owner']:
                content += f"  - GitHub Owner: {row['GitHub Owner']}\n"
            if pd.notna(row['Link']) and row['Link']:
                content += f"  - Link: {row['Link']}\n"
                
            embedding = self.model.encode(content).tolist()
            self.collection.add(ids=[f"bounty_{idx}"], embeddings=[embedding], documents=[content], metadatas=[{"source": "bounties.csv","type": "bounty","bounty_type": row['Type'],"value": row['Value']}])

    def index_tutorials(self, scraped_path: str = "data/tutorials"):
        for file in os.listdir(scraped_path):
            with open(os.path.join(scraped_path, file), "r") as f:
                content = f.read()
                embedding = self.model.encode(content).tolist()
                self.collection.add(ids=[f"tutorial_{file}"],embeddings=[embedding],documents=[content],metadatas=[{"source": file, "type": "tutorial"}])


