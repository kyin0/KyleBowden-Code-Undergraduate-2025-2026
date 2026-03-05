import re
from collections import Counter

def tokenize(text : str) -> list[str]:
    return re.findall(r"\b[a-zA-Z_]+\b", text.lower())

def score_chunk(chunk : dict, query_tokens : list[str]) -> float:

    score = 0.0

    chunk_tags = [t.lower() for t in chunk["tags"]]
    chunk_title_tokens = tokenize(chunk["title"])
    chunk_text_tokens = tokenize(chunk["text"])

    text_counts = Counter(chunk_text_tokens)

    for token in query_tokens:

        if token in chunk_tags:
            score += 5.0
        
        if token in chunk_title_tokens:
            score += 2.0
        
        score += 0.1 * text_counts.get(token, 0)
    
    return score

def retrieve(chunks : list[dict], query : str, k : int = 8) -> list[dict]:
    query_tokens = tokenize(query)

    scored = []

    for chunk in chunks:
        s = score_chunk(chunk, query_tokens)
        scored.append((s, chunk))

    scored.sort(key=lambda x : x[0], reverse=True)

    return [chunk for score, chunk in scored[:k] if score > 0]
