from neo4j import GraphDatabase
import json

URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "neoasmy123"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

PAPERS_FILE = "data/processed/papers.json"
ENTITIES_FILE = "data/processed/entities.json"


def create_paper(tx, paper_id):
    tx.run("""
        MERGE (p:Paper {paper_id:$paper_id})
    """, paper_id=paper_id)


def create_entity_relationship(tx, paper_id, entity_name, entity_type):

    relationship_type = "MENTIONS"

    if entity_type == "Algorithm":
        relationship_type = "USES"
    elif entity_type == "Dataset":
        relationship_type = "USES_DATASET"

    query = f"""
        MERGE (p:Paper {{paper_id:$paper_id}})
        MERGE (e:{entity_type} {{name:$entity_name}})
        MERGE (p)-[:{relationship_type}]->(e)
    """

    tx.run(query, paper_id=paper_id, entity_name=entity_name)


def load_data():

    with open(PAPERS_FILE, "r", encoding="utf-8") as f:
        papers = json.load(f)

    with open(ENTITIES_FILE, "r", encoding="utf-8") as f:
        entities_data = json.load(f)

    with driver.session() as session:

        # Create paper nodes
        for paper in papers:
            session.write_transaction(create_paper, paper["paper_id"])

        # Create entity relationships
        for item in entities_data:
            paper_id = item["paper_id"]

            for entity in item["entities"]:
                session.write_transaction(
                    create_entity_relationship,
                    paper_id,
                    entity["name"],
                    entity["type"]
                )

    print("Graph successfully loaded into Neo4j.")


if __name__ == "__main__":
    load_data()
    driver.close()
