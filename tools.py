from dotenv import load_dotenv, find_dotenv
import os
from pprint import pprint
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
import json
from duckduckgo_search import DDGS

load_dotenv(find_dotenv())

# Setup and connection to the server
connection_string = os.environ.get("CONNECTION_STRING")
client = MongoClient(connection_string, server_api=ServerApi('1'))
ORCR = client.get_database('ORCR')
collection = ORCR.ORCR

available_tools = [{
  "type": "function",
  "function": {
    "name": "find_colleges_in_rank_range",
    "description": "Find colleges within a rank range based on closing rank, filtered by category and gender",
    "parameters": {
      "type": "object",
      "properties": {
        "rank": {
          "type": "integer",
          "description": "The reference rank to search around (range will be rank-200 to rank+600)"
        },
        "category": {
          "type": "string",
          "description": "The seat type/category (e.g., General, OBC, SC, ST, EWS)",
          "enum" : ["OPEN", "EWS", "OBC-NCL", "SC", "ST"]
        },
        "gender": {
          "type": "string",
          "description": "The gender category. Male = Gender-Neutral",
          "enum": ["Female", "Gender-Neutral"]
        }
      },
      "required": ["rank", "category", "gender"]
    }
  }
},
    {
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
                            "best colleges for computer science engineering India",
                            "affordable colleges mechanical engineering",
                            "IIT vs NIT placement statistics 2024",
                            "IIT Bombay Placement Stats",
                            "IIT Bombay NIRF Ranking"
                        ]
                    }
                },
                "required": ["query"]
            }
        }
    }
]


# Creating the tools which can be accessed
def find_colleges_in_rank_range(rank, category, gender):
    upper_bound = rank + 600
    lower_bound = rank - 200
    query = {
        "$and" : [
            {"Closing Rank" : {"$lte" : upper_bound}},
            {"Closing Rank" : {"$gte" : lower_bound}},
            {"Seat Type" : category},
            {"Gender" : gender}
        ]
    }
    colleges = list(collection.find(query, {"_id" : 0}))
    return json.dumps(colleges)


def web_search(query):
    response = DDGS().text(query, max_results= 5)
    response = [result.get("body") for result in response]
    response = "\nNext Result: ".join(response)
    return response

if __name__ == "__main__":
    result = DDGS().text("IIT Gandhinagar placement stats", max_results= 5)
    print(result[1])





