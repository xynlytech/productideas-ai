import logging

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN

logger = logging.getLogger(__name__)

# Lazy-loaded model
_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info("Loading sentence-transformer model (all-MiniLM-L6-v2)...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def cluster_signals(signals: list[dict], eps: float = 0.35, min_samples: int = 2) -> list[dict]:
    """
    Cluster normalized signals into topic groups using semantic embeddings + DBSCAN.

    Returns a list of cluster dicts:
    [
        {
            "label": str,       # Representative query
            "keywords": [{"keyword": str, "weight": float}, ...],
            "signals": [signal_dicts],
            "category": str | None,
        }
    ]
    """
    if not signals:
        return []

    queries = [s["query"] for s in signals]
    model = _get_model()

    logger.info(f"Embedding {len(queries)} queries...")
    embeddings = model.encode(queries, normalize_embeddings=True, show_progress_bar=False)

    # DBSCAN clustering on cosine distance (1 - cosine similarity)
    distance_matrix = 1 - np.dot(embeddings, embeddings.T)
    np.fill_diagonal(distance_matrix, 0)

    clustering = DBSCAN(eps=eps, min_samples=min_samples, metric="precomputed")
    labels = clustering.fit_predict(distance_matrix)

    # Group signals by cluster label
    cluster_map: dict[int, list[int]] = {}
    noise_indices = []
    for idx, label in enumerate(labels):
        if label == -1:
            noise_indices.append(idx)
        else:
            cluster_map.setdefault(label, []).append(idx)

    clusters = []

    for _label, indices in cluster_map.items():
        cluster_signals_list = [signals[i] for i in indices]
        cluster_queries = [queries[i] for i in indices]

        # Find centroid to pick representative label
        cluster_embeddings = embeddings[indices]
        centroid = cluster_embeddings.mean(axis=0)
        centroid_distances = np.linalg.norm(cluster_embeddings - centroid, axis=1)
        representative_idx = indices[np.argmin(centroid_distances)]

        # Compute keyword weights based on distance to centroid
        keywords = []
        for i, idx in enumerate(indices):
            weight = max(0.0, 1.0 - centroid_distances[i])
            keywords.append({"keyword": queries[idx], "weight": round(float(weight), 3)})
        keywords.sort(key=lambda k: k["weight"], reverse=True)

        clusters.append({
            "label": queries[representative_idx],
            "keywords": keywords,
            "signals": cluster_signals_list,
            "category": _infer_category(cluster_queries),
        })

    # Treat noise as individual single-signal clusters
    for idx in noise_indices:
        clusters.append({
            "label": queries[idx],
            "keywords": [{"keyword": queries[idx], "weight": 1.0}],
            "signals": [signals[idx]],
            "category": _infer_category([queries[idx]]),
        })

    logger.info(f"Clustered {len(signals)} signals into {len(clusters)} clusters ({len(noise_indices)} noise)")
    return clusters


# Simple rule-based category inference
CATEGORY_RULES = {
    "SaaS": ["software", "saas", "app", "tool", "platform", "dashboard", "api", "automation"],
    "E-commerce": ["shop", "store", "buy", "sell", "product", "marketplace", "ecommerce"],
    "Health & Wellness": ["health", "fitness", "diet", "wellness", "medical", "supplement"],
    "Education": ["learn", "course", "tutorial", "study", "education", "training"],
    "Finance": ["money", "finance", "invest", "bank", "budget", "crypto", "trading"],
    "Food & Beverage": ["food", "recipe", "restaurant", "meal", "cook", "drink"],
    "Home & Garden": ["home", "garden", "furniture", "decor", "renovation", "kitchen"],
    "Travel": ["travel", "hotel", "flight", "vacation", "trip", "booking"],
    "Entertainment": ["game", "movie", "music", "entertainment", "streaming"],
    "Productivity": ["productivity", "organize", "schedule", "plan", "workflow", "task"],
}


def _infer_category(queries: list[str]) -> str | None:
    combined = " ".join(queries).lower()
    scores = {}
    for category, keywords in CATEGORY_RULES.items():
        score = sum(1 for kw in keywords if kw in combined)
        if score > 0:
            scores[category] = score
    if scores:
        return max(scores, key=scores.get)
    return None
