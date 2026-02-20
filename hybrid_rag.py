import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
import ollama

# -------------------------
# Load Embedding Model
# -------------------------
model = SentenceTransformer(
    "all-MiniLM-L6-v2",
    local_files_only=True
)


# -------------------------
# Load FAISS Index
# -------------------------
index = faiss.read_index("vector_db/faiss_index.index")

with open("vector_db/metadata.pkl", "rb") as f:
    texts, paper_ids = pickle.load(f)

# -------------------------
# Connect Neo4j
# -------------------------
driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "neoasmyta123") 
)

def query_kg(paper_id):
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Paper {name: $paper_id})-[r]->(e)
            RETURN p.name AS paper, type(r) AS relationship, e.name AS entity
        """, paper_id=paper_id)

        return [record.data() for record in result]


# -------------------------
# Hybrid Retrieval
# -------------------------
def hybrid_retrieve(query, top_k=3):

    # Vector search
    query_embedding = model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")

    distances, indices = index.search(query_embedding, top_k)

    vector_results = [texts[i] for i in indices[0]]

    # KG search
    kg_results = query_kg(query)
    print("Vector Results:", vector_results)
    print("KG Results:", kg_results)


    return vector_results, kg_results

# -------------------------
# Generate Summary
# -------------------------
def generate_summary(query):

    vector_context, kg_context = hybrid_retrieve(query)

    combined_context = f"""
    You are an academic research assistant.

Using ONLY the information provided below,
generate a structured research paper summary.

Structure:
1. Title
2. Authors
3. Problem Statement
4. Methodology
5. Key Findings
6. Conclusion

Vector Retrieved Content:
{vector_context}

Knowledge Graph Retrieved Facts:
{kg_context}

Do not add unrelated information.
Base your answer strictly on the context.
"""


    response = ollama.chat(
        model="tinyllama",
        messages=[{"role": "user", "content": combined_context}]
    )

    return response["message"]["content"]

# -------------------------
# Test
# -------------------------
if __name__ == "__main__":
    query = "P02"
    summary = generate_summary(query)
    print("\n===== GENERATED SUMMARY =====\n")
    print(summary)
