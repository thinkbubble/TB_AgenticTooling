
from dotenv import load_dotenv
# EVERYTHING in helper will be imported
from helper import *
#from new_helper import name_a_function
import os
from newsapi import NewsApiClient 

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY") #load api key from .env

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
        