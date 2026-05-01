"""Simple Flask web UI for the news summarizer."""

from flask import Flask, render_template_string, request

from analytics import analyze_results
from config import Config
from database import ArticleStore
from summarizer import NewsSummarizer

app = Flask(__name__)


PAGE_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>News Summarizer</title>
  <style>
    :root {
      color-scheme: light;
      font-family: Arial, sans-serif;
      --border: #d8dee4;
      --ink: #1f2937;
      --muted: #64748b;
      --accent: #0f766e;
      --bg: #f8fafc;
      --panel: #ffffff;
    }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
    }
    main {
      max-width: 1120px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }
    h1 {
      margin: 0 0 20px;
      font-size: 32px;
    }
    form {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: end;
      padding: 16px;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
    }
    label {
      display: grid;
      gap: 6px;
      font-size: 14px;
      color: var(--muted);
    }
    input, select, button {
      min-height: 40px;
      padding: 8px 10px;
      border-radius: 6px;
      border: 1px solid var(--border);
      font: inherit;
    }
    button {
      background: var(--accent);
      color: white;
      border-color: var(--accent);
      cursor: pointer;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 16px;
      margin-top: 20px;
    }
    .article, .analytics {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
    }
    .meta {
      color: var(--muted);
      font-size: 14px;
    }
    .badge {
      display: inline-block;
      padding: 3px 7px;
      border-radius: 999px;
      background: #ccfbf1;
      color: #115e59;
      font-size: 12px;
      margin-right: 6px;
    }
    a {
      color: var(--accent);
      overflow-wrap: anywhere;
    }
  </style>
</head>
<body>
  <main>
    <h1>News Summarizer</h1>
    <form method="post">
      <label>
        Category
        <select name="category">
          {% for option in categories %}
            <option value="{{ option }}" {% if option == category %}selected{% endif %}>{{ option }}</option>
          {% endfor %}
        </select>
      </label>
      <label>
        Articles
        <input name="count" type="number" min="1" max="10" value="{{ count }}">
      </label>
      <button type="submit">Run</button>
    </form>

    {% if error %}
      <p>{{ error }}</p>
    {% endif %}

    {% if results %}
      <section class="analytics">
        <h2>Analytics</h2>
        <p class="meta">Stored articles: {{ stored_count }}</p>
        <p>Total: {{ analytics.total_articles }}</p>
        <p>Cache hits: {{ analytics.cache_hits }} | Cache misses: {{ analytics.cache_misses }}</p>
        <p>Sentiment: {{ analytics.sentiment_counts }}</p>
        <p>Top keywords:
          {% for item in analytics.top_keywords %}
            <span class="badge">{{ item.keyword }} {{ item.count }}</span>
          {% endfor %}
        </p>
      </section>

      <section class="grid">
        {% for result in results %}
          <article class="article">
            <h2>{{ result.title }}</h2>
            <p class="meta">{{ result.source }} | {{ result.published_at }}</p>
            <p>
              <span class="badge">summary: {{ result.summary_provider }}</span>
              <span class="badge">sentiment: {{ result.sentiment_provider }}</span>
              <span class="badge">cache: {{ "hit" if result.cache_hit else "miss" }}</span>
            </p>
            <h3>Summary</h3>
            <p>{{ result.summary }}</p>
            <h3>Sentiment</h3>
            <p>{{ result.sentiment }}</p>
            <p><a href="{{ result.url }}" target="_blank" rel="noreferrer">Open article</a></p>
          </article>
        {% endfor %}
      </section>
    {% endif %}
  </main>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    """Render the web UI and optionally process articles."""
    category = request.form.get("category", "technology")
    count = int(request.form.get("count", "3"))
    count = max(1, min(10, count))
    results = []
    error = None

    if request.method == "POST":
        try:
            Config.validate()
            summarizer = NewsSummarizer()
            articles = summarizer.fetch_top_headlines(
                category=category,
                country="us",
                max_articles=count,
            )
            results = summarizer.process_articles(articles)
            if not results:
                error = "No articles were processed. Try another category."
        except Exception as exc:
            error = str(exc)

    store = ArticleStore()
    analytics = analyze_results(results)
    return render_template_string(
        PAGE_TEMPLATE,
        analytics=analytics,
        categories=["technology", "business", "health", "general", "science", "sports"],
        category=category,
        count=count,
        error=error,
        results=results,
        stored_count=store.count(),
    )


if __name__ == "__main__":
    app.run(debug=Config.ENVIRONMENT == "development")
