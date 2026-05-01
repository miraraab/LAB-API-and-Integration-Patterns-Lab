"""News API integration module."""

import requests
from typing import List, Dict, Optional
import logging
import time
from config import Config

logger = logging.getLogger(__name__)


class NewsAPIClient:
    """Client for fetching news from NewsAPI."""
    
    def __init__(self, api_key: str = None):
        """Initialize the NewsAPI client.
        
        Args:
            api_key: API key for NewsAPI. Uses env var if not provided.
        """
        self.api_key = api_key or Config.NEWS_API_KEY
        self.base_url = Config.NEWS_API_URL
        self.timeout = Config.REQUEST_TIMEOUT
        self.last_call_time = 0.0
        self.min_interval = 60.0 / Config.NEWS_API_RPM
        
        if not self.api_key:
            logger.warning("NEWS_API_KEY not configured")

    def _wait_if_needed(self):
        """Apply simple per-process rate limiting."""
        elapsed = time.time() - self.last_call_time
        if elapsed < self.min_interval:
            wait_time = self.min_interval - elapsed
            logger.info("Rate limiting NewsAPI for %.2fs", wait_time)
            time.sleep(wait_time)
        self.last_call_time = time.time()

    @staticmethod
    def _normalize_article(article: Dict) -> Dict:
        """Return the article shape used by the summarizer."""
        return {
            "title": article.get("title") or "",
            "description": article.get("description") or "",
            "content": article.get("content") or "",
            "url": article.get("url") or "",
            "source": article.get("source", {}).get("name", "Unknown"),
            "published_at": article.get("publishedAt") or "",
        }
    
    def get_top_headlines(
        self,
        query: Optional[str] = None,
        country: Optional[str] = "us",
        category: Optional[str] = None,
        page_size: int = 10
    ) -> List[Dict]:
        """Fetch top headlines from NewsAPI.
        
        Args:
            query: Search query
            country: ISO 3166-1 alpha-2 country code
            category: News category
            page_size: Number of articles to fetch
            
        Returns:
            List of article dictionaries
        """
        self._wait_if_needed()

        try:
            endpoint = f"{self.base_url}/top-headlines"
            params = {
                "apiKey": self.api_key,
                "pageSize": page_size,
            }
            
            if country:
                params["country"] = country
            if query:
                params["q"] = query
            if category:
                params["category"] = category
            
            response = requests.get(
                endpoint,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "ok":
                return [
                    self._normalize_article(article)
                    for article in data.get("articles", [])
                ]
            else:
                logger.error(f"NewsAPI error: {data.get('message')}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching headlines: {e}")
            return []
    
    def search_articles(
        self,
        query: str,
        sort_by: str = "publishedAt",
        page_size: int = 10,
        page: int = 1
    ) -> List[Dict]:
        """Search for articles using NewsAPI.
        
        Args:
            query: Search query
            sort_by: Sort order (publishedAt, relevancy, popularity)
            page_size: Number of articles per page
            page: Page number
            
        Returns:
            List of article dictionaries
        """
        self._wait_if_needed()

        try:
            endpoint = f"{self.base_url}/everything"
            params = {
                "apiKey": self.api_key,
                "q": query,
                "sortBy": sort_by,
                "pageSize": page_size,
                "page": page,
            }
            
            response = requests.get(
                endpoint,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "ok":
                return [
                    self._normalize_article(article)
                    for article in data.get("articles", [])
                ]
            else:
                logger.error(f"NewsAPI error: {data.get('message')}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching articles: {e}")
            return []
