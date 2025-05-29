from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json
import os
from dotenv import load_dotenv, find_dotenv

def find_colleges_in_rank_range(rank, category, gender):
    try:
        load_dotenv(find_dotenv())

        # Setup and connection to the server
        connection_string = os.environ.get("CONNECTION_STRING")
        client = MongoClient(connection_string, server_api=ServerApi('1'))
        ORCR = client.get_database('ORCR')
        collection = ORCR.ORCR
        rank = int(rank)

        upper_bound = rank + 600
        lower_bound = rank - 200
        query = {
            "$and": [
                {"Closing Rank": {"$lte": upper_bound}},
                {"Closing Rank": {"$gte": lower_bound}},
                {"Seat Type": category},
                {"Gender": gender}
            ]
        }
        colleges = list(collection.find(query, {"_id": 0}))
        return {
            "success": True,
            "answer" : json.dumps(colleges),
            "error" : None
        }

    except Exception as e:
        error_msg = f"Error in web_search: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "answer": None,
            "error": error_msg
        }

college_rank_range_schema = {
  "type": "function",
  "function": {
    "name": "find_colleges_in_rank_range",
    "description": "Find colleges within a rank range based on closing rank, filtered by category and gender",
    "parameters": {
      "type": "object",
      "properties": {
        "rank": {
          "type": "string",
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
}
