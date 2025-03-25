# Description: A tool that searches for financial information on approved financial websites only.
from langchain.tools import BaseTool
from duckduckgo_search import DDGS
from pydantic import BaseModel, Field, PrivateAttr
from typing import List, Optional, Type

class WebSearchInput(BaseModel):
    query: str = Field(..., description="The search query to look up")

class FinanceWebSearchTool(BaseTool):
    name: str = "finance_web_search"
    description: str = "Search for financial information on approved financial websites only."
    args_schema: Type[BaseModel] = WebSearchInput
    _allowed_domains: List[str] = PrivateAttr()
    def __init__(self):
        super().__init__()
        self._allowed_domains = [
            "bloomberg.com",
            "cnbc.com",
            "reuters.com",
            "wsj.com",
            "ft.com",
            "investopedia.com",
            "morningstar.com",
            "marketwatch.com",
            "finance.yahoo.com",
            "fool.com"
        ]
    
    def _run(self, query: str) -> str:
        """Search for information on approved financial websites only using DuckDuckGo Search."""
        try:
            # Create site-restricted search query
            site_restrictions = " OR ".join([f"site:{domain}" for domain in self._allowed_domains])
            search_query = f"{query} ({site_restrictions})"
            print(search_query)
            
            # Initialize DuckDuckGo search
            ddgs = DDGS()
            
            # Perform the search
            results = list(ddgs.text(search_query, max_results=5))
            
            if not results:
                return f"No financial information found for '{query}' from trusted sources."
            
            # Filter results to ensure they're from allowed domains
            filtered_results = []
            for result in results:
                # Check if the result is from one of our allowed domains
                if any(domain in result.get('href', '') for domain in self._allowed_domains):
                    filtered_results.append(result)
            
            if not filtered_results:
                return f"No financial information found for '{query}' from trusted sources."
            
            # Format results
            formatted_results = []
            for result in filtered_results:
                title = result.get('title', 'No title')
                link = result.get('href', 'No link')
                snippet = result.get('body', 'No description available')
                
                formatted_results.append(
                    f"Title: {title}\n"
                    f"URL: {link}\n"
                    f"Summary: {snippet}\n"
                )
            
            return f"Financial search results for '{query}':\n\n" + "\n\n".join(formatted_results)
            
        except Exception as e:
            return f"Error performing web search: {str(e)}"