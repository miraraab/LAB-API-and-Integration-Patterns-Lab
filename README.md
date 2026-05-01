# News Summarizer

Multi-provider news summarizer for the API and Integration Patterns lab. The app fetches articles from NewsAPI, summarizes them with OpenAI, analyzes sentiment with Anthropic, falls back between providers when needed, and tracks estimated API cost.

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
```

## Cost Notes

Costs are estimated from token counts and model pricing in `llm_providers.py`. OpenAI `gpt-4o-mini` is used for summaries because it is fast and inexpensive. Anthropic Claude is used for sentiment analysis because the lab scenario prioritizes nuance for that task. `DAILY_BUDGET` in `.env` stops processing once the estimated budget is exceeded.

## File Map

- `config.py`: environment configuration and validation.
- `news_api.py`: NewsAPI client with simple rate limiting and article normalization.
- `llm_providers.py`: OpenAI and Anthropic clients, fallback logic, token counting, and cost tracking.
- `summarizer.py`: article processing pipeline and report generation.
- `main.py`: interactive command-line entry point.
- `test_summarizer.py`: unit tests with mocked API calls.
- `requirements.txt`: Python dependencies.
- `.env.example`: safe environment variable template.
