import os
from typing import List, Dict
from tavily import TavilyClient # type: ignore
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Tavily
tavily_api_key = os.getenv("TAVILY_API_KEY")
if not tavily_api_key:
    raise ValueError("Missing TAVILY_API_KEY in .env file")

tavily = TavilyClient(api_key=tavily_api_key)

def get_market_news(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Searches for the latest market news.
    Returns a list of dictionaries with 'title', 'url', and 'content'.
    """
    try:
        print(f"--- FETCHING NEWS FOR: {query} ---")
        
        # We use "finance" as the topic to get better market-relevant results
        response = tavily.search(
            query=query, 
            topic="finance", 
            max_results=max_results, 
            include_answer=False  # We want raw articles, not a summary
        )
        
        news_items = []
        seen_urls = set()

        for result in response.get('results', []):
            url = result['url']
            
            # Deduplicate articles
            if url in seen_urls:
                continue
            seen_urls.add(url)
            
            # Clean up the content (limit length to avoid token overflow)
            content = result.get('content', '')[:1000] 
            
            news_items.append({
                "title": result['title'],
                "url": url,
                "content": content,
                "score": result.get('score', 0) # Relevance score
            })
            
        return news_items
        
    except Exception as e:
        return [{"error": f"News search failed: {str(e)}"}]