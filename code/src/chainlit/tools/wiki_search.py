from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, List, Optional
import wikipedia

class WikipediaSearchInput(BaseModel):
    query: str = Field(..., description="The search query to look up on Wikipedia")
    max_results: Optional[int] = Field(3, description="Maximum number of results to return")

class WikipediaSearchTool(BaseTool):
    name:str = "wikipedia_search"
    description:str = "Search for information on Wikipedia. Useful for finding factual and historical information on topics, events, people, places, and concepts."
    args_schema: Type[BaseModel] = WikipediaSearchInput
    
    def _run(self, query: str, max_results: int = 3) -> str:
        """Search Wikipedia for the given query and return summaries of relevant articles."""
        try:
            # Set language to English (can be changed if needed)
            wikipedia.set_lang("en")
            
            # Search for the query
            search_results = wikipedia.search(query, results=max_results)
            
            if not search_results:
                return f"No Wikipedia articles found for '{query}'."
            
            # Compile results from each article
            results = []
            for title in search_results:
                try:
                    # Get a summary of the page
                    page = wikipedia.page(title, auto_suggest=False)
                    summary = wikipedia.summary(title, sentences=3, auto_suggest=False)
                    
                    results.append(
                        f"Title: {page.title}\n"
                        f"URL: {page.url}\n"
                        f"Summary: {summary}\n"
                    )
                except (wikipedia.exceptions.DisambiguationError, 
                        wikipedia.exceptions.PageError, 
                        wikipedia.exceptions.WikipediaException) as e:
                    # Skip problematic articles but continue with others
                    continue
            
            if not results:
                return f"Found Wikipedia articles for '{query}', but couldn't retrieve their content."
            
            return f"Wikipedia search results for '{query}':\n\n" + "\n\n".join(results)
            
        except Exception as e:
            return f"Error performing Wikipedia search: {str(e)}"
    
    async def _arun(self, query: str, max_results: int = 3) -> str:
        """Async implementation of Wikipedia search."""
        return self._run(query, max_results)