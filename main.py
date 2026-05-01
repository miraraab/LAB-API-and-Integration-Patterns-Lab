"""Main application entry point."""

import asyncio
import logging
import sys

from config import Config
from summarizer import AsyncNewsSummarizer, NewsSummarizer

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Run the interactive news summarizer."""
    try:
        Config.validate()

        print("=" * 80)
        print("NEWS SUMMARIZER - Multi-Provider Edition")
        print("=" * 80)

        category = (
            input("\nEnter news category (technology/business/health/general): ").strip()
            or "technology"
        )
        raw_count = input("How many articles to process? (1-10): ").strip()
        use_async = input("Use async processing? (y/n): ").strip().lower() == "y"

        try:
            num_articles = max(1, min(10, int(raw_count)))
        except ValueError:
            num_articles = 3

        summarizer = AsyncNewsSummarizer() if use_async else NewsSummarizer()
        print(f"\nFetching {num_articles} articles from category: {category}")
        articles = summarizer.fetch_top_headlines(
            category=category,
            country="us",
            max_articles=num_articles,
        )

        if not articles:
            print("No articles fetched. Check your NewsAPI key or try another category.")
            return

        if use_async:
            print(f"\nProcessing {len(articles)} articles concurrently...")
            results = asyncio.run(summarizer.process_articles_async(articles, max_concurrent=3))
        else:
            print(f"\nProcessing {len(articles)} articles...")
            results = summarizer.process_articles(articles)

        summarizer.generate_report(results)
        print("\nProcessing complete.")

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as error:
        logger.error("Application failed: %s", error)
        sys.exit(1)


if __name__ == "__main__":
    main()
