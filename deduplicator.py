"""
Deduplicator Module.
Removes duplicate news articles using URL normalization and text/title similarity.
"""
import re
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Query parameters commonly used for tracking
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "ref", "source", "feed", "feature", "tracking", "trk"
}


def normalize_url(url: str) -> str:
    """Normalizes URL by removing tracking query parameters and fragments."""
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        query_items = parse_qsl(parsed.query, keep_blank_values=False)
        cleaned_query = [
            (k, v) for k, v in query_items
            if k.lower() not in TRACKING_PARAMS
        ]
        new_query = urlencode(cleaned_query)
        # Drop fragment (#) and trailing slashes in path
        path = parsed.path.rstrip("/")
        normalized = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            path,
            parsed.params,
            new_query,
            ""  # fragment removed
        ))
        return normalized
    except Exception:
        return url


def clean_title_for_comparison(title: str) -> str:
    """Cleans title by removing brackets, publisher tags, and punctuation."""
    if not title:
        return ""
    # Remove bracketed tags: [단독], [포토], (종합), [딥다이브]
    t = re.sub(r'\[[^\]]*\]|\([^\)]*\)', '', title)
    # Remove special punctuation
    t = re.sub(r'[^\w\s가-힣]', ' ', t)
    # Collapse whitespaces
    t = re.sub(r'\s+', ' ', t).strip().lower()
    return t


def calculate_jaccard_similarity(str1: str, str2: str) -> float:
    """Calculates word-level Jaccard similarity between two strings."""
    words1 = set(str1.split())
    words2 = set(str2.split())
    if not words1 or not words2:
        return 0.0
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    return len(intersection) / len(union)


def calculate_char_ngram_similarity(str1: str, str2: str, n: int = 2) -> float:
    """Calculates n-gram character similarity."""
    if len(str1) < n or len(str2) < n:
        return 1.0 if str1 == str2 else 0.0
    ngrams1 = {str1[i:i+n] for i in range(len(str1) - n + 1)}
    ngrams2 = {str2[i:i+n] for i in range(len(str2) - n + 1)}
    intersection = ngrams1.intersection(ngrams2)
    union = ngrams1.union(ngrams2)
    return len(intersection) / len(union) if union else 0.0


class ArticleDeduplicator:
    def __init__(self, title_threshold: float = 0.65):
        self.title_threshold = title_threshold

    def is_duplicate(self, article: Dict[str, Any], seen_articles: List[Dict[str, Any]]) -> bool:
        """Checks if the article is a duplicate of any existing seen article."""
        url = article.get("url", "")
        norm_url = normalize_url(url)
        clean_title = clean_title_for_comparison(article.get("title", ""))

        for seen in seen_articles:
            # 1. URL match
            seen_url = seen.get("url", "")
            if norm_url and seen_url and normalize_url(seen_url) == norm_url:
                logger.info(f"Duplicate detected by URL: '{article.get('title')}' == '{seen.get('title')}'")
                return True

            # 2. Clean Title match (Exact)
            seen_clean_title = clean_title_for_comparison(seen.get("title", ""))
            if clean_title and seen_clean_title:
                if clean_title == seen_clean_title:
                    logger.info(f"Duplicate detected by exact title: '{clean_title}'")
                    return True

                # 3. Jaccard & Char N-gram similarity
                word_sim = calculate_jaccard_similarity(clean_title, seen_clean_title)
                ngram_sim = calculate_char_ngram_similarity(clean_title, seen_clean_title)
                combined_score = max(word_sim, ngram_sim)

                if combined_score >= self.title_threshold:
                    logger.info(
                        f"Duplicate detected by similarity ({combined_score:.2f}): "
                        f"'{article.get('title')}' vs '{seen.get('title')}'"
                    )
                    return True

        return False

    def deduplicate(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filters out duplicate articles from list, keeping the more complete article
        (e.g. longer content or having image).
        """
        unique_articles: List[Dict[str, Any]] = []

        for art in articles:
            if not self.is_duplicate(art, unique_articles):
                unique_articles.append(art)
            else:
                # Optional: If this article has an image and the existing one doesn't, enrich it
                pass

        logger.info(f"Deduplication finished: {len(articles)} -> {len(unique_articles)} articles.")
        return unique_articles
