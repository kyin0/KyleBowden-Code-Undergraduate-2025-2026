import json
from pathlib import Path

def load_corpus(base_path : str | Path) -> list[dict]:

    """
    A function to load a specific corpus' chunks
    
    :param base_path: Path to the base folder for knowledge
    :type base_path: str
    :return: List of each chunk including id, title, tags, source and the content of the chunk.
    :rtype: list[dict]
    """

    base_path = Path(base_path)
    index_path = base_path / "index.json"

    with open(index_path, "r", encoding="UTF-8-SIG") as f:
        index_content = json.load(f)

    output_chunks : list[dict] = []

    for chunk in index_content["chunks"]:
        chunk_file = base_path / chunk["path"]

        with open(chunk_file, "r", encoding="UTF-8") as cf:
            chunk_text = cf.read()

        output_chunks.append({
            "id": chunk["id"],
            "title": chunk["title"],
            "tags": chunk["tags"],
            "source": chunk["source"],
            "text": chunk_text
        })

    return output_chunks