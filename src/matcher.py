"""
Automated Resume Screening Tool — Lexical Relevance & TF-IDF Matcher.

Computes textual relevance using joint TF-IDF n-gram vectorization and
cosine similarity in the vector space, bounded strictly within [0.0, 100.0]%.
Identifies top shared lexical terms for explainable scoring.
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Token pattern capturing alphanumeric tokens and programming symbols (c++, c#, .net, node.js, ci/cd)
TOKEN_PATTERN = r"(?u)\b\w[\w\.\+\#\-\/]*\b"

def compute_tfidf_similarity(
    cleaned_resume_text: str,
    cleaned_jd_text: str,
    top_n_terms: int = 5
) -> dict:
    """
    Calculate the cosine similarity between candidate resume text and target
    job description in the joint TF-IDF vector space.

    Args:
        cleaned_resume_text: Normalized candidate resume string.
        cleaned_jd_text: Normalized job description string.
        top_n_terms: Number of top shared lexical contributors to return.

    Returns:
        dict: {
            "tfidf_similarity": float,       # Cosine similarity (0.0 to 1.0)
            "tfidf_percentage": float,       # Scaled percentage (0.0 to 100.0)
            "top_shared_terms": list[str]    # Most influential shared n-grams
        }
    """
    # Guard against empty documents
    if not cleaned_resume_text.strip() or not cleaned_jd_text.strip():
        return {
            "tfidf_similarity": 0.0,
            "tfidf_percentage": 0.0,
            "top_shared_terms": []
        }

    try:
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            token_pattern=TOKEN_PATTERN,
            sublinear_tf=True
        )

        # Fit joint vocabulary across both documents
        tfidf_matrix = vectorizer.fit_transform([cleaned_jd_text, cleaned_resume_text])
        v_jd = tfidf_matrix[0]
        v_res = tfidf_matrix[1]

        # Cosine similarity
        sim = float(cosine_similarity(v_jd, v_res)[0][0])
        sim_bounded = max(0.0, min(1.0, sim))
        percentage = round(sim_bounded * 100.0, 2)

        # Decompose top shared terms via element-wise vector product
        prod = (v_jd.toarray()[0]) * (v_res.toarray()[0])
        feature_names = np.array(vectorizer.get_feature_names_out())
        sorted_indices = np.argsort(prod)[::-1]
        
        shared_terms = [
            str(feature_names[idx])
            for idx in sorted_indices
            if prod[idx] > 0
        ][:top_n_terms]

        return {
            "tfidf_similarity": round(sim_bounded, 4),
            "tfidf_percentage": percentage,
            "top_shared_terms": shared_terms
        }

    except Exception:
        # Fallback for unexpected matrix or numerical conditions
        return {
            "tfidf_similarity": 0.0,
            "tfidf_percentage": 0.0,
            "top_shared_terms": []
        }
