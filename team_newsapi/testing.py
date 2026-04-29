
# This is where you will write code that interacts with 
# your platform's functions in order to test it.
from dotenv import load_dotenv
#from helper import *
import os
from project_functions import fetch_top_headlines, fetch_everything, fetch_sources, summarize_article, build_video_prompt, generate_news_briefing_video, text_to_speech

load_dotenv()

#calls with no arguments and checks results is a non empty list of articles dictionaries, a list of article dictionaries each containing at least a title key 
def test_fetch_top_headlines_default():
    results = fetch_top_headlines()
    assert isinstance(results, list), "Expected a list"
    assert len(results) > 0, "Expected at least one article"
    assert "title" in results[0], "Expected 'title' key in article"
    print("PASS test_fetch_top_headlines_default")

#calls with country=us, category=technology, page_size=5, and validates count, a list of at most 5 articles
def test_fetch_top_headlines_with_filters():
    results = fetch_top_headlines(country="us", category="technology", page_size=5)
    assert isinstance(results, list), "Expected a list"
    assert len(results) <= 5, "Expected at most 5 articles"
    print("PASS test_fetch_top_headlines_with_filters")

#searches for AI in english and checks articles have expected fields, a list of articles each with a title and url keys
def test_fetch_everything_keyword():
    results = fetch_everything(q="AI", language="en")
    assert isinstance(results, list), "Expected a list"
    assert len(results) > 0, "Expected at least one result"
    assert "title" in results[0], "Expecyed 'title' key in article"
    assert "url" in results[0], "Expected 'url' key in article"
    print("PASS test_fetch_everything_keyword")

#passes a date range and keyword and checks results return without error, a list
def test_fetch_everything_with_dates():
    results = fetch_everything(q="stocks", from_date="2026-04-01", to_date="2026-04-20")
    assert isinstance(results, list), "Expected a list"
    print("PASS test_fetch_everything_with_dates")

#calls with no arguments and checks source objects have expected fields, a list of source dictionaries each containing id and name
def test_fetch_sources_default():
    results = fetch_sources()
    assert isinstance(results, list), "Expected a list"
    assert len(results) > 0, "Expected at least one source"
    assert "id" in results[0], "Expected 'id' key in source"
    assert "name" in results[0], "Expected 'name' key in source"
    print("PASS test_fetch_sources_default")

#filters by category=technology and country=us, checks result is a list, a filtered list of us technology sources
def test_fetch_sources_with_filters():
    results = fetch_sources(category="technology", country="us")
    assert isinstance(results, list), "Expected a list"
    print("PASS test_fetch_sources_with_filters")

#fetches a real article and checks that summarize_article returns a non-empty response from KloeAI
def test_summarize_article():
    article = {
        "title": "AI is transforming the tech industry",
        "content": "Artificial intelligence is rapidly changing how companies operate, from automating tasks to generating content. Many tech giants are investng billions intoAI research and development."
    }
    result = summarize_article(article)
    assert result is not None, "Expected a response from KloeAI"
    assert isinstance(result, dict), "Expected a dict response"
    print("Pass test_summarize_article")

#checks that build_video_prompt returns a dict with the correct keys and default values
def test_build_video_prompt_default():
    summary = "AI is transforming the tech industry by automating tasks and generating content."
    result = build_video_prompt(summary)
    assert isinstance(result, dict), "Expected a dict"
    assert "prompt" in result, "Expected 'prompt' key in result"
    assert "duration" in result, "Expected 'duration' key in result"
    assert "quality" in result, "Expected 'quality' key in result"
    assert result["duration"] == 16, "Expected default duration of 16"
    assert result["quality"] == "480p", "Expected default quality of 480p"
    print("PASS test_build_video_prompt_default")

#checks that build_video_prompt respects custom duration and quality params
def test_build_video_prompt_custom():
    summary = "AI is transforming the tech industry by automating tasks and generating content."
    result = build_video_prompt(summary, duration=32, quality="720p")
    assert result["duration"] == 32, "Expected duration of 32"
    assert result["quality"] == "720p", "Expected quality of 720p"
    print("PASS test_build_video_prompt_custom")

#checks that generate_news_briefing_video returns a non-empty response from KloeAI
def test_generate_news_briefing_video():
    video_prompt_dict = {
        "prompt": "Breaking news: AI is taking over the tech world. Are we ready?",
        "duration": 16,
        "quality": "720p"
    }
    result = generate_news_briefing_video(video_prompt_dict)
    assert result is not None, "Expected a response from KloeAI"
    assert isinstance(result, dict), "Expected a dict response"
    print("PASS test_generate_news_briefing_video")

#checks that text_to_speech returns a non-empty response using default voice alloy
def test_text_to_speech_default():
    summary = "AI is transforming the tech industry by automating tasks and generating content."
    result = text_to_speech(summary)
    assert result is not None, "Expected a response from KloeAI"
    assert isinstance(result, dict), "Expected a dict response"
    print("PASS test_text_to_speech_default")

#checks that text_to_speech works with a custom voice and language
def test_text_to_speech_custom_voice():
    summary = "AI is transforming the tech industry by automating tasks and generating content."
    result = text_to_speech(summary, voice="nova", language="en")
    assert result is not None, "Expected a response from KloeAI"
    assert isinstance(result, dict), "Expected a dict response"
    print("PASS test_text_to_speech_custom_voice")

if __name__ == "__main__":
    test_fetch_top_headlines_default()
    test_fetch_top_headlines_with_filters()
    test_fetch_everything_keyword()
    test_fetch_everything_with_dates()
    test_fetch_sources_default()
    test_fetch_sources_with_filters()
    test_summarize_article()
    test_build_video_prompt_default()
    test_build_video_prompt_custom()
    test_generate_news_briefing_video()
    test_text_to_speech_default()
    test_text_to_speech_custom_voice()



