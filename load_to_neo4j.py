from neo4j import GraphDatabase
import json
import re

URL = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "neoasmyta123"

TRIPLES_FILE = "data/processed/triples.json"

driver = GraphDatabase.driver(
    URL,
    auth=(USERNAME, PASSWORD)
)

# ----------------------------
# Clean Relationship Name
# ----------------------------
def clean_relationship(rel):
    rel = rel.upper()
    rel = rel.replace(" ", "_")
    rel = re.sub(r"[^A-Z_]", "", rel)
    return rel


# ----------------------------
# 👇 PUT YOUR NEW FUNCTION HERE
# ----------------------------
def create_triple(tx, subj, pred, obj):

    relationship = clean_relationship(pred)

    # Clean names to avoid duplicates
    subj = subj.strip()
    obj = obj.strip()

    if relationship == "WRITTEN_BY":
        obj_label = "Author"

    elif relationship == "PUBLISHED_IN":
        obj_label = "Organization"

    elif relationship == "USES":
        obj_label = "Algorithm"

    elif relationship == "USES_DATASET":
        obj_label = "Dataset"

    elif relationship == "EVALUATED_BY":
        obj_label = "Metric"

    else:
        obj_label = "Concept"

    query = f"""
        MERGE (p:Paper {{name: $subj}})
        MERGE (o:{obj_label} {{name: $obj}})
        MERGE (p)-[:{relationship}]->(o)
    """

    tx.run(query, subj=subj, obj=obj)



# ----------------------------
# Main Function
# ----------------------------
def main():

    with open(TRIPLES_FILE, "r", encoding="utf-8") as f:
        triples = json.load(f)

    with driver.session(database="neo4j") as session:

        for t in triples:
            session.execute_write(
                create_triple,
                t["subject"],
                t["predicate"],
                t["object"]
            )

    print("✅ Triples successfully loaded into Neo4j")


if __name__ == "__main__":
    main()
    driver.close()
