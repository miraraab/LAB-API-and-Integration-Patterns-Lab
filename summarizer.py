"""News summarizer with multi-provider support."""

import asyncio
import logging
from typing import Dict, List

from llm_providers import LLMProviders
from news_api import NewsAPIClient

logger = logging.getLogger(__name__)


class NewsSummarizer:
    """Fetch, summarize, analyze, and report on news articles."""

    def __init__(self):
        self.news_client = NewsAPIClient()
        self.llm_providers = LLMProviders()

    @staticmethod
    def _article_text(article: Dict) -> str:
        """Build compact article text for LLM prompts."""
        return f"""Title: {article.get("title", "")}
Description: {article.get("description", "")}
Content: {article.get("content", "")[:500]}"""

    def summarize_article(self, article: Dict) -> Dict:
        """Summarize one article and analyze sentiment."""
        title = article.get("title", "Untitled")
        logger.info("Processing article: %s", title[:80])

        article_text = self._article_text(article)
        summary_prompt = f"""Summarize this news article in 2-3 sentences:

{article_text}"""

        summary_result = self.llm_providers.ask_with_fallback(
            summary_prompt,
            primary="openai",
            max_tokens=180,
        )
        summary = summary_result["response"]

        sentiment_prompt = f"""Analyze the sentiment of this article summary:

"{summary}"

Provide:
- Overall sentiment (positive, negative, or neutral)
- Confidence (0-100%)
- Key emotional tone

Be concise."""

        try:
            sentiment = self.llm_providers.ask_anthropic(sentiment_prompt, max_tokens=160)
            sentiment_provider = "anthropic"
        except Exception as error:
            logger.warning("Anthropic sentiment analysis failed: %s", error)
            fallback = self.llm_providers.ask_with_fallback(
                sentiment_prompt,
                primary="openai",
                max_tokens=160,
            )
            sentiment = fallback["response"]
            sentiment_provider = fallback["provider"]

        return {
            "title": title,
            "source": article.get("source", "Unknown"),
            "url": article.get("url", ""),
            "published_at": article.get("published_at", ""),
            "summary": summary,
            "summary_provider": summary_result["provider"],
            "sentiment": sentiment,
            "sentiment_provider": sentiment_provider,
        }

    def process_articles(self, articles: List[Dict]) -> List[Dict]:
        """Process multiple articles sequentially."""
        results = []
        for article in articles:
            try:
                results.append(self.summarize_article(article))
            except Exception as error:
                logger.error("Failed to process article: %s", error)
        return results

    def fetch_top_headlines(
        self,
        category: str = None,
        country: str = "us",
        max_articles: int = 3,
    ) -> List[Dict]:
        """Fetch top headlines from NewsAPI."""
        return self.news_client.get_top_headlines(
            country=country,
            category=category,
            page_size=max_articles,
        )

    def search_articles(self, query: str, max_articles: int = 3) -> List[Dict]:
        """Search articles from NewsAPI."""
        return self.news_client.search_articles(query=query, page_size=max_articles)

    def generate_report(self, results: List[Dict]):
        """Print a summary report and cost summary."""
        print("\n" + "=" * 80)
        print("NEWS SUMMARY REPORT")
        print("=" * 80)

        for index, result in enumerate(results, 1):
            print(f"\n{index}. {result['title']}")
            print(f"   Source: {result['source']} | Published: {result['published_at']}")
            print(f"   URL: {result['url']}")
            print(f"   Summary provider: {result['summary_provider']}")
            print(f"   Sentiment provider: {result['sentiment_provider']}")
            print("\n   SUMMARY:")
            print(f"   {result['summary']}")
            print("\n   SENTIMENT:")
            print(f"   {result['sentiment']}")
            print(f"\n   {'-' * 76}")

        cost_summary = self.llm_providers.cost_tracker.get_summary()
        print("\n" + "=" * 80)
        print("COST SUMMARY")
        print("=" * 80)
        print(f"Total requests: {cost_summary['total_requests']}")
        print(f"Total cost: ${cost_summary['total_cost']:.4f}")
        print(
            "Total tokens: "
            f"{cost_summary['total_input_tokens'] + cost_summary['total_output_tokens']:,}"
        )
        print(f"  Input: {cost_summary['total_input_tokens']:,}")
        print(f"  Output: {cost_summary['total_output_tokens']:,}")
        print(f"Average cost per request: ${cost_summary['average_cost']:.6f}")
        print("=" * 80)


class AsyncNewsSummarizer(NewsSummarizer):
    """Async wrapper for processing multiple articles concurrently."""

    async def summarize_article_async(self, article: Dict) -> Dict:
        """Run the synchronous article processor in a worker thread."""
        return await asyncio.to_thread(self.summarize_article, article)

    async def process_articles_async(self, articles: List[Dict], max_concurrent: int = 3) -> List[Dict]:
        """Process articles concurrently with a semaphore."""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_with_limit(article):
            async with semaphore:
                return await self.summarize_article_async(article)

        results = await asyncio.gather(
            *(process_with_limit(article) for article in articles),
            return_exceptions=True,
        )
        return [result for result in results if not isinstance(result, Exception)]


if __name__ == "__main__":
    summarizer = NewsSummarizer()
    articles = summarizer.fetch_top_headlines(category="technology", max_articles=2)
    if articles:
        summarizer.generate_report(summarizer.process_articles(articles))
    else:
        print("No articles fetched. Check your NewsAPI key.")
