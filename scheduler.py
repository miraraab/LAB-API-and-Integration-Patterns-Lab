"""Scheduled runner for automatic news reports."""

import argparse
import logging
import time
from typing import List

from config import Config
from email_reporter import send_email_report
from summarizer import NewsSummarizer

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_report_job(
    category: str = None,
    article_count: int = None,
    send_email: bool = None,
) -> List[dict]:
    """Fetch, process, store, and optionally email one news report."""
    Config.validate()

    category = category or Config.SCHEDULE_CATEGORY
    article_count = article_count or Config.SCHEDULE_ARTICLE_COUNT
    send_email = Config.SEND_EMAIL_REPORT if send_email is None else send_email

    summarizer = NewsSummarizer()
    articles = summarizer.fetch_top_headlines(
        category=category,
        country="us",
        max_articles=article_count,
    )
    results = summarizer.process_articles(articles)
    summarizer.generate_report(results)

    if send_email and results:
        send_email_report(results)
        logger.info("Email report sent")

    return results


def run_forever(interval_minutes: int):
    """Run reports repeatedly with a fixed interval."""
    while True:
        logger.info("Starting scheduled report job")
        run_report_job()
        logger.info("Sleeping for %s minutes", interval_minutes)
        time.sleep(interval_minutes * 60)


def main():
    """Run the scheduler from the command line."""
    parser = argparse.ArgumentParser(description="Run scheduled news summaries.")
    parser.add_argument("--once", action="store_true", help="Run one job and exit.")
    parser.add_argument("--category", default=Config.SCHEDULE_CATEGORY)
    parser.add_argument("--count", type=int, default=Config.SCHEDULE_ARTICLE_COUNT)
    parser.add_argument("--email", action="store_true", help="Send email report after processing.")
    parser.add_argument(
        "--interval-minutes",
        type=int,
        default=Config.SCHEDULE_INTERVAL_MINUTES,
        help="Minutes between scheduled jobs.",
    )
    args = parser.parse_args()

    if args.once:
        run_report_job(
            category=args.category,
            article_count=args.count,
            send_email=args.email,
        )
        return

    run_forever(args.interval_minutes)


if __name__ == "__main__":
    main()
