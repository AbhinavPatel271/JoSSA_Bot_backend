from typing import Dict, Any
from duckduckgo_search import DDGS



def web_search(query: str, max_results: int = 5) -> Dict[str, Any]:
    try:
        response =''
        sources = ""
        with DDGS() as ddgs:
            for i , result in enumerate(ddgs.text(query, max_results=max_results)):
                if "%20" not in result['href']:
                    result['href'] = result['href'].replace('+', "%20")
                    # sources += f"Source : {result['href']} \n"
                    sources += f'<a href={result["href"]} target="_blank" > {result["href"]} </a> \n'
                body = str(result)
                response = response + body + "\n"

        return {
            "success": True,
            "answer": response,
            "sources": sources,
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
            "description": "Search the web for FOCUSED, SINGLE-TOPIC information about colleges. CRITICAL: Use multiple separate calls for complex queries instead of cramming multiple topics into one search. Break down comparisons into individual searches for better results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "A FOCUSED search query for ONE specific aspect of college information. AVOID complex multi-topic queries. Use separate calls for each college, each topic, each comparison aspect.",
                        "examples": [
                            "IIT Bombay NIRF ranking 2024",
                            "IIT Delhi campus life student experience",
                            "IIT Madras hostel facilities",
                            "IIT Kanpur computer science curriculum",
                            "IIT Guwahati placement statistics",
                            "IIT Roorkee branch change rules",
                            "IIT Hyderabad research opportunities",
                            "IIT Indore coding culture programming clubs"
                        ],
                        "anti_examples": [
                            "IIT Bombay vs IIT Delhi campus life facilities ranking cutoffs",
                            "Compare all IITs placement statistics and rankings",
                            "IIT Bombay Delhi Madras campus life facilities hostels"
                        ]
                    }
                },
                "required": ["query"]
            }
        }
    }