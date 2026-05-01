"""SQLite storage for processed news articles."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from cache import ArticleCache


class ArticleStore:
    """Persist processed article results in SQLite."""

    def __init__(self, db_path: str = ".data/news_summaries.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        """Create a SQLite connection."""
        return sqlite3.connect(self.db_path)

    def _initialize(self):
        """Create database tables if they do not exist."""
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS processed_articles (
                    cache_key TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    source TEXT,
                    url TEXT,
                    published_at TEXT,
                    summary TEXT,
                    summary_provider TEXT,
                    sentiment TEXT,
                    sentiment_provider TEXT,
                    cache_hit INTEGER DEFAULT 0,
                    processed_at TEXT NOT NULL,
                    raw_result TEXT NOT NULL
                )
                """
            )

    def save_result(self, article: Dict, result: Dict):
        """Insert or update a processed article result."""
        cache_key = ArticleCache.make_key(article)
        stored_result = dict(result)
        stored_result["cache_hit"] = bool(result.get("cache_hit", False))

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO processed_articles (
                    cache_key,
                    title,
                    source,
                    url,
                    published_at,
                    summary,
                    summary_provider,
                    sentiment,
                    sentiment_provider,
                    cache_hit,
                    processed_at,
                    raw_result
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(cache_key) DO UPDATE SET
                    title = excluded.title,
                    source = excluded.source,
                    url = excluded.url,
                    published_at = excluded.published_at,
                    summary = excluded.summary,
                    summary_provider = excluded.summary_provider,
                    sentiment = excluded.sentiment,
                    sentiment_provider = excluded.sentiment_provider,
                    cache_hit = excluded.cache_hit,
                    processed_at = excluded.processed_at,
                    raw_result = excluded.raw_result
                """,
                (
                    cache_key,
                    result.get("title", ""),
                    result.get("source", ""),
                    result.get("url", ""),
                    result.get("published_at", ""),
                    result.get("summary", ""),
                    result.get("summary_provider", ""),
                    result.get("sentiment", ""),
                    result.get("sentiment_provider", ""),
                    int(bool(result.get("cache_hit", False))),
                    datetime.now(timezone.utc).isoformat(),
                    json.dumps(stored_result, sort_keys=True),
                ),
            )

    def list_recent(self, limit: int = 20) -> List[Dict]:
        """Return recently processed article results."""
        with self._connect() as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT raw_result
                FROM processed_articles
                ORDER BY processed_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [json.loads(row["raw_result"]) for row in rows]

    def count(self) -> int:
        """Return number of stored processed articles."""
        with self._connect() as connection:
            row = connection.execute("SELECT COUNT(*) FROM processed_articles").fetchone()
        return int(row[0])
