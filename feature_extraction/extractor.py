"""
Feature Extractor – generates TF‑IDF vectors for matching.
Uses only scikit‑learn for fast, reliable scoring without heavy model downloads.
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class FeatureExtractor:
    """TF-IDF based feature extraction — fast and dependency-light."""

    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
        )

    # ------------------------------------------------------------------ #
    #  TF‑IDF
    # ------------------------------------------------------------------ #
    def tfidf_vectors(self, documents: list[str]) -> np.ndarray:
        """Fit‑transform a list of documents and return TF‑IDF matrix."""
        return self.tfidf_vectorizer.fit_transform(documents).toarray()

    # ------------------------------------------------------------------ #
    #  Sentence embeddings (lightweight TF-IDF based)
    # ------------------------------------------------------------------ #
    def sentence_embeddings(self, documents: list[str]) -> np.ndarray:
        """
        Return document vectors using weighted TF-IDF with higher n-gram range.
        This replaces the heavy SentenceTransformer model with a fast alternative
        that still captures semantic similarity through n-gram overlap.
        """
        vectorizer = TfidfVectorizer(
            max_features=8000,
            stop_words='english',
            ngram_range=(1, 3),
            sublinear_tf=True,
        )
        return vectorizer.fit_transform(documents).toarray()
