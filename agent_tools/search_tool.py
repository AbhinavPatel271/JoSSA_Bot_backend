from typing import Dict, Any
from duckduckgo_search import DDGS

def web_search(query: str, max_results: int = 3) -> Dict[str, Any]:
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "body": r.get("body", "").strip(),
                    "source": r.get("href", "").strip()
                })

        return {
            "success": True,
            "answer": results,
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
    "name": "web_search",
    "description" : "Search the web for up-to-date information about colleges, including placements, rankings, admissions, courses, and comparisons to help students make informed decisions."
,
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "The search query to find college-related information. "
                    "Can include college names, placement stats, rankings, admission requirements, "
                    "course offerings, infrastructure details, or comparisons."
                ),
                "examples": [
                    "What are the best colleges for computer science engineering India",
                    "Affordable colleges for mechanical engineering",
                    "IIT vs NIT placement statistics 2024",
                    "IIT Delhi Placement Stats",
                    "How is the campus life at IIT Hyderabad",
                    "How is NIT Surathkal as compared to IIT Indore",
                    "What the placement trends in IITs",
                    "IIT Roorkee vs IIT BHU CSE"
                ]
            }
        },
        "required": ["query"]
    },
    "function": web_search
}

print(web_search("What are the placement stats at IIT Patna ?"))