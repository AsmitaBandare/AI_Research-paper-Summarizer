import json
from pathlib import Path

ENTITIES_FILE = Path("data/processed/entities.json")
TRIPLES_FILE = Path("data/processed/triples.json")


def main():

    with open(ENTITIES_FILE, "r", encoding="utf-8") as f:
        entities_data = json.load(f)

    triples = []

    for item in entities_data:
        paper_id = item["paper_id"]

        for entity in item["entities"]:

            if entity["type"] == "Algorithm":
                triples.append({
                    "subject": paper_id,
                    "predicate": "USES",
                    "object": entity["name"]
                })

            elif entity["type"] == "Dataset":
                triples.append({
                    "subject": paper_id,
                    "predicate": "USES_DATASET",
                    "object": entity["name"]
                })

            elif entity["type"] == "Organization":
                triples.append({
                    "subject": paper_id,
                    "predicate": "PUBLISHED_BY",
                    "object": entity["name"]
                })

            else:
                triples.append({
                    "subject": paper_id,
                    "predicate": "MENTIONS",
                    "object": entity["name"]
                })

    with open(TRIPLES_FILE, "w", encoding="utf-8") as f:
        json.dump(triples, f, indent=2)

    print(f"✅ Created {len(triples)} triples")


if __name__ == "__main__":
    main()
