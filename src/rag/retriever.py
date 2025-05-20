import chromadb
from sentence_transformers import SentenceTransformer

class Retriever:
    def __init__(self, collection_name="tinygrad_data", persist_directory="./chroma_db"):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_collection(collection_name)

    def retrieve(self, query, top_k=5):
        query_embedding = self.model.encode(query).tolist()
        
        if "bounty" in query.lower() or "bounties" in query.lower():
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=100,
                where={"type": "bounty"},
                include=["metadatas", "documents", "distances"]
            )
            
            retrieved_docs = []
            for i in range(len(results["documents"][0])):
                doc = results["documents"][0][i]
                if doc is None: continue
                    
                metadata = results["metadatas"][0][i]
                score = 1.0 - results["distances"][0][i]
                
                if "$" in query:
                    query_parts = query.split("$")
                    if len(query_parts) > 1:
                        value_part = query_parts[1].split()[0]
                        if value_part.isdigit():
                            target_value = f"${value_part}"
                            if metadata.get("value") != target_value:
                                continue
                            
                retrieved_docs.append({"content": doc, "metadata": metadata, "score": score})
            retrieved_docs = sorted(retrieved_docs, key=lambda x: x["score"], reverse=True)[:20]
            return retrieved_docs
            
        else:
            tutorial_results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=10,
                where={"type": "tutorial"},
                include=["metadatas", "documents", "distances"]
            )
            
            other_results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where={"type": {"$ne": "tutorial"}},
                include=["metadatas", "documents", "distances"]
            )
            
            retrieved_docs = []
            
            for i in range(len(tutorial_results["documents"][0])):
                doc = tutorial_results["documents"][0][i]
                if doc is None: continue
                retrieved_docs.append({
                    "content": doc,
                    "metadata": tutorial_results["metadatas"][0][i],
                    "score": 1.0 - tutorial_results["distances"][0][i]
                })
            
            for i in range(len(other_results["documents"][0])):
                doc = other_results["documents"][0][i]
                if doc is None: continue
                retrieved_docs.append({
                    "content": doc,
                    "metadata": other_results["metadatas"][0][i],
                    "score": 1.0 - other_results["distances"][0][i]
                })
            
            retrieved_docs = sorted(retrieved_docs, key=lambda x: x["score"], reverse=True)
            return retrieved_docs
