
# This is where you will write code that interacts with 
# your platform's functions in order to test it.
from dotenv import load_dotenv
from helper import *
import os
from project_functions import fetch_top_headlines, fetch_everything, fetch_sources

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
    results = fetch_everything(q="stocks", from_date="2026-03-15", to_date="2026-04-02")
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

if __name__ == "__main__":
    test_fetch_top_headlines_default()
    test_fetch_top_headlines_with_filters()
    test_fetch_everything_keyword()
    test_fetch_everything_with_dates()
    test_fetch_sources_default()
    test_fetch_sources_with_filters()



