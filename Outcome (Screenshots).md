I decided for a md file instead of screenshots 

1. Microsoft's Internal Initiative to Fix Windows 11: Don't Rush Features Out the Door - TechPowerUp
   Source: Google News | Published: 2026-04-30T01:27:01Z
   URL: https://news.google.com/rss/articles/CBMitgFBVV95cUxPRVpNYXpxbWp6Umt0XzZubFpuX3VlWVNMaHd2NmxvVFRKR01jRXlTOTVUelpZaTQzVUcxcmROM3BDNHVYYTYtVjN4dkF6ckhabFdkZUVEQ09ZNEVZR2lQenhfZ1ZvMzN5bW50cHc4akxWN01wZEhyaUFmbzA0ZW1hZmt6em5vTTNwU0lhbFRseF9rcTZBRkY4OXVVazFTaTlyd0hHcVVoX0x0SDg2N2kxTHZKTTZ2d9IBuwFBVV95cUxNUmR2cklReldRN2tEZmJ2aUlzNEo2TkZKVmhSLTV2LVExcUlMNENVTWpZZW1YY0diZXBFbzBKTjQ1VHFDcDJ5aUw0dDV4QnV4WkxwNDV4Rm13akgzazV6d19WVVUtNk5sOTlpNWFUUy0tRjB3Y2ZTMUpxYUpEQTBhR09LR3N6Tm9weFBOVjBMaGRkWG1EUkNIMzEtRFpibU1UR0xNcmxqaDAwYzRPWGZ3M1RMVFRYaHRMQjJr?oc=5
   Summary provider: openai
   Sentiment provider: openai

   SUMMARY:
   Microsoft is implementing an internal initiative aimed at improving Windows 11 by emphasizing the importance of thorough testing and quality assurance before releasing new features. The company is encouraging its teams to avoid rushing updates, focusing instead on delivering a more stable and reliable operating system. This approach is part of Microsoft's broader strategy to enhance user experience and address previous criticisms regarding feature rollouts.

   SENTIMENT:
   - Overall sentiment: Positive  
- Confidence: 85%  
- Key emotional tone: Optimistic

   ----------------------------------------------------------------------------

2. Super Mario Galaxy 2 1.4.0 update out now, patch notes – includes new story in story book - Nintendo Everything
   Source: Google News | Published: 2026-04-30T01:22:43Z
   URL: https://news.google.com/rss/articles/CBMiugFBVV95cUxQVjk1RG1DcnRQZzNzNnRFNW04U0o3VjRQczliU2hnbk9KQkxJN3FzZks0ai1ZZUxSSjZ0bFJmcnN6MGszYlBOdnZRMWtoT1RHaEpVYmNPTG5fR3FqT3pyUndLVlVLZTlUV0Rva1pJMHhGY2lEUTlHcWJBYjRoQTlmTUo3M21CLWNkVnUySVlIeFlVQnZKNll0aGlkM3FMTWlycEMyVUJTenFBZnVBMWJ5X1A0WUhhcGRqQkE?oc=5
   Summary provider: openai
   Sentiment provider: openai

   SUMMARY:
   The latest update for Super Mario Galaxy 2, version 1.4.0, has been released, introducing a new story feature in the game's storybook. This update enhances the overall gameplay experience by adding fresh content for players to enjoy. Fans of the game can now explore this new narrative element alongside the classic gameplay.

   SENTIMENT:
   - Overall sentiment: Positive  
- Confidence: 90%  
- Key emotional tone: Excitement and enthusiasm

   ----------------------------------------------------------------------------

3. How Apple (AAPL) Plans to Turn the iPhone Camera into an AI Tool - TipRanks
   Source: Google News | Published: 2026-04-30T01:22:43Z
   URL: https://news.google.com/rss/articles/CBMilwFBVV95cUxNaVlPeTVjZzh6NERWUU1Ca1ZDRGl4b25hUzNxb1Vsa2N0RU82WF83MlhiU3pkRExGM3k4VVdweDFrVmljaFBURGJYbkdEYzc0Y0x3Z2VvMXMxaGxLUWpUU29na2lQNERyenI3bWhkSnVTaWx3MkF2eGw0UWxGVWdSbU5HTmRNWGREY2ZvNTB3MW4wem1sTFdV?oc=5
   Summary provider: openai
   Sentiment provider: openai

   SUMMARY:
   Apple plans to enhance the iPhone camera by integrating advanced AI capabilities, transforming it into a powerful tool for various applications. This initiative aims to improve image processing, enable new features, and provide users with innovative ways to interact with their photos and videos. The move reflects Apple's ongoing commitment to leveraging artificial intelligence to enhance user experience across its devices.

   SENTIMENT:
   - Overall sentiment: Positive  
- Confidence: 85%  
- Key emotional tone: Optimistic

   ----------------------------------------------------------------------------

================================================================================
COST SUMMARY
================================================================================
Total requests: 6
Total cost: $0.0002
Total tokens: 713
  Input: 446
  Output: 267
Average cost per request: $0.000038
================================================================================




(base) Air-von-Mira:news-summarizer miraraab$ python -m pytest test_summarizer.py -v
=================================== test session starts ===================================
platform darwin -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0 -- /opt/anaconda3/bin/python

cachedir: .pytest_cache
rootdir: /Users/miraraab/Desktop/Ironhack_Labs/LAB I API and Integration Patterns/news-summarizer
plugins: anyio-4.10.0
collected 11 items                                                                        

test_summarizer.py::TestCostTracker::test_track_request PASSED                      [  9%]
test_summarizer.py::TestCostTracker::test_get_summary PASSED                        [ 18%]
test_summarizer.py::TestCostTracker::test_budget_check PASSED                       [ 27%]
test_summarizer.py::TestTokenCounting::test_count_tokens PASSED                     [ 36%]
test_summarizer.py::TestNewsAPIClient::test_init_with_api_key PASSED                [ 45%]
test_summarizer.py::TestNewsAPIClient::test_get_top_headlines_success PASSED        [ 54%]
test_summarizer.py::TestNewsAPIClient::test_get_top_headlines_error PASSED          [ 63%]
test_summarizer.py::TestLLMProviders::test_ask_with_fallback_uses_primary PASSED    [ 72%]
test_summarizer.py::TestLLMProviders::test_ask_with_fallback_uses_secondary PASSED  [ 81%]
test_summarizer.py::TestNewsSummarizer::test_initialization PASSED                  [ 90%]
test_summarizer.py::TestNewsSummarizer::test_summarize_article PASSED               [100%]

=================================== 11 passed in 0.97s ====================================
(base) Air-von-Mira:news-summarizer miraraab$ 
(base) Air-von-Mira:news-summarizer miraraab$ 