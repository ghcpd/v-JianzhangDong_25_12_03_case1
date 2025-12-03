import regex
from tqdm import tqdm


def extract_keywords(texts):
    """Use regex to extract words > 4 chars."""
    results = []
    for t in tqdm(texts, desc="Extracting"):
        words = regex.findall(r"\b\w{5,}\b", t)
        results.append(words)
    return results
