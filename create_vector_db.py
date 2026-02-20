import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import pickle

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load papers.json
with open("data/processed/papers.json", "r", encoding="utf-8") as f:
    papers = json.load(f)

texts = []
paper_ids = []

for paper in papers:
    abstract = paper.get("abstract", "")
    if abstract:
        texts.append(abstract)
        paper_ids.append(paper["paper_id"])

# Create embeddings
embeddings = model.encode(texts)

# Convert to numpy
embeddings = np.array(embeddings).astype("float32")

# Create FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# Save index
if not os.path.exists("vector_db"):
    os.makedirs("vector_db")

faiss.write_index(index, "vector_db/faiss_index.index")

# Save metadata
with open("vector_db/metadata.pkl", "wb") as f:
    pickle.dump((texts, paper_ids), f)

print("✅ Vector database created successfully!")
