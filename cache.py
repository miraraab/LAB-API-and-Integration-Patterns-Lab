"""Simple JSON cache for processed article results."""

import hashlib
import json
import logging
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ArticleCache:
    """Persist processed article results to avoid repeated LLM calls."""

    def __init__(self, cache_path: str = ".cache/articles.json"):
        self.cache_path = Path(cache_path)
        self._lock = threading.Lock()

    @staticmethod
    def make_key(article: Dict) -> str:
        """Create a stable cache key for an article."""
        source = article.get("url") or "|".join(
            [
                article.get("title", ""),
                article.get("published_at", ""),
                article.get("content", ""),
            ]
        )
        return hashlib.sha256(source.encode("utf-8")).hexdigest()

    def _load(self) -> Dict:
        """Load cache data from disk."""
        if not self.cache_path.exists():
            return {}

        try:
            with self.cache_path.open("r", encoding="utf-8") as cache_file:
                return json.load(cache_file)
        except (json.JSONDecodeError, OSError) as error:
            logger.warning("Could not read cache file: %s", error)
            return {}

    def _save(self, data: Dict):
        """Write cache data to disk."""
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        with self.cache_path.open("w", encoding="utf-8") as cache_file:
            json.dump(data, cache_file, indent=2, sort_keys=True)

    def get(self, article: Dict) -> Optional[Dict]:
        """Return cached result for an article if available."""
        key = self.make_key(article)
        with self._lock:
            cached = self._load().get(key)

        if not cached:
            return None

        result = dict(cached["result"])
        result["cache_hit"] = True
        return result

    def set(self, article: Dict, result: Dict):
        """Store a processed article result."""
        key = self.make_key(article)
        cache_entry = {
            "cached_at": datetime.now(timezone.utc).isoformat(),
            "article_url": article.get("url", ""),
            "article_title": article.get("title", ""),
            "result": result,
        }

        with self._lock:
            data = self._load()
            data[key] = cache_entry
            self._save(data)
