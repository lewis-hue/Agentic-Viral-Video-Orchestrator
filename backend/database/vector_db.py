import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class VectorDB:
    def __init__(self, index_path: str):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = faiss.IndexFlatL2(384)  # Dimension for the model
        self.index_path = index_path
        self.load_index()

    def load_index(self):
        try:
            self.index = faiss.read_index(self.index_path)
        except:
            pass  # Index doesn't exist yet

    def save_index(self):
        faiss.write_index(self.index, self.index_path)

    def add_trend(self, trend: str):
        embedding = self.model.encode([trend])
        self.index.add(np.array(embedding))
        self.save_index()

    def search(self, query: str, k: int = 5):
        embedding = self.model.encode([query])
        distances, indices = self.index.search(np.array(embedding), k)
        return distances, indices