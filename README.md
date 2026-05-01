# News Summarizer

Multi-provider news summarizer for the API and Integration Patterns lab. The app fetches articles from NewsAPI, summarizes them with OpenAI, analyzes sentiment with Anthropic, falls back between providers when needed, tracks estimated API cost, caches processed articles, stores results in SQLite, provides analytics, can run on a schedule, can email reports, and includes a small Flask web UI.

## Setup

Create a `.env` file from `.env.example` and add real API keys:

```bash
cp .env.example .env
```

Install dependencies in your Conda environment:

```bash
pip install -r requirements.txt
```

Validate configuration:

```bash
python config.py
```

## Run

Start the interactive application:

```bash
python main.py
```

Start the web UI:

```bash
python web_app.py
```

Run one scheduled job:

```bash
python scheduler.py --once --category technology --count 3
```

Run repeated scheduled jobs using `.env` defaults:

```bash
python scheduler.py
```

Run tests:

```bash
python -m pytest test_summarizer.py -v
```

## Example Output

```text
NEWS SUMMARIZER - Multi-Provider Edition
Fetching 3 articles from category: technology
Processing 3 articles...

NEWS SUMMARY REPORT
1. Example article title
   Summary provider: openai
   Sentiment provider: anthropic

COST SUMMARY
Total requests: 6
Total cost: $0.0008

ADVANCED ANALYTICS
Total articles: 3
Sentiment: neutral: 2, positive: 1
Top keywords: ai (2), cloud (1)
```

## Cost Notes

Costs are estimated from token counts and model pricing in `llm_providers.py`. OpenAI `gpt-4o-mini` is used for summaries because it is fast and inexpensive. Anthropic Claude is used for sentiment analysis because the lab scenario prioritizes nuance for that task. `DAILY_BUDGET` in `.env` stops processing once the estimated budget is exceeded.

## Caching

Processed article results are stored in `.cache/articles.json`. The cache key is based on the article URL when available, with a title/date/content fallback. Cached files are ignored by Git, so local results and repeated API outputs are not committed.

## Database

Processed articles are stored in SQLite at `.data/news_summaries.db`. The database is ignored by Git because it is a local runtime artifact, but it lets the app keep a durable local history of processed summaries.

## Email Reports

Email reports use SMTP settings from `.env`. Set `SEND_EMAIL_REPORT=true` for scheduled jobs or call `send_email_report()` from `email_reporter.py`. Use an app password or API-specific SMTP credential rather than your normal mailbox password.

## File Map

- `analytics.py`: aggregate sentiment, source, cache, provider, and keyword analytics.
- `cache.py`: JSON cache for processed article results.
- `config.py`: environment configuration and validation.
- `database.py`: SQLite persistence for processed article results.
- `email_reporter.py`: plain-text email report generation and SMTP sending.
- `news_api.py`: NewsAPI client with simple rate limiting and article normalization.
- `llm_providers.py`: OpenAI and Anthropic clients, fallback logic, token counting, and cost tracking.
- `scheduler.py`: automatic report runner.
- `summarizer.py`: article processing pipeline and report generation.
- `main.py`: interactive command-line entry point.
- `web_app.py`: Flask web interface.
- `test_summarizer.py`: unit tests with mocked API calls.
- `requirements.txt`: Python dependencies.
- `.env.example`: safe environment variable template.
