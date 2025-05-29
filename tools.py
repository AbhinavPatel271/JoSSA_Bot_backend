from dotenv import load_dotenv, find_dotenv
import os
from pprint import pprint
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
import json
from duckduckgo_search import DDGS
from agent_tools.josaa_rag_tool import rag_tool_schema, rag_pipeline

load_dotenv(find_dotenv())

# Setup and connection to the server
connection_string = os.environ.get("CONNECTION_STRING")
client = MongoClient(connection_string, server_api=ServerApi('1'))
ORCR = client.get_database('ORCR')
collection = ORCR.ORCR

with open("unique_values.json", "r") as file:
    unique_values = json.load(file)

available_tools = [{
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
                            "IIT Bombay NIRF Ranking",
                            "IIT Indore Coding Culture Reddit",
                        ]
                    }
                },
                "required": ["query"]
            }
        }
    },
# {
#     "type": "function",
#     "function": {
#         "name": "find_ORCR_for_specific_colleges",
#         "description": "Search and retrieve  data for specific colleges based on various filters like college names, academic branches, seat categories, gender, and rank ranges. Useful for college admission guidance and rank analysis. If you want to query all fields for a given parameter, don't give an input for that parameter",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "college_names": {
#                     "type": ["array", "string", "null"],
#                     "items": {
#                         "type": "string",
#                         "enum": unique_values['institutes']
#                     },
#                     "description": "Name(s) of specific colleges/institutes to search for. Can be a single string or array of college names. Must match exact institute names from the database.Use only the values from the database provided, do not create your own values",
#                     "examples": [
#                         "Indian Institute  of Technology Bombay",
#                         ["Indian Institute  of Technology Delhi", "Indian Institute  of Technology Madras"],
#                         "National Institute of Technology, Tiruchirappalli"
#                     ]
#                 },
#                 "categories": {
#                     "type": ["array", "string", "null"],
#                     "items": {
#                         "type": "string",
#                         "enum": unique_values['categories']
#                     },
#                     "description": "Seat category/reservation type(s) to filter by. Can be single string or array",
#                     "examples": [
#                         "OPEN",
#                         ["OPEN", "OBC-NCL"],
#                         "SC"
#                     ]
#                 },
#                 "branches": {
#                     "type": ["array", "string", "null"],
#                     "items": {
#                         "type": "string",
#                         "enum": unique_values['branches']
#                     },
#                     "description": "Academic program/branch name(s) to filter by. Can be single string or array. Must match exact branch names from the database.",
#                     "examples": [
#                         "Computer Science and Engineering (4 Years, Bachelor of Technology)",
#                         ["Mechanical Engineering (4 Years, Bachelor of Technology)", "Electrical Engineering (4 Years, Bachelor of Technology)"],
#                         "Electronics and Communication Engineering (4 Years, Bachelor of Technology)"
#                     ]
#                 },
#                 "genders": {
#                     "type": ["array", "string", "null"],
#                     "items": {
#                         "type": "string",
#                         "enum": unique_values['genders']
#                     },
#                     "description": "Gender(s) to filter by. Can be single string or array",
#                     "examples": [
#                         "Gender-Neutral",
#                         ["Female-only (including Supernumerary)", "Gender-Neutral"],
#                         "Female-only (including Supernumerary)"
#                     ]
#                 },
#                 "closing_rank": {
#                     "type": ["integer", "null"],
#                     "description": "Target closing rank to search around. Used with offset to create a range",
#                     "examples": [1600 , 1700, 12000]
#                 },
#                 "opening_rank": {
#                     "type": ["integer", "null"],
#                     "description": "Target opening rank to search around. Used with offset to create a range",
#                     "examples": [500, 2000, 8000]
#                 },
#                 "offset": {
#                     "type": ["integer", "null"],
#                     "description": "Range offset to use with closing_rank or opening_rank. Creates a range of ±offset around the target rank",
#                     "examples": [100, 500, 1000]
#                 }
#             },
#             "required": []
#         }
#     }
# }
rag_tool_schema]


# Creating the tools which can be accessed
def find_colleges_in_rank_range(rank, category, gender):
    rank = int(rank)
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

# def find_ORCR_for_specific_colleges(college_names=None, categories=None, branches= None, genders= None, closing_rank = None, opening_rank = None, offset = None):
#     conditions = []
#     if offset:
#         offset = int(offset)
#
#     if closing_rank:
#         c_r = int(closing_rank)
#         upper_bound = c_r + offset
#         lower_bound = c_r - offset
#         conditions.append({"Closing Rank" : {"$lte" : upper_bound}})
#         conditions.append({"Closing Rank" : {"$gte" : lower_bound}})
#
#     if opening_rank:
#         o_r = int(opening_rank)
#         upper_bound = o_r + offset
#         lower_bound = o_r - offset
#         conditions.append({"Closing Rank": {"$lte": upper_bound}})
#         conditions.append({"Closing Rank": {"$gte": lower_bound}})
#
#     if genders and not isinstance(genders, list):
#         genders = [genders]
#
#     if branches and not isinstance(branches, list):
#         branches = [branches]
#
#     if categories and not isinstance(categories, list):
#         categories = [categories]
#
#     if college_names and not isinstance(college_names, list):
#         college_names = [college_names]
#
#     if genders:
#         conditions.append({"Gender": {"$in": genders}})
#
#     if branches:
#         conditions.append({"Academic Program Name": {"$in": branches}})
#
#     if categories:
#         conditions.append({"Seat Type": {"$in": categories}})
#
#     if college_names:
#         conditions.append({"Institute": {"$in": college_names}})
#
#     query = {
#         "$and": conditions
#     }
#     colleges = list(collection.find(query, {"_id": 0}))
#     return json.dumps(colleges)

def web_search(query):
    response = DDGS().text(query, max_results= 3)
    for result in response:
        result['href'] = result['href'].replace('+', "%20")
    body = [str(result) for result in response]
    response = "\nNext Result: ".join(body)
    return response

if __name__ == "__main__":
    result = DDGS().text("IIT Gandhinagar placement stats", max_results= 20)
    print(result[1])





