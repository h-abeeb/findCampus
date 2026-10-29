from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


FIELDS = ("title", "description", "category", "location")


def find_matches(item, candidates):
    if not candidates:
        return []
    documents = [
        " ".join(str(row.get(field) or "") for field in FIELDS)
        for row in [item, *candidates]
    ]
    if not any(character.isalnum() for document in documents for character in document):
        return []

    vectors = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b").fit_transform(documents)
    scores = cosine_similarity(vectors[0:1], vectors[1:]).ravel()
    matches = [
        {**candidate, "score": float(score)}
        for candidate, score in zip(candidates, scores)
        if score >= 0.2
    ]
    return sorted(matches, key=lambda match: match["score"], reverse=True)[:3]
