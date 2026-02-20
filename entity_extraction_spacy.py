import spacy
import json

nlp = spacy.load("en_core_web_sm")

algorithm_list = ["cnn", "rnn", "lstm", "transformer", "bert", "resnet"]
dataset_list = ["imagenet", "mnist", "cifar-10"]

INPUT_FILE = "data/processed/papers.json"
OUTPUT_FILE = "data/processed/entities.json"


def classify_entity(text, label):
    text_lower = text.lower()

    if label == "PERSON":
        return "Author"
    elif text_lower in algorithm_list:
        return "Algorithm"
    elif text_lower in dataset_list:
        return "Dataset"
    elif label == "ORG":
        return "Organization"
    else:
        return "Concept"


def extract_entities():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        papers = json.load(f)

    results = []

    for paper in papers:
        paper_id = paper["paper_id"]
        abstract = paper.get("abstract", "")

        doc = nlp(abstract)

        entities = []

        for ent in doc.ents:
            entity_type = classify_entity(ent.text, ent.label_)
            entities.append({
                "name": ent.text.strip(),
                "type": entity_type
            })

        results.append({
            "paper_id": paper_id,
            "entities": entities
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    print("Entity extraction completed.")


if __name__ == "__main__":
    extract_entities()
