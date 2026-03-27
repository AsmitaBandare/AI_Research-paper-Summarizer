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

    query_embedding = model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")

    distances, indices = index.search(query_embedding, top_k)

    raw_distance = distances[0][0]

    #  IMPORTANT: This is L2 distance (IndexFlatL2)
    # Smaller = better
    threshold = 1.5   # stricter threshold (reduce if still wrong answers)

    # Confidence calculation
    max_distance = 3.0
    confidence = max(0, (1 - (raw_distance / max_distance))) * 100

    # for  STRICT FILTER
    if raw_distance > threshold:
        return None, None, None

    vector_results = []
    retrieved_paper_ids = []

    for i in indices[0]:
        vector_results.append(texts[i])
        retrieved_paper_ids.append(paper_ids[i])

    kg_results = []
    for pid in set(retrieved_paper_ids):
        kg_results.extend(query_kg(pid))

    return vector_results, kg_results, confidence



# -------------------------
# Grounding Score
# -------------------------
def calculate_grounding(answer, context):

    answer_words = set(answer.lower().split())
    context_words = set(context.lower().split())

    if len(answer_words) == 0:
        return 0

    overlap = answer_words.intersection(context_words)

    return (len(overlap) / len(answer_words)) * 100




# -------------------------
# Generate Answer
# -------------------------
def generate_answer(query):

    vector_context, kg_context, confidence = hybrid_retrieve(query)

    # If unrelated → STOP immediately
    if vector_context is None:
        return "Did not find the relatable answer", None, None

    combined_context = f"""
You are an academic research assistant.

Answer the question STRICTLY using only the information below.
Do not add external knowledge.

Vector Retrieved Content:
{vector_context}

Knowledge Graph Retrieved Facts:
{kg_context}

Question:
{query}
"""

    response = ollama.chat(
        model="tinyllama",
        messages=[{"role": "user", "content": combined_context}]
    )

    answer = response["message"]["content"]

    full_context = str(vector_context) + " " + str(kg_context)
    grounding = calculate_grounding(answer, full_context)

    return answer, confidence, grounding

# -------------------------
# Function for UI
# -------------------------
def ask_question(query):

    answer, confidence, grounding = generate_answer(query)

    return {
        "answer": answer,
        "confidence_score": round(confidence, 2) if confidence is not None else 0,
        "grounding_score": round(grounding, 2) if grounding is not None else 0
    }