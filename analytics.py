"""Advanced analytics for processed news results."""

import re
from collections import Counter
from typing import Dict, List


STOP_WORDS = {
    "about",
    "after",
    "again",
    "against",
    "and",
    "are",
    "for",
    "from",
    "has",
    "have",
    "into",
    "its",
    "new",
    "not",
    "the",
    "this",
    "that",
    "with",
    "was",
    "will",
}


def classify_sentiment(sentiment_text: str) -> str:
    """Classify free-form sentiment text into positive, negative, or neutral."""
    text = sentiment_text.lower()
    if "negative" in text:
        return "negative"
    if "positive" in text:
        return "positive"
    return "neutral"


def extract_keywords(results: List[Dict], limit: int = 8) -> List[Dict]:
    """Extract frequent title and summary keywords."""
    words = []
    for result in results:
        text = f"{result.get('title', '')} {result.get('summary', '')}".lower()
        words.extend(
            word
            for word in re.findall(r"[a-z][a-z0-9]{2,}", text)
            if word not in STOP_WORDS
        )

    return [
        {"keyword": keyword, "count": count}
        for keyword, count in Counter(words).most_common(limit)
    ]


def analyze_results(results: List[Dict]) -> Dict:
    """Return aggregate analytics for processed results."""
    sentiment_counts = Counter(
        classify_sentiment(result.get("sentiment", "")) for result in results
    )
    source_counts = Counter(result.get("source") or "Unknown" for result in results)
    summary_provider_counts = Counter(
        result.get("summary_provider") or "unknown" for result in results
    )
    sentiment_provider_counts = Counter(
        result.get("sentiment_provider") or "unknown" for result in results
    )
    cache_hits = sum(1 for result in results if result.get("cache_hit"))

    return {
        "total_articles": len(results),
        "sentiment_counts": dict(sentiment_counts),
        "source_counts": dict(source_counts),
        "summary_provider_counts": dict(summary_provider_counts),
        "sentiment_provider_counts": dict(sentiment_provider_counts),
        "cache_hits": cache_hits,
        "cache_misses": len(results) - cache_hits,
        "top_keywords": extract_keywords(results),
    }


def format_analytics(analytics: Dict) -> str:
    """Format analytics as CLI-friendly text."""
    keywords = ", ".join(
        f"{item['keyword']} ({item['count']})"
        for item in analytics.get("top_keywords", [])
    ) or "None"
    sentiment = ", ".join(
        f"{label}: {count}"
        for label, count in sorted(analytics.get("sentiment_counts", {}).items())
    ) or "None"
    sources = ", ".join(
        f"{source}: {count}"
        for source, count in analytics.get("source_counts", {}).items()
    ) or "None"

    return "\n".join(
        [
            f"Total articles: {analytics.get('total_articles', 0)}",
            f"Sentiment: {sentiment}",
            f"Sources: {sources}",
            f"Cache hits: {analytics.get('cache_hits', 0)}",
            f"Cache misses: {analytics.get('cache_misses', 0)}",
            f"Top keywords: {keywords}",
        ]
    )
