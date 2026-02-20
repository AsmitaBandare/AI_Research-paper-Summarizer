import json
from pathlib import Path

# Paths
PROCESSED_DIR = Path("data/processed")
PAPERS_FILE = PROCESSED_DIR / "papers.json"
CHUNKS_FILE = PROCESSED_DIR / "chunks.json"

CHUNK_SIZE = 500  # words


def chunk_text(text, chunk_size=500):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks


def main():
    with open(PAPERS_FILE, "r", encoding="utf-8") as f:
        papers = json.load(f)

    all_chunks = []

    for paper in papers:
        paper_id = paper["paper_id"]

        # Abstract chunk
        if "abstract" in paper and paper["abstract"].strip():
            all_chunks.append({
                "paper_id": paper_id,
                "chunk_id": f"{paper_id}_ABS",
                "chunk_type": "abstract",
                "text": paper["abstract"].strip()
            })

        # Body text chunks
        body_chunks = chunk_text(paper["text"])

        for idx, chunk in enumerate(body_chunks, start=1):
            all_chunks.append({
                "paper_id": paper_id,
                "chunk_id": f"{paper_id}_C{idx:03}",
                "chunk_type": "body",
                "text": chunk
            })

    with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"✅ Chunking completed. Total chunks: {len(all_chunks)}")


if __name__ == "__main__":
    main()
