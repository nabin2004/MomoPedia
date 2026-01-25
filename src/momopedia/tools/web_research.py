from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools import tool

@tool
def search_momo_facts(query: str):
    """
    Search the web for authentic momo recipes, regional variations, 
    cultural history, and specific restaurant names for citations.
    """
    search = TavilySearchResults(max_results=3) # limits results to 3 
    return search.run(query)