import requests
from typing import Dict, Any

def get_wikipedia_summary(query: str) -> Dict[str, Any]:
    """
    Queries the Wikipedia API to find the most relevant article for `query`
    and returns a short text summary along with the source URL.
    """
    search_url = "https://en.wikipedia.org/w/api.php"
    headers = {
        "User-Agent": "PersonalizedNetworkingAssistant/1.0 (github.com/varun-posimsetti/personalized-networking-assistant)"
    }
    
    # 1. Search for matching articles
    search_params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "utf8": 1
    }
    
    try:
        response = requests.get(search_url, params=search_params, headers=headers, timeout=10)
        response.raise_for_status()
        search_data = response.json()
        
        search_results = search_data.get("query", {}).get("search", [])
        if not search_results:
            return {
                "topic": query,
                "summary": f"Could not find any Wikipedia articles matching '{query}'. Please try a different search term.",
                "source_url": "",
                "found": False
            }
            
        # Get the top search match
        top_match = search_results[0]
        title = top_match["title"]
        
        # 2. Fetch the text extract of the top match
        extract_params = {
            "action": "query",
            "prop": "extracts",
            "exintro": 1,
            "explaintext": 1,
            "titles": title,
            "format": "json",
            "utf8": 1
        }
        
        response = requests.get(search_url, params=extract_params, headers=headers, timeout=10)
        response.raise_for_status()
        extract_data = response.json()
        
        pages = extract_data.get("query", {}).get("pages", {})
        if not pages:
            return {
                "topic": title,
                "summary": "No page summary could be loaded.",
                "source_url": f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
                "found": False
            }
            
        page_id = list(pages.keys())[0]
        if page_id == "-1":
            return {
                "topic": title,
                "summary": "No page summary was found.",
                "source_url": f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
                "found": False
            }
            
        extract = pages[page_id].get("extract", "").strip()
        if not extract:
            extract = "The article exists, but no summary snippet was returned by the Wikipedia API."
            
        # Limit to 500 characters with ellipsis
        if len(extract) > 500:
            extract = extract[:500] + "..."
            
        source_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
        return {
            "topic": title,
            "summary": extract,
            "source_url": source_url,
            "found": True
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "topic": query,
            "summary": f"Network error connecting to Wikipedia API: {str(e)}",
            "source_url": "",
            "found": False
        }
    except Exception as e:
        return {
            "topic": query,
            "summary": f"Unexpected error during Wikipedia lookup: {str(e)}",
            "source_url": "",
            "found": False
        }
