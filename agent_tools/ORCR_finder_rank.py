from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json
import os
from dotenv import load_dotenv, find_dotenv

def find_colleges_in_rank_range(rank, category, gender, rank_type):
    try:
        load_dotenv(find_dotenv())

        # Setup and connection to the server
        connection_string = os.environ.get("CONNECTION_STRING")
        client = MongoClient(connection_string, server_api=ServerApi('1'))
        ORCR = client.get_database('ORCR')
        collection = ORCR.ORCR
        rank = int(rank)

        if category == "OPEN":
          upper_bound = rank + 800
          lower_bound = rank - 200
        elif category == "OBC-NCL":
          upper_bound = rank + 500
          lower_bound = rank - 125
        elif category == "SC":
          upper_bound = rank + 200
          lower_bound = rank - 50
        elif category == "ST":
          upper_bound = rank + 100
          lower_bound = rank - 25
        elif category == "EWS":
          upper_bound = rank + 80
          lower_bound = rank - 20
        query = {
            "$and": [
                {"Closing Rank": {"$lte": upper_bound}},
                {"Closing Rank": {"$gte": lower_bound}},
                {"Seat Type": category},
                {"Gender": gender},
                {"Rank Type": rank_type}
            ]
        }
        colleges = list(collection.find(query, {"_id": 0}))
        
        new_list = []
        if rank_type == "Mains":
            college_list = colleges
            for clg in college_list:
                # print(clg)
                if "Architecture" not in clg["Academic Program Name"]:
                    # continue
                    new_list.append(clg)
            colleges = new_list        

        print(f"Rank type : {rank_type} , Rank : {rank} , Category : {category} , Gender : {gender} ")
        print(f"Colleges : \n {json.dumps(colleges)} \n\n")
        return {
            "success": True,
            "answer" : json.dumps(colleges),
            "error" : None
        }


    except Exception as e:
        error_msg = f"Error in web_search: {str(e)}"
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
          "enum": ["OPEN", "EWS", "OBC-NCL", "SC", "ST"]
        },
        "gender": {
          "type": "string",
          "description": "The gender category. Male = Gender-Neutral",
          "enum": ["Female-only (including Supernumerary)", "Gender-Neutral"]
        },
        "rank_type": {
          "type": "string",
          "description": "The type of the rank which is provided, Mains or Advanced",
          "enum": ["Mains", "Advanced"]
        }
      },
      "required": ["rank", "category", "gender", "rank_type"]
    }
  }
}
