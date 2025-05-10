import chromadb
from sentence_transformers import SentenceTransformer

class Retriever:
    def __init__(self, collection_name="tinygrad_data", persist_directory="./chroma_db"):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_collection(collection_name)

    def retrieve(self, query, top_k=5):
        query_embedding = self.model.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["metadatas", "documents", "distances"]
        )
        
        retrieved_docs = []
        for i in range(len(results["documents"][0])):
            doc = results["documents"][0][i]
            if doc is None:
                continue
            retrieved_docs.append({"content": doc,"metadata": results["metadatas"][0][i],"score": 1.0 - results["distances"][0][i]})
        return retrieved_docs
