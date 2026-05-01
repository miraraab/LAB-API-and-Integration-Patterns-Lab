"""Configuration management for the news summarizer application."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    
    # API URLs
    NEWS_API_URL = os.getenv("NEWS_API_URL", "https://newsapi.org/v2")
    
    # Environment and logging
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Model configurations
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    
    # Request parameters
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

    # Cost control
    DAILY_BUDGET = float(os.getenv("DAILY_BUDGET", "5.00"))

    # Rate limits (requests per minute)
    OPENAI_RPM = int(os.getenv("OPENAI_RPM", "500"))
    ANTHROPIC_RPM = int(os.getenv("ANTHROPIC_RPM", "50"))
    NEWS_API_RPM = int(os.getenv("NEWS_API_RPM", "100"))

    @classmethod
    def validate(cls):
        """Validate required configuration."""
        required = [
            ("OPENAI_API_KEY", cls.OPENAI_API_KEY),
            ("ANTHROPIC_API_KEY", cls.ANTHROPIC_API_KEY),
            ("NEWS_API_KEY", cls.NEWS_API_KEY),
        ]
        missing = [
            name
            for name, value in required
            if not value or value.startswith("your_") or value.startswith("your-")
        ]

        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")

        return True


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False


# Select config based on environment.
ENV = os.getenv("ENVIRONMENT", os.getenv("FLASK_ENV", "development"))
if ENV == "production":
    config = ProductionConfig()
elif ENV == "testing":
    config = TestingConfig()
else:
    config = DevelopmentConfig()


if __name__ == "__main__":
    Config.validate()
    print(f"Configuration validated for {Config.ENVIRONMENT} environment")
