from typing import Dict, Any
from duckduckgo_search import DDGS



def web_search(query: str, max_results: int = 3) -> Dict[str, Any]:
    try:
        with DDGS() as ddgs:
            for result in ddgs.text(query, max_results=max_results):
                result['href'] = result['href'].replace('+', "%20")
                body = [str(result) for result in response]
                response = "\nNext Result: ".join(body)

        return {
            "success": True,
            "answer": response,
            "error": None
        }

    except Exception as e:
        error_msg = f"Error in web_search: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "answer": None,
            "error": error_msg
        }


web_search_tool_schema = {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for information about colleges, rankings, admissions, and educational institutions to help students find the best college options",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find college-related information. Can include college names, ranking criteria, admission requirements, course offerings, location preferences, or comparison terms",
                        "examples": [
                            "IIT vs NIT placement statistics 2024",
                            "IIT Bombay Placement Stats",
                            "IIT Bombay NIRF Ranking",
                            "IIT Indore Coding Culture Reddit",
                            "IIT Bombay Hostel Life Reddit"
                        ]
                    }
                },
                "required": ["query"]
            }
        }
    }
