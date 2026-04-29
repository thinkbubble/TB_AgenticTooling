
from dotenv import load_dotenv
# EVERYTHING in helper will be imported
#from helper import *
#from new_helper import name_a_function
import os
import requests
from newsapi import NewsApiClient 

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

NEWS_API_KEY = os.getenv("NEWS_API_KEY") #load api key from .env
KLOE_API_KEY = os.getenv("KLOE_API_KEY") #load api key from .env

KLOE_BASE_URL = "https://kloeai.com/v1/generate"


# YOUR CUSTOM WORK WILL GO HERE
# Naming convention should be robust
# Follow coding_guidelines.pdf on Sharepoint
# Follow documentation_guidelines.pdf on Sharepoint

def fetch_top_headlines(country=None, category=None, sources=None, page_size=10): #fetches top headlines filteres by country, category, or sources
    newsapi = NewsApiClient(api_key=NEWS_API_KEY) #create client using api key from .env
    response = newsapi.get_top_headlines( #calls the newsapi top headlines endpoint
        country=country, #filter by country code
        category=category, #filter by category 
        sources=sources, #filter by source, cannot be used with country or category
        page_size=page_size #number of articles to return default is 10
    )
    return response.get("articles", []) #returns list of articles, empty list if none found


def fetch_everything(q, from_date=None, to_date=None, language="en", sort_by="publishedAt"): #search articles by keyword with optional date range, language, and sort order
    newsapi = NewsApiClient(api_key=NEWS_API_KEY) #create client using api key from .env
    response = newsapi.get_everything( #calls newsapi everything endpoint for broader search
        q=q, #keyword or phrase to search
        from_param=from_date, #start date for results
        to=to_date, #end date for results
        language=language, #langauge code articles, default is english
        sort_by=sort_by #sort by relevancy, popularity, etc.
    )
    return response.get("articles", []) #returns list of articles, empty list if none found


def fetch_sources(category=None, language="en", country=None): #get avilable news source filtered by category, country, or langauge
    newsapi = NewsApiClient(api_key=NEWS_API_KEY) #create client using api key from .env
    response = newsapi.get_sources( #call the newsapi sources endpoint
        category=category, #filter slurces by cateegory
        language=language, #filter sources by language, default is english
        country=country #filter sources by country code
    )
    return response.get("sources", []) #returns list of sources, empty list if none found
        

def summarize_article(article): #takes a news article dict and uses KloeAI claude to generate a 2-3 sentence summary
    title = article.get("title", "")
    content = article.get("content", "") or article.get("description", "")

    payload = {
        "goal": "llm",
        "model": "anthropic - claude-sonnet-4-5",
        "prompt": f"summarize the following news article in 2-3 sentences:\n\nTitle: {title}\n\nContent: {content}"
    }

    headers = {
    "X-API-Key": os.getenv("KLOE_API_KEY"),
    "Content-Type": "application/json"
    }
    
    response = requests.post(KLOE_BASE_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json() # returns summary response from KloeAI


def build_video_prompt(summary, duration=15, quality="480p"): # takes a summary and returns a tiktok/reel style video prompt dict
    payload = {
        "goal":  "llm",
        "model": "anthropic - claude-sonnet-4-5",
        "prompt": f"Turn this news summary into a short, enegaging TikTok/Reel style video script prompt:\n\n{summary}\n\nKeep it punchy and under {duration} seconds."
    }

    headers = {
    "X-API-Key": os.getenv("KLOE_API_KEY"),
    "Content-Type": "application/json"
    }

    response = requests.post(KLOE_BASE_URL, headers=headers, json=payload)
    response.raise_for_status()
    result = response.json()

    return {
        "prompt": result,
        "duration": duration,
        "quality": quality
    } # returns dict containing video prompt, duration, and quality


def generate_news_briefing_video(video_prompt_dict): # sends a video prompt dict to KloeAI grok and returns the generated video response
    payload = {
        "goal": "video",
        "model": "grok - grok-imagine-video",
        "prompt": video_prompt_dict.get("prompt", ""),
        "quality": video_prompt_dict.get("quality", "480p"),
        "duration": video_prompt_dict.get("duration", 16)
    }

    headers = {
    "X-API-Key": os.getenv("KLOE_API_KEY"),
    "Content-Type": "application/json"
    }
    response = requests.post(KLOE_BASE_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json() # returns video generation response from KloeAI


def text_to_speech(summary, voice="alloy", language="en"): # takes an article summary and converts it to audio using KloeAI gpt
    payload = {
        "goal": "tts",
        "model": "openai - gpt-4o-mini-tts",
        "text": summary,
        "language": language    
    }

    payload["voice"] = voice
    headers = {
    "X-API-Key": os.getenv("KLOE_API_KEY"),
    "Content-Type": "application/json"
    }
    response = requests.post(KLOE_BASE_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json() # returns audio response from KloeAI