"""Unit tests for the news summarizer application."""

from unittest.mock import Mock, patch

import pytest

from llm_providers import CostTracker, LLMProviders, count_tokens
from news_api import NewsAPIClient
from summarizer import NewsSummarizer


class TestCostTracker:
    """Test cost tracking functionality."""

    def test_track_request(self):
        """Test tracking a single request."""
        tracker = CostTracker()
        cost = tracker.track_request("openai", "gpt-4o-mini", 100, 500)

        assert cost > 0
        assert tracker.total_cost == cost
        assert len(tracker.requests) == 1

    def test_get_summary(self):
        """Test cost summary generation."""
        tracker = CostTracker()
        tracker.track_request("openai", "gpt-4o-mini", 100, 200)
        tracker.track_request("anthropic", "claude-3-5-sonnet-20241022", 150, 300)

        summary = tracker.get_summary()

        assert summary["total_requests"] == 2
        assert summary["total_cost"] > 0
        assert summary["total_input_tokens"] == 250
        assert summary["total_output_tokens"] == 500

    def test_budget_check(self):
        """Test budget checking."""
        tracker = CostTracker()
        tracker.track_request("openai", "gpt-4o-mini", 100, 100)
        tracker.check_budget(10.00)

        tracker.total_cost = 15.00
        with pytest.raises(RuntimeError, match="budget"):
            tracker.check_budget(10.00)


class TestTokenCounting:
    """Test token counting."""

    def test_count_tokens(self):
        """Test token counting returns a positive integer."""
        count = count_tokens("Hello, how are you?")
        assert count > 0


class TestNewsAPIClient:
    """Test cases for NewsAPIClient."""

    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        client = NewsAPIClient(api_key="test_key")
        assert client.api_key == "test_key"

    @patch("news_api.requests.get")
    def test_get_top_headlines_success(self, mock_get):
        """Test successful headline fetching and normalization."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [
                {
                    "title": "Test Article",
                    "description": "Test Description",
                    "content": "Test Content",
                    "url": "https://example.com",
                    "source": {"name": "Test Source"},
                    "publishedAt": "2026-01-19",
                }
            ],
        }
        mock_get.return_value = mock_response

        client = NewsAPIClient(api_key="test_key")
        articles = client.get_top_headlines(page_size=1)

        assert len(articles) == 1
        assert articles[0]["title"] == "Test Article"
        assert articles[0]["source"] == "Test Source"
        assert articles[0]["published_at"] == "2026-01-19"

    @patch("news_api.requests.get")
    def test_get_top_headlines_error(self, mock_get):
        """Test headline fetching with API error."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "error",
            "message": "API Error",
        }
        mock_get.return_value = mock_response

        client = NewsAPIClient(api_key="test_key")
        assert client.get_top_headlines() == []


class TestLLMProviders:
    """Test LLM provider behavior without real API calls."""

    def test_ask_with_fallback_uses_primary(self):
        """Test fallback helper returns primary response when it succeeds."""
        providers = LLMProviders(openai_client=Mock(), anthropic_client=Mock())
        providers.ask_openai = Mock(return_value="OpenAI response")
        providers.ask_anthropic = Mock(return_value="Anthropic response")

        result = providers.ask_with_fallback("Test prompt", primary="openai")

        assert result == {"provider": "openai", "response": "OpenAI response"}
        providers.ask_anthropic.assert_not_called()

    def test_ask_with_fallback_uses_secondary(self):
        """Test fallback helper uses secondary provider on primary failure."""
        providers = LLMProviders(openai_client=Mock(), anthropic_client=Mock())
        providers.ask_openai = Mock(side_effect=RuntimeError("OpenAI down"))
        providers.ask_anthropic = Mock(return_value="Anthropic response")

        result = providers.ask_with_fallback("Test prompt", primary="openai")

        assert result == {"provider": "anthropic", "response": "Anthropic response"}


class TestNewsSummarizer:
    """Test cases for NewsSummarizer."""

    @patch("summarizer.LLMProviders")
    @patch("summarizer.NewsAPIClient")
    def test_initialization(self, mock_news_client, mock_llm_providers):
        """Test NewsSummarizer initialization."""
        summarizer = NewsSummarizer()
        assert summarizer.news_client is not None
        assert summarizer.llm_providers is not None

    @patch("summarizer.LLMProviders")
    @patch("summarizer.NewsAPIClient")
    def test_summarize_article(self, mock_news_client, mock_llm_providers):
        """Test article summarization and sentiment analysis."""
        mock_llm = Mock()
        mock_llm.ask_with_fallback.return_value = {
            "provider": "openai",
            "response": "Test summary",
        }
        mock_llm.ask_anthropic.return_value = "Neutral sentiment"
        mock_llm_providers.return_value = mock_llm

        summarizer = NewsSummarizer()
        article = {
            "title": "Test Article",
            "description": "Test description",
            "content": "Test content",
            "url": "https://example.com",
            "source": "Test Source",
            "published_at": "2026-01-19",
        }

        result = summarizer.summarize_article(article)

        assert result["title"] == "Test Article"
        assert result["summary"] == "Test summary"
        assert result["summary_provider"] == "openai"
        assert result["sentiment"] == "Neutral sentiment"
        assert result["sentiment_provider"] == "anthropic"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
